# Web App
from tkinter import Tk, filedialog
import gradio as gr

# Audio processing
import librosa
import librosa.display

# Data processing
import numpy as np
import pandas as pd

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

SUGGESTED_SPECIES_FILE = "suggested_species.txt"

def initialize_suggested_species_file():
    if not os.path.exists(SUGGESTED_SPECIES_FILE):
        with open(SUGGESTED_SPECIES_FILE, 'w') as file:
            pass  # Create an empty file

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

def on_audio_selected(selected_row, evt: gr.SelectData):
    """
    Process the selected audio and return relevant information.

    Args:
        selected_row (pandas.DataFrame): The selected row containing audio information.
        evt (gr.SelectData): The event object containing additional information.

    Returns:
        tuple: A tuple containing the following information:
            - mel_spectrogram_image (numpy.ndarray): The mel spectrogram image of the selected audio.
            - audio_path (str): The path of the selected audio file.
            - species_name (str): The name of the species associated with the selected audio.
            - selected_row_index (int): The index of the selected row.
            - sample_audio (str): The path of a sample audio file for the selected species.
            - sample_image (numpy.ndarray): The mel spectrogram image of the sample audio file.
            - suggested_specie (str): The suggested species for the selected audio.

            If no audio is selected or an error occurs, the tuple will contain None values.
    """
    if not selected_row.empty:
        if evt and evt.index:
            selected_row_index = evt.index[0]
            audio_path = selected_row["Path"][selected_row_index]
            audio_path = os.path.normpath(audio_path)
            species_name = selected_row["Specie"][selected_row_index]
            suggested_specie = selected_row["Suggested Specie"][selected_row_index] if "Suggested Specie" in selected_row else None
            mel_spectrogram_image = update_output(audio_path)
            sample_audio_path = "Bird Vocalization Samples" + os.sep + species_name
            sample_audio_files = list_audio_files_from_folder(sample_audio_path)
            if sample_audio_files:
                sample_audio = sample_audio_files[0]
                sample_image = update_output(sample_audio)
            else:
                sample_audio = None
                sample_image = None
                print("No audio files found for the selected species")

            return mel_spectrogram_image, audio_path, species_name, selected_row_index, sample_audio, sample_image, suggested_specie
    return None, None, "Specie", -1, None, None, None

def update_output(audio_clip_path):
    """
    Update the output by converting an audio clip to a mel spectrogram image.

    Parameters:
    audio_clip_path (str): The path to the audio clip file.

    Returns:
    mel_spectrogram_image: The mel spectrogram image generated from the audio clip.
    """
    mel_spectrogram_image = audio_to_mel_spectrogram(audio_clip_path)
    return mel_spectrogram_image

def list_audio_files_from_folder(folder_path):
    """
    Lists all audio files (with extensions .mp3, .wav, .WAV, .MP3) in the given folder and its subfolders.

    Args:
        folder_path (str): The path to the folder to search for audio files.

    Returns:
        list: A list of full paths to the audio files found.
    """

    audio_files = []
    # Walk through the folder and subfolders and list all audio files
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.mp3', '.wav', ".WAV", ".MP3")):
                full_path = os.path.join(root, file)
                audio_files.append(full_path)
    return audio_files

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

