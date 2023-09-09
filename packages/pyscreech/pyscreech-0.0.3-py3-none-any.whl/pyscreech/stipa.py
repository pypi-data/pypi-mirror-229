import copy

import numpy as np
from typing import List
from .audio import AudioWaveform
from loguru import logger

from .filter import (
    apply_butter_sos_bandpass_filter,
    DEFAULT_BUTTER_ORDER,
    apply_lowpass_filter,
    FilterException,
    FirwinFilterParameters
)


class StipaCalculationException(Exception):
    pass


OCTAVE_BAND_CENTERS = np.array([125, 250, 500, 1000, 2000, 4000, 8000])
OCTAVE_MODULATION_FREQUENCIES = np.array(
    [[1.6, 8], [1, 5], [0.63, 3.15], [2, 10], [1.25, 6.25], [0.8, 4], [2.5, 12.5]])

MALE_WEIGHTS_ALPHA = np.array([0.085, 0.127, 0.230, 0.233, 0.309, 0.224, 0.173])
MALE_WEIGHTS_BETA = np.array([0.085, 0.078, 0.065, 0.011, 0.047, 0.095])


def get_octave_band_edges(center_frequency: float, bandwidth: str = "1 octave") -> (float, float):
    """
    Calculate the frequency limits given a center frequency and a fractional octave bandwidth

    Args:
        center_frequency (float): Center frequency of the band requested
        bandwidth (str): fractional bandwidth of an octave. Defaults to "1 octave"

    Returns:
        Tuple of floats with the lower and upper frequency limits for this band
    """
    if bandwidth == "1 octave":
        return center_frequency / np.sqrt(2), center_frequency * np.sqrt(2)
    elif bandwidth == "1/3 octave":
        return center_frequency / np.power(2, 1 / 6), center_frequency * np.power(2, 1 / 6)
    else:
        raise ValueError(f"Unrecognized bandwidth: {bandwidth}")


def calculate_modulation_depth(intensity_envelope: AudioWaveform, modulation_frequency: float) -> float:
    """
    Calculates the modulation depth given an intensity envelope and a modulation frequency

    Args:
        intensity_envelope (AudioWaveform): intensity envelope of the waveform
        modulation_frequency (float): modulation frequency

    Returns:
        Calculated modulation depth for this modulation frequency
    """

    times = copy.deepcopy(intensity_envelope.get_times())
    intensity = copy.deepcopy(intensity_envelope.timeseries)

    # use an integer number of periods in to calculate depth, so calculate the corresponding max time
    max_time_whole_number_periods = int(times[-1]*modulation_frequency)/modulation_frequency

    intensity = intensity[times <= max_time_whole_number_periods]
    times = times[times <= max_time_whole_number_periods]

    I = np.sin(2 * np.pi * modulation_frequency * times)
    Q = np.cos(2 * np.pi * modulation_frequency * times)

    return 2 * np.sqrt(np.sum(intensity * I) ** 2 + np.sum(intensity * Q) ** 2) / np.sum(intensity)


def calculate_octave_depths(waveform: AudioWaveform,
                            modulation_frequencies: List[float],
                            central_frequency: float = None,
                            butter_order: int = DEFAULT_BUTTER_ORDER,
                            firwin_filter_params: FirwinFilterParameters = None,
                            bandwidth: str = "1 octave") -> np.ndarray:
    """
    Calculate the octave modulation depths for this frequency band given a list of modulation frequencies

    Args:
        waveform (AudioWaveform): Waveform to assess
        central_frequency (float): central frequency of the band
        modulation_frequencies (List): list of modulation frequencies for which to calculate depths
        butter_order (int): order of the butter filter. Defaults to DEFAULT_BUTTER_ORDER
        firwin_filter_params (FirwinFilterParameters): low pass filter parameters
        bandwidth (str): fractional bandwidth of an octave. Defaults to "1 octave"

    Returns:
        Numpy array of modulations depths for each modulation frequency used in calculation
    """

    # Apply bandpass filter to the waveform
    frequency_range = get_octave_band_edges(central_frequency, bandwidth=bandwidth)
    try:
        filtered_output = apply_butter_sos_bandpass_filter(waveform=waveform,
                                                           frequency_range=frequency_range,
                                                           butter_order=butter_order)

    except FilterException:
        return None

    # Get the intensity envelope by squaring the filtered waveform
    filtered_output.timeseries = filtered_output.timeseries ** 2

    # Apply a low pass filter (FIR)
    if firwin_filter_params is not None:
        filtered_output = apply_lowpass_filter(filtered_output, filter_params=firwin_filter_params)

    # Calculate the depths for each modulation frequency
    depths = np.array([calculate_modulation_depth(filtered_output, mi) for mi in modulation_frequencies])

    return depths


