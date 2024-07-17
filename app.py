from tkinter import Tk, filedialog
import gradio as gr
import librosa
import librosa.display
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import os
import zipfile
import tempfile
import tkinter as tk

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

def update_output(audio_clip):
    if isinstance(audio_clip, list):
        # Process each file individually
        # For demonstration, let's just process the first file
        audio_clip = audio_clip[0]

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
            return audio_file_list.to_string(index=False), "Root path: " + root_dir_audio_files, audio_file_list
        else:
            root.destroy()
            return "Files not selected", "Root path: ", pd.DataFrame()
    elif data_type == "Folder":
        folder_path = filedialog.askdirectory()
        # Asumiendo que tienes una función que lista los archivos en el directorio y subdirectorios
        if folder_path:
            audio_files = list_audio_files_from_folder(folder_path)  # Esta función debe estar definida en alguna parte de tu código
            audio_file_list = pd.DataFrame([{"File": os.path.basename(f), "Path": f} for f in audio_files])
            root_dir_audio_files = folder_path
            root.destroy()
            return audio_file_list.to_string(index=False), "Root path: " + root_dir_audio_files, audio_file_list
        else:
            root.destroy()
            return "Folder not selected", "Root path: ", pd.DataFrame()
    else:
        root.destroy()
        return "Please select an upload option", "Root path: ", pd.DataFrame()

# Use a gr.Label to display the root path
root_path_label = gr.Label()

# Use a gr.Dataframe or gr.Dynamic for audio file selection
audio_file_table = gr.Dataframe()

def main():
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                data_type = gr.Radio(choices=["Files", "Folder"], value="Folder", label="Upload Audio Files")
                input_path = gr.Textbox(label="Path of audios", scale=3, interactive=False)
                browse_btn = gr.Button("Browse", min_width=1)
                root_path_label = gr.Label("Root path: ")
                audio_file_table = gr.Dataframe(headers=["File", "Path"], type="pandas")
                browse_btn.click(on_browse, inputs=data_type, outputs=[input_path, root_path_label, audio_file_table])
            with gr.Column():
                audio_input = gr.Audio(label="Upload Audio Clip", type="filepath")
                mel_spectrogram_output = gr.Image(label="Mel Spectrogram")
                # Asegúrate de ajustar esta parte según lo que necesites hacer con el audio seleccionado
                audio_input.change(fn=update_output, inputs=audio_input, outputs=[mel_spectrogram_output, audio_input])
    return demo

demo = main()
demo.launch(inbrowser=True)


'''def main():
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                data_type = gr.Radio(choices=["Files", "Folder"], value="Files", label="Offline data type")
                input_path = gr.Textbox(label="Select Multiple videos", scale=5, interactive=False)
                image_browse_btn = gr.Button("Browse", min_width=1)
                image_browse_btn.click(on_browse, inputs=data_type, outputs=input_path, show_progress="hidden")

                audio_input = gr.Audio(label="Upload Audio Clip", type="filepath")
                mel_spectrogram_output = gr.Image(label="Mel Spectrogram")
                # Conectar la entrada de audio con la función update_output
                audio_input.change(fn=update_output, inputs=audio_input, outputs=[mel_spectrogram_output, audio_input])
            with gr.Column():
                # zip_input = gr.File(label="Upload Zip File")
                audio_list = gr.Radio(label="Select Audio File")
                # Conectar la selección del archivo zip con la función on_zip_selected
                # zip_input.change(fn=on_zip_selected, inputs=zip_input, outputs=[audio_list, audio_input])
    return demo'''