def on_browse(data_type):
    """
    Opens a file dialog to browse and select audio files or folders.

    Parameters:
    - data_type (str): The type of data to browse. Can be "Files" or "Folder".

    Returns:
    - tuple: A tuple containing a string message and a pandas DataFrame.
        - The string message indicates the result of the browse operation.
        - The pandas DataFrame contains information about the selected audio files.

    """

    global root_dir_audio_files
    global audio_file_list

    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    if data_type == "Files":
        filenames = filedialog.askopenfilenames()
        if filenames:
            # Extract audio time
            audio_file_list = pd.DataFrame([{"Specie": f.split(os.sep)[-2], "Time": convert_to_hhmmss(f),"File": os.path.basename(f), "Validation": -1, "Suggested Specie": " ", "Path": f} for f in filenames])
            root_dir_audio_files = os.path.dirname(filenames[0])
            root.destroy()
            return audio_file_list.to_string(index=False), audio_file_list
        else:
            root.destroy()
            return "Files not selected", pd.DataFrame()
    elif data_type == "Folder":
        folder_path = filedialog.askdirectory()
        if folder_path:
            folder_path = os.path.normpath(folder_path)
            filenames = list_audio_files_from_folder(folder_path)
            audio_file_list = pd.DataFrame([{"Specie": f.split(os.sep)[-2], "Time": convert_to_hhmmss(f), "File": os.path.basename(f),"Validation": -1, "Path": f} for f in filenames])
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
def update_validation(audio_table, row_index, new_value, suggestedSpecie=None):
    """
    Update the validation status of an audio in the audio_table.

    Args:
        audio_table (pandas.DataFrame): The table containing the audio data.
        row_index (int): The index of the row to update.
        new_value (int): The new validation status to assign to the audio.
        suggestedSpecie (str, optional): The suggested species for the audio. Defaults to None.

    Returns:
        pandas.DataFrame: The updated audio_table with the validation status and suggested species updated.

    """
    if 0 <= row_index < len(audio_table):
        # Change value of the row row index, column validation to newvalue
        audio_table.at[row_index, "Validation"] = new_value
        audio_table.at[row_index, "Suggested Specie"] = suggestedSpecie

        def style_row(row):
            # Check the Validation value and apply color styling to the entire row
            if row["Validation"] == 1:
                return ['background-color: #63C132'] * len(row)  # Green for Validation = 1
            elif row["Validation"] == -2:
                # light grey for Unknown
                return ['background-color: #D3D3D3'] * len(row)
            elif row["Validation"] == 0:
                if row["Suggested Specie"] is not None:
                    return ['background-color: #FFA500'] * len(row) # Orange for Suggested Specie
                return ['background-color: #B02E0C'] * len(row)  # Red for Validation = 0
            elif row["Validation"] == 2:
                # Light green for Bird
                return ['background-color: #78c451'] * len(row)
            else:
                return [''] * len(row)  # Default, no styling

        audio_table = audio_table.style.apply(style_row, axis=1)

    return audio_table

def on_species_button_clicked(audio_table, selected_row_index):
    """
    Update the validation of the audio table for the selected row index to 1 for 'Specie'.

    Args:
        audio_table (list): The audio table to be updated.
        selected_row_index (int): The index of the selected row.

    Returns:
        list: The updated audio table.
    """
    audio_table = update_validation(audio_table, selected_row_index, 1)  # Update to 1 for 'Specie'
    return audio_table

def on_unknown_button_clicked(audio_table, selected_row_index):
    """
    Updates the validation status of the selected audio in the audio table to 'Unknown' (-1).

    Args:
        audio_table (list): The audio table containing the audio data.
        selected_row_index (int): The index of the selected row in the audio table.

    Returns:
        list: The updated audio table with the validation status of the selected audio set to 'Unknown' (-2).
    """
    audio_table = update_validation(audio_table, selected_row_index, -2)  # Update to -2 for 'Unknown'
    return audio_table

def on_bird_button_clicked(audio_table, selected_row_index):
    """
    Updates the validation status of the selected row in the audio table to 1 (Bird).

    Parameters:
    audio_table (list): The list of audio data.
    selected_row_index (int): The index of the selected row.

    Returns:
    list: The updated audio_table with the validation status of the selected row set to 1.
    """
    audio_table = update_validation(audio_table, selected_row_index, 2, "Bird")  # Update to 1 for 'Bird'
    return audio_table

def on_other_button_clicked(audio_table, selected_row_index):
    """
    Updates the audio_table by setting the validation status of the selected row to 0 (Other).

    Parameters:
    audio_table (list): The list of audio data.
    selected_row_index (int): The index of the selected row.

    Returns:
    list: The updated audio_table with the validation status of the selected row set to 0.
    """
    audio_table = update_validation(audio_table, selected_row_index, 0)  # Update to 0 for 'Other'
    return audio_table

def add_suggested_species(species):
    with open(SUGGESTED_SPECIES_FILE, 'r') as file:
        species_list = file.read().splitlines()
    
    # If specie is not in the list, add it as the last row
    if species not in species_list:
        with open(SUGGESTED_SPECIES_FILE, 'a') as file:
            file.write(species + "\n")

    # if specie is in the list, move it to the last row
    else:
        species_list.remove(species)
        species_list.append(species)
        with open(SUGGESTED_SPECIES_FILE, 'w') as file:
            for specie in species_list:
                file.write(specie + "\n")

def get_suggested_species():
    with open(SUGGESTED_SPECIES_FILE, 'r') as file:
        species_list = file.read().splitlines()
    return species_list

def on_suggested_specie_button_clicked(audio_table, selected_row_index, suggested_specie_text):
    species = suggested_specie_text.strip() if suggested_specie_text else None
    print(f"Suggested species: {species}")
    if species:
        add_suggested_species(species)
        # Update the audio table with the suggested species
        audio_table = update_validation(audio_table, selected_row_index, 0, species)  # Update to 0 for 'Other'
    return audio_table, gr.update(choices=get_suggested_species())