def construct_stipa_depth_matrix(waveform: AudioWaveform,
                                 butter_order: int = DEFAULT_BUTTER_ORDER,
                                 firwin_filter_params: FirwinFilterParameters = None) -> np.ndarray:
    """
    Construct the depth matrix for each octave band

    Args:
        waveform (AudioWaveform): Waveform to process
        butter_order (int): Butterworth filter order used in octave band filter
        firwin_filter_params (FirwinFilterParameters): low pass filter parameters

    Returns:
        Matrix of modulation depths for each octave and with modulation frequency requested
    """

    m = []

    for c, mf in zip(OCTAVE_BAND_CENTERS, OCTAVE_MODULATION_FREQUENCIES):
        depths = calculate_octave_depths(waveform=waveform,
                                         modulation_frequencies=mf,
                                         central_frequency=c,
                                         butter_order=butter_order,
                                         firwin_filter_params=firwin_filter_params)

        if depths is not None:
            m.append(depths)

    m = np.asarray(m)

    # for depths > 1.0, set back to 1.0 (per IEC document)
    m[m > 1.0] = 1.0
    return m


def calculate_modulation_transfer_index(mtf: np.ndarray) -> np.ndarray:
    """
    Calculate the modulation transfer index for each octave band given the modulation transfer matrix

    Args:
        mtf (np.ndarray): 2D modulation transfer matrix, giving modulation depth ratios between the two
            waveforms for each modulation frequency (axis=1) for each octave band (axis=0)

    Returns:
        Numpy array of modulation transfer index for each octave band
    """
    # mtf is matrix of ratios...
    m = np.asarray(mtf)
    snr = 10 * np.log10(m / (1 - m))

    # if m = 1 then SNR will be NaN...but should be max so setting to 15
    snr = np.nan_to_num(snr, nan=15, posinf=15, neginf=-15)

    snr[snr > 15] = 15
    snr[snr < -15] = -15

    ti = (snr + 15) / 30
    mti = np.sum(ti, axis=1) / 2.0
    return mti


def calculate_weighted_stipa(mti: np.ndarray) -> float:
    """
    Calculate the male-weighted STIPA score for each octave band given the modulation transfer matrix.
    Per IEC document, female speech is generally considered more intelligible than male speech, so
    male speech is typically used to assess speech transmission

    Args:
        mti (np.ndarray): modulation transfer indices for each octave band

    Returns:
        Male-weighted STIPA score
    """

    # if we've cut off higher frequency bands b/c our waveform has low sampling rate,
    # then we need to set the transfer indices for those bands to zero
    mti_p = copy.deepcopy(mti)
    length_diff = len(MALE_WEIGHTS_ALPHA)-len(mti)
    if length_diff > 0:
        mti_p = np.append(mti_p, [0.0] * length_diff)

    value = np.sum(MALE_WEIGHTS_ALPHA * mti_p) - np.sum(MALE_WEIGHTS_BETA * np.sqrt(mti_p[:-1] * mti_p[1:]))
    return value


