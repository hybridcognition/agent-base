"""Tests for voice_transcription.py - faster-whisper integration."""
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


def test_transcribe_valid_audio(sample_audio_file):
    """Test transcribing a valid audio file."""
    from voice_transcription import transcribe_voice

    with patch('voice_transcription.convert_to_wav') as mock_convert, \
         patch('voice_transcription.get_model') as mock_get_model:
        # Mock audio conversion
        mock_convert.return_value = sample_audio_file + ".wav"

        # Mock the model and transcription
        mock_model = Mock()
        mock_segment = Mock()
        mock_segment.text = "This is a test transcription"
        mock_model.transcribe.return_value = ([mock_segment], None)
        mock_get_model.return_value = mock_model

        # Mock os.remove to avoid cleanup errors
        with patch('voice_transcription.os.remove'):
            result = transcribe_voice(sample_audio_file)

        assert result['success'] is True
        assert result['transcription'] == "This is a test transcription"
        assert 'error' not in result or result['error'] is None


def test_transcribe_multiple_segments(sample_audio_file):
    """Test transcribing audio with multiple segments."""
    from voice_transcription import transcribe_voice

    with patch('voice_transcription.convert_to_wav') as mock_convert, \
         patch('voice_transcription.get_model') as mock_get_model:
        # Mock audio conversion
        mock_convert.return_value = sample_audio_file + ".wav"

        mock_model = Mock()

        # Create multiple segments
        seg1 = Mock()
        seg1.text = "First segment"
        seg2 = Mock()
        seg2.text = "Second segment"
        seg3 = Mock()
        seg3.text = "Third segment"

        mock_model.transcribe.return_value = ([seg1, seg2, seg3], None)
        mock_get_model.return_value = mock_model

        # Mock os.remove to avoid cleanup errors
        with patch('voice_transcription.os.remove'):
            result = transcribe_voice(sample_audio_file)

        assert result['success'] is True
        assert result['transcription'] == "First segment Second segment Third segment"


def test_transcribe_nonexistent_file():
    """Test transcribing a file that doesn't exist."""
    from voice_transcription import transcribe_voice

    result = transcribe_voice("/nonexistent/file.ogg")

    assert result['success'] is False
    assert 'error' in result
    assert result['error'] is not None


def test_transcribe_invalid_audio():
    """Test transcribing an invalid audio file."""
    from voice_transcription import transcribe_voice

    # Create invalid file
    invalid_file = "/tmp/invalid_audio.txt"
    with open(invalid_file, "w") as f:
        f.write("This is not audio")

    result = transcribe_voice(invalid_file)

    assert result['success'] is False
    assert 'error' in result

    # Cleanup
    os.remove(invalid_file)


def test_model_lazy_loading():
    """Test that model is lazily loaded once and reused."""
    from voice_transcription import get_model, _model

    with patch('voice_transcription.WhisperModel') as mock_whisper:
        mock_instance = Mock()
        mock_whisper.return_value = mock_instance

        # First call should create model
        model1 = get_model()
        assert mock_whisper.call_count == 1

        # Second call should reuse model
        model2 = get_model()
        assert mock_whisper.call_count == 1  # Should still be 1

        # Both should return same instance
        assert model1 is model2


def test_model_configuration():
    """Test that model is configured correctly."""
    import voice_transcription

    # Reset global model state
    voice_transcription._model = None

    with patch('voice_transcription.WhisperModel') as mock_whisper:
        from voice_transcription import get_model

        get_model()

        # Verify model created with correct parameters
        mock_whisper.assert_called_once_with(
            "small",
            device="cpu",
            compute_type="int8"
        )


def test_audio_conversion(sample_audio_file):
    """Test that audio is converted to WAV format."""
    from voice_transcription import transcribe_voice

    with patch('voice_transcription.get_model') as mock_get_model, \
         patch('voice_transcription.convert_to_wav') as mock_convert:

        mock_wav_path = "/tmp/converted.wav"
        mock_convert.return_value = mock_wav_path

        mock_model = Mock()
        mock_segment = Mock()
        mock_segment.text = "Test"
        mock_model.transcribe.return_value = ([mock_segment], None)
        mock_get_model.return_value = mock_model

        result = transcribe_voice(sample_audio_file)

        # Verify conversion was called
        mock_convert.assert_called_once_with(sample_audio_file)

        # Verify model transcribe called with converted file
        mock_model.transcribe.assert_called_once_with(mock_wav_path)


