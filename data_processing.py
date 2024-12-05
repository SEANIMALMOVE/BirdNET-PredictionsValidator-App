# data_processing.py

from tkinter import Tk, filedialog

import pandas as pd

from ui_components import apply_styles

def load_csv_and_copy_validation(audio_table):
    """
    Loads a CSV file, maps the validation values to the audio table, and applies color styling to the table rows based on the validation values.

    Parameters:
    - audio_table (DataFrame): The audio table to be updated.

    Returns:
    - audio_table (DataFrame): The updated audio table with validation values and color styling applied.
    - message (str): A message indicating the result of the operation.
    """
    try:
        root = Tk()
        root.attributes("-topmost", True)
        root.withdraw()  # Hide the root window
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = pd.read_csv(file_path)
            # Map per File from audio table and df and change Validation value to df value
            audio_table = audio_table.merge(df[['File', 'Validation', 'Suggested Specie']], on='File', how='left')
            
            # If exists Validation_x and Validation_y, keep Validation from df
            if 'Validation_x' in audio_table and 'Validation_y' in audio_table:
                audio_table['Validation'] = audio_table['Validation_y']
                audio_table = audio_table.drop(columns=['Validation_x', 'Validation_y'])
            # If exists Suggested Specie_x and Suggested Specie_y, keep Suggested Specie from df
            if 'Suggested Specie_x' in audio_table and 'Suggested Specie_y' in audio_table:
                audio_table['Suggested Specie'] = audio_table['Suggested Specie_y']
                audio_table = audio_table.drop(columns=['Suggested Specie_x', 'Suggested Specie_y'])

            audio_table = audio_table.style.apply(apply_styles, axis=1)

            root.destroy()
            return audio_table, "Validation Values Loaded"  # Devuelve el DataFrame de Pandas con los valores de validación
        else:
            root.destroy()
            return pd.DataFrame(), "ERROR: No Validation File"  # Devuelve un DataFrame vacío si se cancela la operación
    except Exception as e:
        return pd.DataFrame(), f"ERROR: {str(e)}"
    
    
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