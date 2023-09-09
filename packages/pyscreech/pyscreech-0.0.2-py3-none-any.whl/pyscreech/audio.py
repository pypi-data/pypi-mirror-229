from __future__ import annotations

import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
from loguru import logger

class WaveformOperationException(Exception):
    pass

class AudioWaveform(object):
    """
    Object holding an audio waveform
    """

    def __init__(self, timeseries: np.ndarray, sample_rate: float, name: str = None):
        """
        Initialize the AudioWaveform object
        Args:
            timeseries (np.ndarray): the waveform timeseries data
            sample_rate (float): sampling frequency of the data points in Hz
            name (str): name of the waveform (Optional)
        """
        self.name = name
        self.timeseries = np.asarray(timeseries)
        self.sample_rate = sample_rate

    def get_times(self) -> np.ndarray:
        """
        Use the sample rate to get the array of relative times associated with the waveform

        Returns:
            Numpy array with relative timestamps for the waveform
        """
        time_step = 1.0 / self.sample_rate
        times = np.arange(0, (len(self.timeseries)) * time_step, time_step)

        # deal with floating point imprecision
        if len(times) > len(self.timeseries):
            times = times[:len(self.timeseries)]

        return times

    def get_segment(self, duration_sec: float, segment_start_sec: float, segment_name: str = None) -> AudioWaveform:
        """
        Get a segment of a waveform given a start time and requested duration

        Args:
            duration_sec (float): Requested duration in seconds
            segment_start_sec (float): Requested start time in seconds, relative to t=0 being the first point in the
                waveform
            segment_name (str): Optional string to name the segment

        Returns:
            Segment of the original waveform as an AudioWaveform object
        """

        num_points_in_segment = int(duration_sec * self.sample_rate)
        index_lo = int(segment_start_sec * self.sample_rate)
        index_hi = int(index_lo + num_points_in_segment)

        if segment_start_sec < 0.0:
            raise WaveformOperationException("Negative segment start time is not allowed")

        if index_hi > len(self.timeseries):
            raise WaveformOperationException("Requested segment extends past end of waveform")

        return AudioWaveform(timeseries=self.timeseries[index_lo:index_hi],
                             sample_rate=self.sample_rate,
                             name=segment_name)

    def get_sequential_segment(self, duration_sec: float, segment_number: int, offset_sec: float = 5) -> AudioWaveform:
        """
        Get the segment_number-th segment of this waveform of duration duration_sec in seconds, and
        offsets from the beginning of the file and between each segment of offset_sec in seconds

        Args:
            duration_sec (float): duration of the segment in seconds
            segment_number (int): the sequential segment number
            offset_sec (float): offset in seconds from the beginning of the file and between each segment

        Returns:
            AudioWaveform object with the requested segment of the original waveform
        """

        if self.name is not None:
            name = f"{self.name}_{segment_number}"
        else:
            name = f"segment_{segment_number}"

        segment_start_sec = offset_sec + duration_sec * segment_number

        return self.get_segment(duration_sec=duration_sec, segment_start_sec=segment_start_sec, segment_name=name)

    def get_random_segment(self, duration_sec: float, offset_sec: float = 5, starting_seed: int = None,
                           segment_index: int = None) -> AudioWaveform:

        if starting_seed is not None:
            logger.info(f"Seeding random number generator with seed={starting_seed}")
            np.random.seed(starting_seed)

        max_time_sec = len(self.timeseries) / self.sample_rate

        segment_start_sec = np.random.uniform(low=offset_sec, high=max_time_sec - duration_sec)

        if segment_index is None:
            segment_index = f"{segment_start_sec:.2f}"

        if self.name is not None:
            name = f"{self.name}_{segment_index}"
        else:
            name = f"segment_{segment_index}"

        return self.get_segment(duration_sec=duration_sec, segment_start_sec=segment_start_sec, segment_name=name)




    def get_num_segments(self, duration_sec: float, offset_sec: float = 5) -> int:
        """
        Calculate the number of sequential segments that the waveform can be divided into, given a
        duration of duration_sec per segment and with gaps of offset_sec between segments. First gap
        happens at the beginning of the file

        Args:
            duration_sec (float): duration of the segment in seconds
            offset_sec (float): offset in seconds from the beginning of the file and between each segment

        Returns:
            The integer number of full sequential segments given the request parameters
        """
        num_points_offset = offset_sec * self.sample_rate
        num_points_duration = duration_sec  * self.sample_rate
        num_points_available = len(self.timeseries) - num_points_offset
        num_segments = int(num_points_available / num_points_duration)

        if num_segments <= 0:
            raise WaveformOperationException(f"duration_sec={duration_sec} and offset_sec={offset_sec} results in no segments")

        return num_segments


    def plot_timeseries(self, ax=None):
        """
        Plot the timeseries

        Args:
            ax: the matplotlib axis to use
        """
        if ax is None:
            f, ax = plt.subplots()

        ax.set_title(f"self.name (Sample Rate: {self.sample_rate} Hz")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.plot(self.get_times(), self.timeseries)

    def plot_mel_spectrogram(self, n_fft: int = 2048, hop_length: int = 512, n_mels: int = 128, ax: plt.axes = None):
        """
        Plot the waveform frequencies on the Mel scale

        Args:
            n_fft:
            hop_length:
            n_mels:
            ax:
        """
        if ax is None:
            f, ax = plt.subplots()

        S = librosa.feature.melspectrogram(y=self.timeseries, sr=self.sample_rate, n_fft=n_fft, hop_length=hop_length,
                                           n_mels=n_mels)
        S_DB = librosa.power_to_db(S, ref=np.max)
        librosa.display.specshow(S_DB, sr=self.sample_rate, hop_length=hop_length, x_axis='time', y_axis='mel', ax=ax)

    @staticmethod
    def load_audio(filename: str) -> AudioWaveform:
        """Load Audio File into a Waveform object

        Args:
            filename (str): Only .wav file type has been tested

        Returns:
            AudioWaveform: Waveform Object containing timeseries data
        """

        with sf.SoundFile(filename) as of:
            logger.info(
                f"File: `{filename}` Sample Rate: {of.samplerate} Hz, nChannels: {of.channels}, BitDepth: {str(of.subtype).replace('PCM_', '')}")

        wave, rate = librosa.load(filename, sr=None)
        return AudioWaveform(timeseries=wave, sample_rate=rate, name=filename)
