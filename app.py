import gradio as gr
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import os
import zipfile
import tempfile

def audio_to_mel_spectrogram(audio_clip):
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

def update_output(audio_clip):
    mel_spectrogram_image = audio_to_mel_spectrogram(audio_clip)
    return mel_spectrogram_image, audio_clip

def list_audio_files_from_zip(zip_path):
    audio_files = []
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        temp_dir = tempfile.mkdtemp()
        zip_ref.extractall(temp_dir)
        # Recorrer el directorio temporal y sus subdirectorios
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(('.mp3', '.wav', ".WAV", ".MP3")):
                    # Asegurarse de que la ruta del archivo se construya correctamente
                    full_path = os.path.join(root, file)
                    audio_files.append(full_path)
    return audio_files

def on_zip_selected(zip_file):
    if not zip_file.name.endswith('.zip'):
        return ["Please upload a .zip file"], None
    audio_files = list_audio_files_from_zip(zip_file)
    return audio_files, audio_files[0] if audio_files else "No audio files found"

# Adjust the interface creation to use gr.File without the filetypes argument
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(label="Upload Audio Clip", type="filepath")
            mel_spectrogram_output = gr.Image(label="Mel Spectrogram")
            # Conectar la entrada de audio con la función update_output
            audio_input.change(fn=update_output, inputs=audio_input, outputs=[mel_spectrogram_output, audio_input])
        with gr.Column():
            zip_input = gr.File(label="Upload Zip File")
            audio_list = gr.Radio(label="Select Audio File")
            # Conectar la selección del archivo zip con la función on_zip_selected
            zip_input.change(fn=on_zip_selected, inputs=zip_input, outputs=[audio_list, audio_input])

demo.launch()