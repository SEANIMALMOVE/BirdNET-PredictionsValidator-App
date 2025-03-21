# app.py

# Web App
from tkinter import Tk, filedialog
import gradio as gr

# Data processing
import pandas as pd

import os

from audio_processing import load_audio_files_from_folder, update_audio_and_image, list_audio_files_from_folder, extract_time_from_filename, extract_date_from_filename
from species_management import add_suggested_species, get_suggested_species, initialize_suggested_species_file, initialize_comments_file, add_comment, get_comments
from data_processing import save_table_to_csv, update_table_with_validation
from ui_components import build_footer, tutorial_tab, on_audio_selected, update_validation, get_sample_audio_and_image

# Global variables
from config import Globals

def on_browse(data_type):
    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    if data_type == "Files":
        filenames = filedialog.askopenfilenames()
        if filenames:
            # Extraer tiempo de audio
            Globals.set_audio_file_list(pd.DataFrame([
                {"Idx": idx + 1, "Specie": f.split(os.sep)[-2], "File": os.path.basename(f), "Validation": -100, "Suggested Specie": " ", "Path": f}
                for idx, f in enumerate(filenames)
            ]))
            Globals.set_root_dir_audio_files(os.path.dirname(filenames[0]))
            root.destroy()
            return Globals.get_audio_file_list().to_string(index=False), Globals.get_audio_file_list()
        else:
            root.destroy()
            return "Files not selected", pd.DataFrame()
    elif data_type == "Folder":
        folder_path = filedialog.askdirectory()
        if folder_path:
            folder_path = os.path.normpath(folder_path)
            with gr.Blocks() as progress:
                gr.Markdown("Loading audio files, please wait...")
                filenames = load_audio_files_from_folder(folder_path)  # Usando caché
            Globals.set_audio_file_list(pd.DataFrame([
                {"Idx": idx+1,"Specie": f.split(os.sep)[-2], "File": os.path.basename(f), "Validation": -100, "Suggested Specie": " ", "Path": f}
                for idx, f in enumerate(filenames)
            ]))
            Globals.set_root_dir_audio_files(folder_path)
            root.destroy()
            return Globals.get_audio_file_list().to_string(index=False), Globals.get_audio_file_list()
        else:
            root.destroy()
            return "Folder not selected", pd.DataFrame()
    else:
        root.destroy()
        return "Please select an upload option", pd.DataFrame()

def on_browse_sample_audio_folder():

    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()

    folder = filedialog.askdirectory()
    if folder:
        Globals.set_sample_audio_dir(os.path.normpath(folder))
        # print("New sample audio folder selected:", sample_audio_dir)
        root.destroy()
    else:
        root.destroy()


# Buttons

def on_species_button_clicked(audio_table, selected_row_index, comment):
    """
    Handle the event when the species button is clicked.

    Parameters:
    - audio_table (pandas.DataFrame): The audio table.
    - selected_row_index (int): The index of the selected row.

    Returns:
    - tuple: Updated audio table, new selected row index, audio, image, current species name, current sample audio file, sample image, current species name.
    """
    add_comment(comment)
    audio_table.at[selected_row_index, "Comment"] = comment if comment else pd.NA

    audio_table = update_validation(audio_table, selected_row_index, 1)  # Update to 1 for 'Specie'

    selected_row_index += 1

    # Check if the selected_row_index is within the range of the audio_table
    if selected_row_index < len(audio_table.data):
        next_audio = load_next_audio_file()
        audio, image = update_audio_and_image(next_audio)

        audio_files = Globals.get_audio_file_list()
        new_specie_name = audio_files["Specie"][selected_row_index]

        if new_specie_name != Globals.get_current_specie_name():
            Globals.set_current_specie_name(new_specie_name)
            
        sample_audio, sample_image = get_sample_audio_and_image()

        Globals.set_current_sample_audio_file(sample_audio)

        audio_path = audio_files["Path"][selected_row_index]
        time = extract_time_from_filename(audio_path)
        date = extract_date_from_filename(audio_path)

        return audio_table, selected_row_index, audio, image, Globals.get_current_specie_name(), Globals.get_current_sample_audio_file(), sample_image, Globals.get_current_specie_name(), date, time
    else:
        # If it's the last row, stop the audio and return the current state
        return audio_table, selected_row_index, None, None, Globals.get_current_specie_name(), None, None, Globals.get_current_specie_name(), None, None

def on_unknown_button_clicked(audio_table, selected_row_index, comment):

    add_comment(comment)
    audio_table.at[selected_row_index, "Comment"] = comment if comment else pd.NA

    audio_table = update_validation(audio_table, selected_row_index, -2)  # Update to -2 for 'Unknown'
    selected_row_index += 1
    next_audio = load_next_audio_file()
    audio, image = update_audio_and_image(next_audio)

    audio_files = Globals.get_audio_file_list()
    new_specie_name = audio_files["Specie"][selected_row_index]

    if new_specie_name != Globals.get_current_specie_name():
        Globals.set_current_specie_name(new_specie_name)
        
    sample_audio, sample_image = get_sample_audio_and_image()

    Globals.set_current_sample_audio_file(sample_audio)

    return audio_table, selected_row_index, audio, image, Globals.get_current_specie_name(), Globals.get_current_sample_audio_file(), sample_image, Globals.get_current_specie_name()