def calculate_multiple_stipa_random(input_waveform: AudioWaveform, reference_waveform: AudioWaveform,
                                    duration_sec: float, offset_sec: float = 5, num_segments: int = 3,
                                    butter_order: int = DEFAULT_BUTTER_ORDER,
                                    firwin_filter_params: FirwinFilterParameters = None,
                                    starting_seed: int = None, print_status: bool = False) -> np.ndarray:
    """
    Calculate stipa values for multiple randomly selected segments of a waveform

    Args:
        input_waveform (AudioWaveform): input waveform to assess
        reference_waveform (AudioWaveform): reference waveform used to compare
        duration_sec (float): duration in seconds of each randomly selected segment
        offset_sec (float): offset in seconds at the beginning of the waveform that is ignored
        num_segments (int): number of segments to randomly select and evaluate
        butter_order (int): Butterworth filter order used in octave band filter
        firwin_filter_params (FirwinFilterParameters): low pass filter parameters
        starting_seed (int): random number seed
        print_status (bool): whether to print a status message to the screen for monitoring progress

    Returns:
        Numpy array of STIPA scores for the randomized segments
    """

    stipa_results = []

    logger.info(f"Using {duration_sec} second samples to calculate scores.")

    for i_score in range(num_segments):
        seed = starting_seed
        if i_score > 0:
            seed = None

        if print_status and (i_score + 1) % 10 == 0:
            logger.info(f"Score {i_score + 1} of {num_segments}")

        ref_segment = reference_waveform.get_random_segment(duration_sec=duration_sec,
                                                            offset_sec=offset_sec,
                                                            starting_seed=seed,
                                                            segment_index=i_score)
        input_segment = input_waveform.get_random_segment(duration_sec=duration_sec,
                                                          offset_sec=offset_sec,
                                                          starting_seed=None,
                                                          segment_index=i_score)
        individual_stipa_score = calculate_stipa_from_waveforms(input_segment, ref_segment,
                                                                butter_order=butter_order,
                                                                firwin_filter_params=firwin_filter_params)

        stipa_results.append(individual_stipa_score)

    return np.array(stipa_results)


def calculate_multiple_stipa_sequential(input_waveform: AudioWaveform, reference_waveform: AudioWaveform,
                                        duration_sec: float, offset_sec: float = 5, num_segments: int = 3,
                                        butter_order: int = DEFAULT_BUTTER_ORDER,
                                        firwin_filter_params: FirwinFilterParameters = None,
                                        print_status: bool = False) -> np.ndarray:
    """
    Calculate stipa values for multiple sequential segments of a waveform

    Args:
        input_waveform (AudioWaveform): input waveform to assess
        reference_waveform (AudioWaveform): reference waveform used to compare
        duration_sec (float): duration in seconds of each randomly selected segment
        offset_sec (float): offset in seconds at the beginning of the waveform that is ignored
        num_segments (int): number of segments to randomly select and evaluate
        butter_order (int): Butterworth filter order used in octave band filter
        firwin_filter_params (FirwinFilterParameters): low pass filter parameters
        print_status (bool): whether to print a status message to the screen for monitoring progress

    Returns:
        Numpy array of STIPA scores for the randomized segments
    """

    num_input_segments = input_waveform.get_num_segments(duration_sec=duration_sec, offset_sec=offset_sec)
    num_ref_segments = reference_waveform.get_num_segments(duration_sec=duration_sec, offset_sec=offset_sec)

    if num_input_segments < num_segments or num_ref_segments < num_segments:
        raise StipaCalculationException(f"Number of input segments ({num_input_segments}) or number of reference "
                                        f"segments ({num_ref_segments}) is less than requested number ({num_segments})")

    stipa_results = []

    logger.info(f"Using {duration_sec} second samples to calculate scores.")

    for i_score in range(num_segments):
        if print_status and (i_score + 1) % 10 == 0:
            logger.info(f"Score {i_score + 1} of {num_segments}")

        ref_segment = reference_waveform.get_sequential_segment(duration_sec=duration_sec,
                                                                offset_sec=offset_sec,
                                                                segment_number=i_score)
        input_segment = input_waveform.get_sequential_segment(duration_sec=duration_sec,
                                                              offset_sec=offset_sec,
                                                              segment_number=i_score)
        individual_stipa_score = calculate_stipa_from_waveforms(input_segment, ref_segment,
                                                                butter_order=butter_order,
                                                                firwin_filter_params=firwin_filter_params)
        stipa_results.append(individual_stipa_score)

    return np.array(stipa_results)