def suggestedSpecie_button_clicked(audio_table, selected_row_index, suggestedSpecie):
    """
    Updates the audio table with the suggested species for the selected row.

    Parameters:
    audio_table (list): The audio table containing the audio data.
    selected_row_index (int): The index of the selected row in the audio table.
    suggestedSpecie (str): The suggested species for the selected row.

    Returns:
    list: The updated audio table with the suggested species updated for the selected row.
    """
    audio_table = update_validation(audio_table, selected_row_index, 0, suggestedSpecie)  # Update to 0 for 'Other'
    return audio_table

# Use a gr.Dataframe or gr.Dynamic for audio file selection
audio_file_table = gr.Dataframe()

def load_csv_and_copy_validation(audio_table):
    """
    Loads a CSV file, maps the validation values to the audio table, and applies color styling to the table rows based on the validation values.

    Parameters:
    - audio_table (DataFrame): The audio table to be updated.

    Returns:
    - audio_table (DataFrame): The updated audio table with validation values and color styling applied.
    - message (str): A message indicating the result of the operation.
    """
    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        # Map per File from audio table and df and change Validation value to df value
        audio_table["Validation"] = df["File"].map(df.set_index("File")["Validation"])
        audio_table["Suggested Specie"] = df["File"].map(df.set_index("File")["Suggested Specie"])

        def style_row(row):
            # Check the Validation value and apply color styling to the entire row
            if row["Validation"] == 1:
                return ['background-color: #63C132'] * len(row)  # Green for Validation = 1
            elif row["Validation"] == -2:
                # light grey for Unknown
                return ['background-color: #D3D3D3'] * len(row)
            elif row["Validation"] == 0:
                if row["Suggested Specie"] is not None:
                    return ['background-color: #FFA500'] * len(row) # Orange for Suggested Specie
                return ['background-color: #B02E0C'] * len(row)  # Red for Validation = 0
            elif row["Validation"] == 2:
                # Light green for Bird
                return ['background-color: #78c451'] * len(row)
            else:
                return [''] * len(row)  # Default, no styling

        audio_table = audio_table.style.apply(style_row, axis=1)

        root.destroy()
        return audio_table, "Validation Values Loaded"  # Devuelve el DataFrame de Pandas con los valores de validación
    else:
        root.destroy()
        return pd.DataFrame(), "ERROR: No Validation File"  # Devuelve un DataFrame vacío si se cancela la operación

def save_table_to_csv(audio_table):
    """
    Saves the given audio table to a CSV file.

    Parameters:
    audio_table (pandas.DataFrame): The audio table to be saved.

    Returns:
    str: A message indicating the status of the save operation.
    """

    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()  # Hide the root window
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        # Save all columns but Path
        table_to_save = audio_table.drop(columns=["Path"])
        table_to_save.to_csv(file_path, index=False)
        root.destroy()
        return f"Validation saved to {file_path}"
    else:
        root.destroy()
        return "Save operation cancelled"
    
def update_table_with_validation(audio_table):
    """
    Update the audio table with validation data.

    Parameters:
    audio_table (str): The path to the audio table.

    Returns:
    validation_df (pandas.DataFrame): The validation data loaded from the CSV file.
    msg (str): A message indicating the status of the operation.
    """
    validation_df, msg = load_csv_and_copy_validation(audio_table)
    return validation_df, msg

def tutorial_tab():
    """
    Generate the tutorial tab content.

    Returns:
    gr.Blocks: The tutorial tab content.
    """
    with gr.Blocks() as tutorial:
        gr.Markdown("""
        # Tutorial

        ## Purpose of the Application
        The BirdNET Predictions Validator App is designed to help validate bird species predictions generated by BirdNET. This tool allows users to view and listen to audio segments and record the accuracy of predictions in a downloadable CSV file.

        ## How to Use the Application

        ### Load Audios
        1. Navigate to the "Load Audios" tab.
        2. Select "Files" or "Folder" and click "Browse" to upload your audio files.

        ### Validate Predictions
        1. Go to the "Validate BirdNET predictions" tab.
        2. Select an audio file from the table.
        3. View the mel spectrogram and listen to the audio.
        4. Use the "Specie", "Other", and "Unknown" buttons to validate the predictions.
        5. If necessary, enter a suggested species and click "Suggested Specie".

        ### Save and Load Validations
        1. To save the validations, click "Save Table".
        2. To load previous validations from a CSV file, click "Load CSV and Copy Validation".
                    
        ## Video Tutorial
        
        """)

        embed_html = '<iframe width="560" height="315" src="https://www.youtube.com/embed/BJYW3RqA2uQ?si=SVWU3tZrFiRqfVuD" title="Tutorial" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
        gr.HTML(embed_html)

    return tutorial

