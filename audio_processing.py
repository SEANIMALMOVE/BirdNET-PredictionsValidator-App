# audio_processing.py

import numpy as np

# Audio processing
import librosa
import librosa.display

# Image processing
import matplotlib.pyplot as plt
from PIL import Image

# File handling
import os
from io import BytesIO
from pathlib import Path

# Caching
from functools import lru_cache

import gradio as gr

#                       Cache functions
# ============================================================
@lru_cache(maxsize=128)
def load_audio_files_from_folder(folder_path):
    return list_audio_files_from_folder(folder_path)

@lru_cache(maxsize=128)
def load_audio(file_path):
    return file_path

@lru_cache(maxsize=128)
def get_mel_spectrogram(file_path):
    audio_data = load_audio(file_path)
    mel_spectrogram = audio_to_mel_spectrogram(audio_data)
    return mel_spectrogram

def audio_to_mel_spectrogram(audio_clip):
    """
    Convert an audio clip to a mel spectrogram image.

    Parameters:
    audio_clip (str): The path to the audio clip file.

    Returns:
    PIL.Image.Image: The mel spectrogram image.
    """
    y, sr = librosa.load(audio_clip, sr=None)
    fmin = 1
    fmax = 32000
    fig, ax = plt.subplots(figsize=(12, 6))
    D = librosa.amplitude_to_db(librosa.stft(y), ref=np.max)
    librosa.display.specshow(D, sr=sr, x_axis="time", y_axis="log", fmin=fmin, fmax=fmax, ax=ax)
    ax.axis('off')
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    image = Image.open(buf)
    return image

def list_audio_files_from_folder(folder_path):
    """
    Lists all audio files (with extensions .mp3, .wav, .WAV, .MP3) in the given folder and its subfolders.

    Args:
        folder_path (str): The path to the folder to search for audio files.

    Returns:
        list: A list of full paths to the audio files found.
    """

    return [str(file) for file in Path(folder_path).rglob('*') if file.suffix.lower() in ['.mp3', '.wav']]

def convert_to_hhmmss(filename):
    # Extract the 2nd and 3rd parameters from the filename
    parts = os.path.basename(filename).split("_")
    
    # Convert parts[2] (HHMMSS) to total seconds
    hhmmss = parts[2]
    hours = int(hhmmss[:2])
    minutes = int(hhmmss[2:4])
    seconds = int(hhmmss[4:6])
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    # Add the seconds from parts[3] (which is in milliseconds)
    additional_seconds = int(parts[3]) / 1000
    total_seconds += additional_seconds
    
    # Convert total seconds to HH:MM:SS format
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    # Format the result as HH:MM:SS
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def update_audio_and_image(audio_path):
    audio = load_audio(audio_path)
    image = get_mel_spectrogram(audio_path)

    return audio, image
