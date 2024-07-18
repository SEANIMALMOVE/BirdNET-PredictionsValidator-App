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
            species_name = selected_row["Specie"][selected_row_index]  # Obtener el nombre de la especie de la fila seleccionada
            # audio_path = selected_row["Path"][0]  # Asumiendo que "Path" es la columna que contiene la ruta del archivo
            mel_spectrogram_image = update_output(audio_path)
            return mel_spectrogram_image, audio_path, species_name, selected_row_index
    return None, None, "Specie", -1

def update_output(audio_clip_path):
    mel_spectrogram_image = audio_to_mel_spectrogram(audio_clip_path)
    return mel_spectrogram_image

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
            audio_file_list = pd.DataFrame([{"Specie": f.split("/")[-2], "File": os.path.basename(f), "Validation": -1, "Path": f} for f in filenames])
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
            filenames = list_audio_files_from_folder(folder_path)  # Esta función debe estar definida en alguna parte de tu código
            audio_file_list = pd.DataFrame([{"Specie": f.split("/")[-2], "File": os.path.basename(f),"Validation": -1, "Path": f} for f in filenames])
            root_dir_audio_files = folder_path
            root.destroy()
            return audio_file_list.to_string(index=False), audio_file_list
        else:
            root.destroy()
            return "Folder not selected", pd.DataFrame()
    else:
        root.destroy()
        return "Please select an upload option", pd.DataFrame()
    

# Buttons
def update_validation(audio_table, row_index, new_value):
    if 0 <= row_index < len(audio_table):
        # Change value of the row row index, column validation to newvalue
        # print row_index value
        audio_table.at[row_index, "Validation"] = new_value
        # audio_file_table.update(audio_table)  # Asumiendo que df es el DataFrame que alimenta audio_file_table
        # Style df, if Validation = 1, set row color to green, if Validation = 0, set row color to red, if Validation = -1, set row color to orange
        # audio_table.style(audio_table, row_styles=[{"color": "green" if v == 1 else "red" if v == 0 else "orange"} for v in audio_table["Validation"]])

    return audio_table

def on_species_button_clicked(audio_table, selected_row_index):
    audio_table = update_validation(audio_table, selected_row_index, 1)  # Actualiza a 1 para 'Specie'
    return audio_table

def on_unknown_button_clicked(audio_table, selected_row_index):
    audio_table = update_validation(audio_table, selected_row_index, -1)  # Actualiza a -1 para 'Unknown'
    return audio_table

def on_other_button_clicked(audio_table, selected_row_index):
    audio_table = update_validation(audio_table, selected_row_index, 0)  # Actualiza a 0 para 'Other'
    return audio_table

def save_table(audio_table):
    # Save the table to a csv file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, "audio_table.csv")
        # Save all columns but Path
        audio_table_to_save = audio_table.drop(columns=["Path"])
        audio_table_to_save.to_csv(temp_file, index=False)
    return "Table saved successfully"


# Use a gr.Label to display the root path
# root_path_label = gr.Label()

# Use a gr.Dataframe or gr.Dynamic for audio file selection
audio_file_table = gr.Dataframe()

# selected_row_index = gr.Number(visible=False)  # Usamos gr.Number pero lo hacemos invisible

def main():
    with gr.Blocks() as demo:
        selected_row_index = gr.Number(visible=False)
        with gr.Row():
            with gr.Column():
                audio_file_table = gr.Dataframe(headers=["File"], type="pandas", interactive=False)
                data_type = gr.Radio(choices=["Files", "Folder"], value="Folder", label="Upload Audio Files")
                input_path = gr.Textbox(label="Path of audios", scale=3, interactive=False)
                browse_btn = gr.Button("Browse", min_width=1)
                # root_path_label = gr.Label("Root path: ")
            with gr.Column():
                # Define audio_input and mel_spectrogram_output before using them in audio_file_table.select
                audio_input = gr.Audio(label="Upload Audio Clip", type="filepath")
                mel_spectrogram_output = gr.Image(label="Mel Spectrogram")
                with gr.Row():
                    species_button = gr.Button("Specie", variant="primary", )  # Botón verde, el texto se actualizará dinámicamente
                    unknown_button = gr.Button("Unknown", variant="secondary")  # Botón naranja
                    other_button = gr.Button("Other", variant="stop")  # Botón rojo
                # save_table = gr.Button("Save Table", variant="primary")
                browse_btn.click(on_browse, inputs=data_type, outputs=[input_path, audio_file_table])
                # Now audio_input and mel_spectrogram_output are defined before being used here
                audio_file_table.select(fn=on_audio_selected, inputs=[audio_file_table], outputs=[mel_spectrogram_output, audio_input, species_button, selected_row_index])
                species_button.click(on_species_button_clicked, inputs=[audio_file_table, selected_row_index], outputs=audio_file_table)
                unknown_button.click(on_unknown_button_clicked, inputs=[audio_file_table, selected_row_index], outputs=audio_file_table)
                other_button.click(on_other_button_clicked, inputs=[audio_file_table, selected_row_index], outputs=audio_file_table)
                # save_table.click(save_table, inputs=audio_file_table)
    return demo

demo = main()
demo.launch(inbrowser=True)