def calculate_average_stipa_score(input_waveform: AudioWaveform, reference_waveform: AudioWaveform,
                                  duration_sec: float, offset_sec: float = 5,
                                  num_segments_in_avg: int = 3, score_spread_requirement: float = 0.03,
                                  max_attempts: int = 10, randomize: bool = False,
                                  butter_order: int = DEFAULT_BUTTER_ORDER,
                                  firwin_filter_params: FirwinFilterParameters = None,
                                  starting_seed: int = None) -> float:
    """
    Segment the input_waveform and reference_waveform waveforms to be of duration specified by `duration`.
    Specify the number of segments to include in the average and the required spread in score values required before
    calculating the average. If randomize is set to True, random segments of the waveforms will be compared, otherwise
    the segments will be sequential chunks of the waveforms

    Args:
        input_waveform (AudioWaveform): input waveform to assess
        reference_waveform (AudioWaveform): reference waveform used to compare
        duration_sec (float): duration in seconds of the waveform segments
        offset_sec (float): offset to ignore from start of waveform in seconds
        num_segments_in_avg (int): number of segments to use in the average. Defaults to 3
        score_spread_requirement (float): the spread in STIPA scores required before an average is calculated.
            Defaults to 0.03
        max_attempts (int): Maximum number of attempted segments to calculate to achieve the
            score_spread_requirement before giving up
        randomize (bool): If True (default), then randomly select segments from the waveforms. If False, then
            sequential segments will be selected
        butter_order (int): Butterworth filter order used in octave band filter
        firwin_filter_params (FirwinFilterParameters): low pass filter parameters
        starting_seed (int): optional starting random seed. Defaults to None

    Returns:
        The average calculated STIPA score
    """

    for i_attempt in range(max_attempts):

        if randomize:
            seed = starting_seed
            if i_attempt > 0:
                # only set the seed once
                seed = None

            stipa_results = calculate_multiple_stipa_random(input_waveform=input_waveform,
                                                            reference_waveform=reference_waveform,
                                                            duration_sec=duration_sec, offset_sec=offset_sec,
                                                            num_segments=num_segments_in_avg,
                                                            butter_order=butter_order,
                                                            firwin_filter_params=firwin_filter_params,
                                                            starting_seed=seed)
        else:
            if offset_sec > 0:
                cycle_offset = offset_sec * i_attempt
            else:
                # if no offset in seconds is defined, assume we want to shift by 5 seconds
                cycle_offset = 5.0 * i_attempt
            stipa_results = calculate_multiple_stipa_sequential(input_waveform=input_waveform,
                                                                reference_waveform=reference_waveform,
                                                                duration_sec=duration_sec,
                                                                offset_sec=cycle_offset,
                                                                num_segments=num_segments_in_avg,
                                                                butter_order=butter_order,
                                                                firwin_filter_params=firwin_filter_params)

        if np.max(stipa_results) - np.min(stipa_results) > score_spread_requirement:
            logger.warning(f"Warning for attempt {i_attempt + 1}: STIPA results have too much spread.")
        else:
            average_STIPA = np.mean(stipa_results)
            return average_STIPA

    # if we fail to converge, return None
    return None


def calculate_stipa_from_waveforms(input_waveform: AudioWaveform, reference_waveform: AudioWaveform,
                                   butter_order: int = DEFAULT_BUTTER_ORDER,
                                   firwin_filter_params: FirwinFilterParameters = None) -> float:
    """
    Calculate the STIPA score between two waveforms

    Args:
        input_waveform (AudioWaveform): input waveform to assess
        reference_waveform (AudioWaveform): reference waveform used to compare
        butter_order (int): Butterworth filter order used in octave band filter
        firwin_filter_params (FirwinFilterParameters): low pass filter parameters


    Returns:
        A single calculated STIPA score
    """

    """Following Instructions provided in IEC60268-16-2011 Standard"""
    # Calculate the depth matrix for each waveform
    input_depth_matrix = construct_stipa_depth_matrix(input_waveform,
                                                      butter_order=butter_order,
                                                      firwin_filter_params=firwin_filter_params)
    reference_depth_matrix = construct_stipa_depth_matrix(reference_waveform,
                                                          butter_order=butter_order,
                                                          firwin_filter_params=firwin_filter_params)


    # if our input waveform has low enough sampling rate,
    # the higher frequency octaves do not exist, so just ignore them
    if len(input_depth_matrix) != len(reference_depth_matrix):
        reference_depth_matrix = reference_depth_matrix[:len(input_depth_matrix)]

    # Calculate the modulation transfer matrix, which is the ratio of the input and reference depth matrices
    modulation_transfer_matrix = input_depth_matrix / reference_depth_matrix
    modulation_transfer_matrix[modulation_transfer_matrix > 1.0] = 1.0

    # Calculate the modulation transfer index at each octave
    modulation_transfer_index = calculate_modulation_transfer_index(modulation_transfer_matrix)

    # Calculate the male-weighted STIPA score
    return calculate_weighted_stipa(modulation_transfer_index)
