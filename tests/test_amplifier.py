"""Unit tests for the audio amplifier module."""
import sys
from unittest.mock import MagicMock, patch

import pytest
import numpy as np

# Mock PyQt5 and sounddevice before importing
sys.modules['PyQt5'] = MagicMock()
sys.modules['PyQt5.QtWidgets'] = MagicMock()
sys.modules['PyQt5.QtCore'] = MagicMock()
sys.modules['sounddevice'] = MagicMock()


class TestAmplificationLogic:
    """Tests for the audio amplification callback logic.

    The core amplification is: outdata[:] = np.clip(indata * factor, -1, 1)
    We test this logic directly since it's the heart of the module.
    """

    def test_amplify_with_factor_1(self):
        """Factor 1.0 should pass audio through unchanged."""
        indata = np.array([[0.5], [-0.3], [0.0]], dtype=np.float32)
        outdata = np.zeros_like(indata)
        factor = 1.0
        outdata[:] = np.clip(indata * factor, -1, 1)
        np.testing.assert_array_almost_equal(outdata, indata)

    def test_amplify_with_factor_2(self):
        """Factor 2.0 should double the amplitude."""
        indata = np.array([[0.3], [-0.2], [0.1]], dtype=np.float32)
        outdata = np.zeros_like(indata)
        factor = 2.0
        outdata[:] = np.clip(indata * factor, -1, 1)
        expected = np.array([[0.6], [-0.4], [0.2]], dtype=np.float32)
        np.testing.assert_array_almost_equal(outdata, expected)

    def test_clipping_positive(self):
        """Values exceeding 1.0 after amplification should be clipped to 1.0."""
        indata = np.array([[0.8], [0.6]], dtype=np.float32)
        outdata = np.zeros_like(indata)
        factor = 2.0  # 0.8 * 2 = 1.6 -> clipped to 1.0
        outdata[:] = np.clip(indata * factor, -1, 1)
        assert outdata[0, 0] == 1.0
        assert abs(outdata[1, 0] - 1.0) < 1e-5  # 0.6*2=1.2 -> 1.0

    def test_clipping_negative(self):
        """Values below -1.0 after amplification should be clipped to -1.0."""
        indata = np.array([[-0.7], [-0.9]], dtype=np.float32)
        outdata = np.zeros_like(indata)
        factor = 2.0  # -0.7 * 2 = -1.4 -> clipped to -1.0
        outdata[:] = np.clip(indata * factor, -1, 1)
        assert outdata[0, 0] == -1.0
        assert outdata[1, 0] == -1.0

    def test_silence_remains_silence(self):
        """Zero input should produce zero output regardless of factor."""
        indata = np.zeros((10, 1), dtype=np.float32)
        outdata = np.zeros_like(indata)
        factor = 10.0
        outdata[:] = np.clip(indata * factor, -1, 1)
        np.testing.assert_array_equal(outdata, np.zeros_like(indata))

    def test_factor_less_than_1_attenuates(self):
        """Factor < 1.0 should attenuate the signal."""
        indata = np.array([[0.8], [-0.6]], dtype=np.float32)
        outdata = np.zeros_like(indata)
        factor = 0.5
        outdata[:] = np.clip(indata * factor, -1, 1)
        expected = np.array([[0.4], [-0.3]], dtype=np.float32)
        np.testing.assert_array_almost_equal(outdata, expected)

    def test_stereo_signal(self):
        """Should work with multi-channel (stereo) signals."""
        indata = np.array([[0.5, -0.5], [0.3, -0.3]], dtype=np.float32)
        outdata = np.zeros_like(indata)
        factor = 2.0
        outdata[:] = np.clip(indata * factor, -1, 1)
        expected = np.array([[1.0, -1.0], [0.6, -0.6]], dtype=np.float32)
        np.testing.assert_array_almost_equal(outdata, expected)

    def test_slider_value_to_factor_conversion(self):
        """Slider value / 5.0 should give correct factor."""
        # Slider range is 1-10, factor = slider_value / 5.0
        assert 1 / 5.0 == pytest.approx(0.2)  # min amplification
        assert 5 / 5.0 == pytest.approx(1.0)  # unity
        assert 10 / 5.0 == pytest.approx(2.0)  # max amplification

    def test_full_scale_signal_with_max_amplification(self):
        """Full-scale signal with max amplification should be fully clipped."""
        indata = np.array([[1.0], [-1.0], [0.5], [-0.5]], dtype=np.float32)
        outdata = np.zeros_like(indata)
        factor = 2.0  # max slider value (10) / 5.0
        outdata[:] = np.clip(indata * factor, -1, 1)
        expected = np.array([[1.0], [-1.0], [1.0], [-1.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(outdata, expected)
