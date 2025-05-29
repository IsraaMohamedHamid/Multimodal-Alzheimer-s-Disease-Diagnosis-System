#################### IMPORTS ####################
# ALL
import os
import sys
import pathlib

# FROM .py SCRIPT
from DataScript.load_metadata import cdr_mapping

#################### FUNCTIONS ####################

# This function is used to create the categories folders.
def create_categories_folders(preprocessed_data_path):
    
    # Define the paths for the different dementia levels
    categories_file_paths = [os.path.join(preprocessed_data_path, category) for category in cdr_mapping.values()]

    # Check if the directories exist, if not create them.
    for category, category_path in zip(cdr_mapping.values(), categories_file_paths):
        if not os.path.exists(category_path):
            os.makedirs(category_path)
            print(f"Created folder: {category_path}")
        else:
            print(f"Folder already exists: {category_path}")


# This function is used to create the image folders.
def create_image_folders(preprocessed_data_path):
    """Create image folders (Axial, Coronal, Sagittal) within the specified directory."""
    for folder_name in ['Axial', 'Coronal', 'Sagittal']:
        folder_path = os.path.join(preprocessed_data_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")
    
    if os.path.exists(preprocessed_data_path) and os.path.isdir(preprocessed_data_path):
        create_image_folders(folder_path)
        # Add your logic for processing the RAW folder here

# Create ['Axial', 'Coronal', 'Sagittal'] folders and inside each of them, create the categories folders
def create_full_folders_folders(preprocessed_data_path):
    """Create image folders (Axial, Coronal, Sagittal) within the specified directory."""

    for folder_name in ['Axial', 'Coronal', 'Sagittal']:
        folder_path = os.path.join(preprocessed_data_path, folder_name)
         # Check to see if files already exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
            # Create the categories folders
            create_categories_folders(folder_path)
        else:
            print(f"Folder already exists: {folder_path}")