def on_bird_button_clicked(audio_table, selected_row_index, comment):

    add_comment(comment)
    audio_table.at[selected_row_index, "Comment"] = comment if comment else pd.NA

    audio_table = update_validation(audio_table, selected_row_index, 2, "Bird")  # Update to 1 for 'Bird'
    selected_row_index += 1
    next_audio = load_next_audio_file()
    audio, image = update_audio_and_image(next_audio)

    audio_files = Globals.get_audio_file_list()
    new_specie_name = audio_files["Specie"][selected_row_index]

    if new_specie_name != Globals.get_current_specie_name():
        Globals.set_current_specie_name(new_specie_name)
        
    sample_audio, sample_image = get_sample_audio_and_image()

    Globals.set_current_sample_audio_file(sample_audio)

    return audio_table, selected_row_index, audio, image, Globals.get_current_specie_name(), Globals.get_current_sample_audio_file(), sample_image, Globals.get_current_specie_name()

def on_other_button_clicked(audio_table, selected_row_index, comment):    
    
    add_comment(comment)
    audio_table.at[selected_row_index, "Comment"] = comment if comment else pd.NA

    audio_table = update_validation(audio_table, selected_row_index, -1)  # Update to 0 for 'Other'
    selected_row_index += 1
    next_audio = load_next_audio_file()
    audio, image = update_audio_and_image(next_audio)

    audio_files = Globals.get_audio_file_list()
    new_specie_name = audio_files["Specie"][selected_row_index]

    if new_specie_name != Globals.get_current_specie_name():
        Globals.set_current_specie_name(new_specie_name)
        
    sample_audio, sample_image = get_sample_audio_and_image()

    Globals.set_current_sample_audio_file(sample_audio)

    return audio_table, selected_row_index, audio, image, Globals.get_current_specie_name(), Globals.get_current_sample_audio_file(), sample_image, Globals.get_current_specie_name()

def on_suggested_specie_button_clicked(audio_table, selected_row_index, suggested_specie_text, comment):
    
    # Add comment if it doesnt exist
    add_comment(comment)

    audio_table.at[selected_row_index, "Comment"] = comment if comment else pd.NA
    
    species = suggested_specie_text.strip() if suggested_specie_text else None
    # print(f"Suggested species: {species}")
    if species:
        add_suggested_species(species)
        # Update the audio table with the suggested species

    audio_table = update_validation(audio_table, selected_row_index, 0, species)  # Update to 0 for 'Other'
    selected_row_index += 1
    next_audio = load_next_audio_file()
    audio, image = update_audio_and_image(next_audio)

    audio_files = Globals.get_audio_file_list()
    new_specie_name = audio_files["Specie"][selected_row_index]

    if new_specie_name != Globals.get_current_specie_name():
        Globals.set_current_specie_name(new_specie_name)
        
    sample_audio, sample_image = get_sample_audio_and_image()

    Globals.set_current_sample_audio_file(sample_audio)

    return audio_table, gr.update(choices=get_suggested_species()), selected_row_index, audio, image, Globals.get_current_specie_name(), Globals.get_current_sample_audio_file(), sample_image, Globals.get_current_specie_name()

# Use a gr.Dataframe or gr.Dynamic for audio file selection
audio_file_table = gr.Dataframe()

# Function to get the list of sample files
def get_sample_files():
    # return sorted if audio fie .WAV, .wav, .MP3, .mp3
    specie_audio_dir = Globals.get_sample_audio_dir() + os.sep + Globals.get_current_specie_name()
    sample_audio_files = list_audio_files_from_folder(specie_audio_dir)
    return sample_audio_files

def load_next_audio_file():
    audio_files = Globals.get_audio_file_list()
    next_index = (Globals.get_current_row_index() + 1) % len(audio_files)
    Globals.set_current_row_index(next_index)
    current_audio_file = audio_files["Path"][next_index]
    return current_audio_file

def load_prev_audio_file():
    audio_files = Globals.get_audio_file_list()
    prev_index = (Globals.get_current_row_index() - 1) % len(audio_files)
    # get current audio file
    Globals.set_current_row_index(prev_index)
    current_audio_file = audio_files["Path"][prev_index]
    return current_audio_file

# Function to load the next sample
def load_next_sample():

    sample_files = get_sample_files()

    current_index = sample_files.index(Globals.get_current_sample_audio_file())
    next_index = (current_index + 1) % len(sample_files)
    Globals.set_current_sample_audio_file(sample_files[next_index])
    return Globals.get_current_sample_audio_file()