def test_wav_cleanup(sample_audio_file):
    """Test that temporary WAV files are cleaned up."""
    from voice_transcription import transcribe_voice

    with patch('voice_transcription.get_model') as mock_get_model, \
         patch('voice_transcription.convert_to_wav') as mock_convert, \
         patch('os.remove') as mock_remove:

        mock_wav_path = "/tmp/test.wav"
        mock_convert.return_value = mock_wav_path

        mock_model = Mock()
        mock_segment = Mock()
        mock_segment.text = "Test"
        mock_model.transcribe.return_value = ([mock_segment], None)
        mock_get_model.return_value = mock_model

        transcribe_voice(sample_audio_file)

        # Verify cleanup called
        mock_remove.assert_called_with(mock_wav_path)


def test_transcription_error_handling(sample_audio_file):
    """Test error handling during transcription."""
    from voice_transcription import transcribe_voice

    with patch('voice_transcription.convert_to_wav') as mock_convert, \
         patch('voice_transcription.get_model') as mock_get_model:
        mock_convert.return_value = sample_audio_file + ".wav"

        mock_model = Mock()
        mock_model.transcribe.side_effect = Exception("Transcription failed")
        mock_get_model.return_value = mock_model

        result = transcribe_voice(sample_audio_file)

        assert result['success'] is False
        assert 'error' in result
        assert "Transcription failed" in result['error']


def test_empty_transcription(sample_audio_file):
    """Test handling of empty transcription (no speech detected)."""
    from voice_transcription import transcribe_voice

    with patch('voice_transcription.convert_to_wav') as mock_convert, \
         patch('voice_transcription.get_model') as mock_get_model:
        mock_convert.return_value = sample_audio_file + ".wav"

        mock_model = Mock()
        # No segments (empty list)
        mock_model.transcribe.return_value = ([], None)
        mock_get_model.return_value = mock_model

        with patch('voice_transcription.os.remove'):
            result = transcribe_voice(sample_audio_file)

        assert result['success'] is True
        assert result['transcription'] == ""


def test_transcribe_returns_dict(sample_audio_file):
    """Test that transcribe_voice always returns a dict with expected keys."""
    from voice_transcription import transcribe_voice

    with patch('voice_transcription.convert_to_wav') as mock_convert, \
         patch('voice_transcription.get_model') as mock_get_model:
        mock_convert.return_value = sample_audio_file + ".wav"

        mock_model = Mock()
        mock_segment = Mock()
        mock_segment.text = "Test"
        mock_model.transcribe.return_value = ([mock_segment], None)
        mock_get_model.return_value = mock_model

        with patch('voice_transcription.os.remove'):
            result = transcribe_voice(sample_audio_file)

        # Verify return structure
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'transcription' in result


def test_long_transcription(sample_audio_file):
    """Test handling of long transcriptions with many segments."""
    from voice_transcription import transcribe_voice

    with patch('voice_transcription.convert_to_wav') as mock_convert, \
         patch('voice_transcription.get_model') as mock_get_model:
        mock_convert.return_value = sample_audio_file + ".wav"

        mock_model = Mock()

        # Create 100 segments
        segments = []
        for i in range(100):
            seg = Mock()
            seg.text = f"Segment {i}"
            segments.append(seg)

        mock_model.transcribe.return_value = (segments, None)
        mock_get_model.return_value = mock_model

        with patch('voice_transcription.os.remove'):
            result = transcribe_voice(sample_audio_file)

        assert result['success'] is True
        # Verify all segments joined
        assert "Segment 0" in result['transcription']
        assert "Segment 99" in result['transcription']


def test_special_characters_in_transcription(sample_audio_file):
    """Test handling of special characters in transcription."""
    from voice_transcription import transcribe_voice

    with patch('voice_transcription.convert_to_wav') as mock_convert, \
         patch('voice_transcription.get_model') as mock_get_model:
        mock_convert.return_value = sample_audio_file + ".wav"

        mock_model = Mock()
        mock_segment = Mock()
        mock_segment.text = "Test with émojis 🎉 and spëcial çharacters!"
        mock_model.transcribe.return_value = ([mock_segment], None)
        mock_get_model.return_value = mock_model

        with patch('voice_transcription.os.remove'):
            result = transcribe_voice(sample_audio_file)

        assert result['success'] is True
        assert "émojis 🎉" in result['transcription']
        assert "spëcial çharacters!" in result['transcription']