def main():
    """
    This function sets up the main user interface for the Label Audios App.
    It creates various UI elements such as audio and image components, data tables, and buttons.
    The function also defines event handlers for user interactions with the UI elements.
    
    Returns:
        gr.Blocks: The main UI component.
    """
    initialize_suggested_species_file()
    sample_audio = gr.Audio(label="Sample Audio per specie", type="filepath")
    sample_image = gr.Image("Sample Mel Spectrogram")
    audio_file_table = gr.Dataframe(headers=["File", "Specie", "Suggested Specie"], type="pandas", interactive=False)
    with gr.Blocks() as demo:
        selected_row_index = gr.Number(visible=False)
        with gr.Tab("Load Audios"):
            gr.Markdown("## Load Audio Files")
            data_type = gr.Radio(choices=["Files", "Folder"], value="Folder", label="Upload Audio Files")
            input_path = gr.Textbox(label="Path of audios", scale=3, interactive=False)
            browse_btn = gr.Button("Browse", min_width=1)
            browse_btn.click(on_browse, inputs=data_type, outputs=[input_path, audio_file_table])
        with gr.Tab("Validate BirdNET predictions"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## Audio Files")
                    audio_file_table.render()
                    save_table_btn = gr.Button("Save Table", variant="primary")
                    load_csv_btn = gr.Button("Load CSV and Copy Validation", variant="primary")
                    csv_status = gr.Label(value="No Validation Saved or Loaded")  # To display the status of the save operation

                with gr.Column():
                    gr.Markdown("## Validation")
                    # Define audio_input and mel_spectrogram_output before using them in audio_file_table.select
                    audio_input = gr.Audio(label="Audio", type="filepath", autoplay=True, loop=True)
                    mel_spectrogram_output = gr.Image(label="Mel Spectrogram")

                    # Specie Validation Buttons
                    with gr.Row():
                        species_button = gr.Button("Specie", variant="primary", size="sm")  # Botón verde, el texto se actualizará dinámicamente
                        other_button = gr.Button("Other", variant="stop", size="sm")  # Botón rojo
                    
                    with gr.Row():
                        unknown_button = gr.Button("Unknown", variant="secondary", size="sm")  # Botón naranja  
                        bird_button = gr.Button("Bird", variant="secondary", size="sm")

                    with gr.Row():
                        suggested_species = get_suggested_species()
                        suggestedSpecie_text = gr.Dropdown(choices=suggested_species, label="Suggested Specie", interactive=True, allow_custom_value=True)
                        suggestedSpecie_button = gr.Button("Suggested Specie", variant="primary", size="sm")
                        
                    audio_file_table.select(fn=on_audio_selected, inputs=[audio_file_table], outputs=[mel_spectrogram_output, audio_input, species_button, selected_row_index, sample_audio, sample_image, suggestedSpecie_text])
                    
                    species_button.click(on_species_button_clicked, inputs=[audio_file_table, selected_row_index], outputs=audio_file_table)
                    unknown_button.click(on_unknown_button_clicked, inputs=[audio_file_table, selected_row_index], outputs=audio_file_table)
                    other_button.click(on_other_button_clicked, inputs=[audio_file_table, selected_row_index], outputs=audio_file_table)
                    bird_button.click(on_bird_button_clicked, inputs=[audio_file_table, selected_row_index], outputs=audio_file_table)
                    suggestedSpecie_button.click(on_suggested_specie_button_clicked, inputs=[audio_file_table, selected_row_index, suggestedSpecie_text], outputs=[audio_file_table, suggestedSpecie_text])
                    
                    save_table_btn.click(fn=save_table_to_csv, inputs=audio_file_table, outputs=csv_status)
                    load_csv_btn.click(fn=update_table_with_validation, inputs=audio_file_table, outputs=[audio_file_table, csv_status])

                with gr.Column():
                    gr.Markdown("## Sample Audio & Spectrogram")
                    sample_audio.render()
                    sample_image.render()
        with gr.Tab("Tutorial"):
            tutorial_tab()
    
        # GitHub Issues Link
        gr.Markdown("""
            <div style="text-align: center;">
                <a href="https://github.com/GrunCrow/BirdNET-PredictionsValidator-App/issues" target="_blank" style="display: inline-flex; align-items: center; text-decoration: none; color: inherit;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" alt="GitHub" width="30" height="30" style="vertical-align: middle; margin-right: 8px;">
                    <span>To report issues or provide feedback, please visit the GitHub repository</span>
                </a>
            </div>
            """)
    return demo

demo = main()
demo.launch(inbrowser=True, inline=True, show_api=False)