# Function to load the previous sample
def load_prev_sample():
    sample_files = get_sample_files()
    current_index = sample_files.index(Globals.get_current_sample_audio_file())
    prev_index = (current_index - 1) % len(sample_files)
    Globals.set_current_sample_audio_file(sample_files[prev_index])
    return Globals.get_current_sample_audio_file()

def main():
    """
    This function sets up the main user interface for the Label Audios App.
    It creates various UI elements such as audio and image components, data tables, and buttons.
    The function also defines event handlers for user interactions with the UI elements.
    
    Returns:
        gr.Blocks: The main UI component.
    """
    
    initialize_suggested_species_file()
    initialize_comments_file()

    # Get comments from the initialized file
    comments = get_comments()
    if not comments:  # If there are no comments, set the default option
        comments = ["No Comments"]

    sample_audio = gr.Audio(label="Sample Audio per specie", type="filepath")
    sample_image = gr.Image("Sample Mel Spectrogram")
    audio_file_table = gr.Dataframe(headers=["Idx", "File", "Specie", "Suggested Specie"], type="pandas", interactive=False)
    comment_box = gr.Dropdown(value="No comments", choices=comments, label="Comments", interactive=True, allow_custom_value=True, filterable=True)

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
                    # Display Date and Time
                    with gr.Row():
                        date_text = gr.Textbox(label="Recording Date", interactive=False)
                        time_text = gr.Textbox(label="Recording Time", interactive=False)

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
                        suggestedSpecie_text = gr.Dropdown(choices=suggested_species, label="Suggested Specie", interactive=True, allow_custom_value=True, filterable=True)
                        suggestedSpecie_button = gr.Button("Suggested Specie", variant="primary", size="sm")
                        
                    audio_file_table.select(fn=on_audio_selected, inputs=[audio_file_table], outputs=[mel_spectrogram_output, audio_input, species_button, selected_row_index, sample_audio, sample_image, suggestedSpecie_text, audio_file_table, date_text, time_text, comment_box])
                    
                    species_button.click(on_species_button_clicked, inputs=[audio_file_table, selected_row_index, comment_box], outputs=[audio_file_table, selected_row_index, audio_input, mel_spectrogram_output, species_button, sample_audio, sample_image])
                    unknown_button.click(on_unknown_button_clicked, inputs=[audio_file_table, selected_row_index, comment_box], outputs=[audio_file_table, selected_row_index, audio_input, mel_spectrogram_output, species_button, sample_audio, sample_image])
                    other_button.click(on_other_button_clicked, inputs=[audio_file_table, selected_row_index, comment_box], outputs=[audio_file_table, selected_row_index, audio_input, mel_spectrogram_output, species_button, sample_audio, sample_image])
                    bird_button.click(on_bird_button_clicked, inputs=[audio_file_table, selected_row_index, comment_box], outputs=[audio_file_table, selected_row_index, audio_input, mel_spectrogram_output, species_button, sample_audio, sample_image])
                    suggestedSpecie_button.click(on_suggested_specie_button_clicked, inputs=[audio_file_table, selected_row_index, suggestedSpecie_text, comment_box], outputs=[audio_file_table, suggestedSpecie_text, selected_row_index, audio_input, mel_spectrogram_output, species_button, sample_audio, sample_image, suggestedSpecie_text])
                    
                    save_table_btn.click(fn=save_table_to_csv, inputs=audio_file_table, outputs=csv_status)
                    load_csv_btn.click(fn=update_table_with_validation, inputs=audio_file_table, outputs=[audio_file_table, csv_status])

                with gr.Column():
                    gr.Markdown("## Sample Audio & Spectrogram")
                    sample_audio.render()
                    sample_image.render()
                    with gr.Row():
                        prev_button = gr.Button("←", variant="secondary")
                        next_button = gr.Button("→", variant="secondary")
                    
                    prev_button.click(
                        fn=lambda: update_audio_and_image(load_prev_sample()), 
                        inputs=[], 
                        outputs=[sample_audio, sample_image]
                    )
                    next_button.click(
                        fn=lambda: update_audio_and_image(load_next_sample()), 
                        inputs=[], 
                        outputs=[sample_audio, sample_image]
                    )
                    # Add folder selection button
                    browse_samplefolder_btn = gr.Button("Select Sample Audio Folder", min_width=1)
                    browse_samplefolder_btn.click(on_browse_sample_audio_folder, inputs=[], outputs=[])

                    # Add observations box to write
                    # gr.Textbox(label="Observations", type="text", placeholder="Write your observations here...", scale=3)
                    # comment_box = gr.Textbox(label="Comments", type="text", placeholder="Write your comments here...", scale=3)
                    comment_box.render()
        with gr.Tab("Tutorial"):
            tutorial_tab()

        with gr.Row():
            # Build and display the footer
            build_footer()

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
# launch in port 7864
demo.launch(inbrowser=True, inline=True, show_api=False, server_port=7864)