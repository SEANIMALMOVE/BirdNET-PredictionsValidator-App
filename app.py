# Web App
from tkinter import Tk, filedialog
import gradio as gr
import tkinter as tk

# Audio processing
import librosa
import librosa.display

# Data processing
import numpy as np
import pandas as pd
import zipfile
import tempfile

# Image processing
import matplotlib.pyplot as plt
from PIL import Image

# File handling
from io import BytesIO
import os

global root_dir_audio_files
root_dir_audio_files = ""
global audio_file_list
audio_file_list = []

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

def on_audio_selected(selected_row, evt: gr.SelectData):
    if not selected_row.empty:
        if evt and evt.index:
            selected_row_index = evt.index[0]  # Obtener el índice de la fila seleccionada
            audio_path = selected_row["Path"][selected_row_index]  # Asumiendo que la columna 1 contiene la ruta del archivo
        
            # audio_path = selected_row["Path"][0]  # Asumiendo que "Path" es la columna que contiene la ruta del archivo
            return update_output(audio_path)
    return None, None

# Paso 4: Asegurarse de que update_output maneje un path de archivo como entrada
def update_output(audio_clip_path):
    mel_spectrogram_image = audio_to_mel_spectrogram(audio_clip_path)
    return mel_spectrogram_image, audio_clip_path

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

def list_audio_files_from_folder(folder_path):
    audio_files = []
    # Recorrer el directorio y sus subdirectorios
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.mp3', '.wav', ".WAV", ".MP3")):
                # Asegurarse de que la ruta del archivo se construya correctamente
                full_path = os.path.join(root, file)
                audio_files.append(full_path)
    return audio_files

def on_browse(data_type):
    global root_dir_audio_files
    global audio_file_list
    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    if data_type == "Files":
        filenames = filedialog.askopenfilenames()
        if filenames:
            audio_file_list = pd.DataFrame([{"File": os.path.basename(f), "Path": f} for f in filenames])
            root_dir_audio_files = os.path.dirname(filenames[0])
            root.destroy()
            return audio_file_list.to_string(index=False), audio_file_list
        else:
            root.destroy()
            return "Files not selected", pd.DataFrame()
    elif data_type == "Folder":
        folder_path = filedialog.askdirectory()
        # Asumiendo que tienes una función que lista los archivos en el directorio y subdirectorios
        if folder_path:
            audio_files = list_audio_files_from_folder(folder_path)  # Esta función debe estar definida en alguna parte de tu código
            audio_file_list = pd.DataFrame([{"File": os.path.basename(f), "Path": f} for f in audio_files])
            root_dir_audio_files = folder_path
            root.destroy()
            return audio_file_list.to_string(index=False), audio_file_list
        else:
            root.destroy()
            return "Folder not selected", pd.DataFrame()
    else:
        root.destroy()
        return "Please select an upload option", pd.DataFrame()

# Use a gr.Label to display the root path
# root_path_label = gr.Label()

# Use a gr.Dataframe or gr.Dynamic for audio file selection
audio_file_table = gr.Dataframe()

def main():
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                audio_file_table = gr.Dataframe(headers=["File", "Path"], type="pandas", interactive=False)
                data_type = gr.Radio(choices=["Files", "Folder"], value="Folder", label="Upload Audio Files")
                input_path = gr.Textbox(label="Path of audios", scale=3, interactive=False)
                browse_btn = gr.Button("Browse", min_width=1)
                # root_path_label = gr.Label("Root path: ")
            with gr.Column():
                # Define audio_input and mel_spectrogram_output before using them in audio_file_table.select
                audio_input = gr.Audio(label="Upload Audio Clip", type="filepath")
                mel_spectrogram_output = gr.Image(label="Mel Spectrogram")
                browse_btn.click(on_browse, inputs=data_type, outputs=[input_path, audio_file_table])
                # Now audio_input and mel_spectrogram_output are defined before being used here
                audio_file_table.select(fn=on_audio_selected, inputs=[audio_file_table], outputs=[mel_spectrogram_output, audio_input])

    return demo

demo = main()
demo.launch(inbrowser=True)