"""Voice message transcription using faster-whisper."""
import os
from pathlib import Path
from typing import Dict

import ffmpeg
from faster_whisper import WhisperModel


# Lazy-loaded model (loaded once, reused)
_model = None


def get_model() -> WhisperModel:
    """Get or create Whisper model instance.

    Model is lazily loaded on first call and reused for subsequent calls.

    Returns:
        WhisperModel instance configured for CPU int8
    """
    global _model

    if _model is None:
        _model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

    return _model


def convert_to_wav(audio_path: str) -> str:
    """Convert audio file to 16kHz mono WAV format.

    Args:
        audio_path: Path to input audio file (OGG, MP3, etc.)

    Returns:
        Path to converted WAV file

    Raises:
        Exception: If conversion fails
    """
    wav_path = audio_path + ".wav"

    try:
        (
            ffmpeg
            .input(audio_path)
            .output(wav_path, ar=16000, ac=1, format='wav')
            .overwrite_output()
            .run(quiet=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise Exception(f"Audio conversion failed: {e.stderr.decode()}")

    return wav_path


def transcribe_voice(voice_file_path: str) -> Dict:
    """Transcribe voice message to text.

    Args:
        voice_file_path: Path to voice file (OGG, MP3, WAV, etc.)

    Returns:
        Dictionary with keys:
            - success: bool
            - transcription: str (if success=True)
            - error: str (if success=False)
    """
    try:
        # Check if file exists
        if not os.path.exists(voice_file_path):
            return {
                'success': False,
                'error': f"File not found: {voice_file_path}"
            }

        # Convert to WAV
        wav_path = convert_to_wav(voice_file_path)

        # Transcribe
        model = get_model()
        segments, info = model.transcribe(wav_path)

        # Join all segments
        transcription = " ".join([seg.text for seg in segments])

        # Cleanup temporary WAV file
        if wav_path != voice_file_path:
            os.remove(wav_path)

        return {
            'success': True,
            'transcription': transcription
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
