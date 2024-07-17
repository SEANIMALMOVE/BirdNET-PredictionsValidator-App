# ------------------ Libraries  ------------------

# Web App
import gradio as gr

# Data Processing
import numpy as np

# File Processing
from io import BytesIO

# Audio Processing
import librosa

# Image Processing
from PIL import Image
import plotly.graph_objects as go
import matplotlib.pyplot as plt

'''
This script creates a Gradio interface that allows users to upload 
an audio clip and generates a mel spectrogram image.
'''

# Function to convert audio clip to mel spectrogram image
def audio_to_mel_spectrogram(audio_clip):
    # Load the audio clip
    # audio_clip_path = process_file(audio_clip)

    y, sr = librosa.load(audio_clip, sr=None)

    # Define the frequency range
    fmin = 1  # Minimum frequency (0 Hz)
    fmax = 32000  # Maximum frequency (32000 Hz)

    fig, ax = plt.subplots(figsize=(12, 6))  # Set the background color to black
    D = librosa.amplitude_to_db(librosa.stft(y), ref=np.max)
    librosa.display.specshow(D, sr=sr, x_axis="time", y_axis="log", fmin=fmin, fmax=fmax)  # Specify frequency range
    ax.axis('off')  # Remove axes

    # Convert the plot to an image object
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    buf.seek(0)
    mel_spectrogram_image = Image.open(buf)

    return mel_spectrogram_image

def update_mel_spectrogram(audio_clip):
    mel_spectrogram_image = audio_to_mel_spectrogram(audio_clip)
    # Convert the image to PNG format before returning
    mel_spectrogram_image = mel_spectrogram_image.convert("RGB")
    return mel_spectrogram_image

# Create Gradio interface with custom layout
audio_clip = gr.Audio(label="Upload Audio Clip", type="filepath")
mel_spectrogram = gr.Image(label="Mel Spectrogram")

iface = gr.Interface(
    fn=update_mel_spectrogram,
    inputs=audio_clip,
    outputs=mel_spectrogram,
    title="Audio to Mel Spectrogram",
    description="Upload an audio clip to generate a mel spectrogram image.",
    theme="compact",
)

iface.launch()