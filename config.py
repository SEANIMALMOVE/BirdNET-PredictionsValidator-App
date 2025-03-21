# config.py

CURRENT_VERSION = "v1.7"  # Replace with your current app version
GITHUB_REPO = "GrunCrow/BirdNET-PredictionsValidator-App"  # Replace with your GitHub repo
SUGGESTED_SPECIES_FILE = "suggested_species.txt"  # File to store suggested species
COMMENTS_FILE = "comments.txt"

class Globals:
    _sample_audio_dir = ""
    _current_specie_name = ""
    _current_sample_audio_file = ""

    _root_dir_audio_files = ""
    _audio_file_list = []
    _current_row_index = -1

    @classmethod
    def set_sample_audio_dir(cls, value):
        cls._sample_audio_dir = value

    @classmethod
    def get_sample_audio_dir(cls):
        return cls._sample_audio_dir
    
    @classmethod
    def set_current_specie_name(cls, value):
        cls._current_specie_name = value

    @classmethod
    def get_current_specie_name(cls):
        return cls._current_specie_name
    
    @classmethod
    def set_current_sample_audio_file(cls, value):
        cls._current_sample_audio_file = value

    @classmethod
    def get_current_sample_audio_file(cls):
        return cls._current_sample_audio_file
    
    @classmethod
    def set_root_dir_audio_files(cls, value):
        cls._root_dir_audio_files = value

    @classmethod
    def get_root_dir_audio_files(cls):
        return cls._root_dir_audio_files
    
    @classmethod
    def set_audio_file_list(cls, value):
        cls._audio_file_list = value

    @classmethod
    def get_audio_file_list(cls):
        return cls._audio_file_list
    
    @classmethod
    def set_current_row_index(cls, value):
        cls._current_row_index = value

    @classmethod
    def get_current_row_index(cls):
        return cls._current_row_index
