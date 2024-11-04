import os
import pandas as pd

from config import SUGGESTED_SPECIES_FILE

def initialize_suggested_species_file():
    required_columns = ["species", "count"]
    try:
        if not os.path.exists(SUGGESTED_SPECIES_FILE):
            with open(SUGGESTED_SPECIES_FILE, 'w') as file:
                file.write(",".join(required_columns) + "\n")  # Create an empty file with headers
        else:
            # Backup the existing file
            backup_file = SUGGESTED_SPECIES_FILE + ".bak"
            if os.path.exists(backup_file):
                os.remove(backup_file)
            os.rename(SUGGESTED_SPECIES_FILE, backup_file)
            
            df = pd.read_csv(backup_file)
            df['count'] = 0  # Reset the count to 0
            
            # Ensure the correct column order and save the new file
            df = df[required_columns]

            # Ensure file is deleted before writing to it
            if os.path.exists(SUGGESTED_SPECIES_FILE):
                os.remove(SUGGESTED_SPECIES_FILE)

            df.to_csv(SUGGESTED_SPECIES_FILE, index=False)
    except Exception as e:
        print(f"Error initializing suggested species file: {str(e)}")
        # If an error occurs, change name of file to avoid further errors and create a new one
        error_backup_file = SUGGESTED_SPECIES_FILE + ".error.bak"
        if os.path.exists(error_backup_file):
            os.remove(error_backup_file)
        os.rename(SUGGESTED_SPECIES_FILE, error_backup_file)
        if os.path.exists(SUGGESTED_SPECIES_FILE):
            os.remove(SUGGESTED_SPECIES_FILE)
        initialize_suggested_species_file()

def add_suggested_species(species):
    if os.path.exists(SUGGESTED_SPECIES_FILE):
        df = pd.read_csv(SUGGESTED_SPECIES_FILE)
    else:
        df = pd.DataFrame(columns=["species", "count"])
    
    if species in df['species'].values:
        df.loc[df['species'] == species, 'count'] += 1
    else:
        new_row = pd.DataFrame([[species, 1]], columns=["species", "count"])
        df = pd.concat([df, new_row], ignore_index=True)
    
    df = df.sort_values(by='count')
    df.to_csv(SUGGESTED_SPECIES_FILE, index=False)

def get_suggested_species():
    if os.path.exists(SUGGESTED_SPECIES_FILE):
        df = pd.read_csv(SUGGESTED_SPECIES_FILE)
        df = df.sort_values(by='count')
        return df['species'].tolist()
    else:
        return []