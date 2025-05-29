
#################### IMPORTS ####################
# ALL
import shutil
import os
import sys
import pathlib
# Append the parent folder to the python path 
# Get the current notebook's path
notebook_path = os.path.join(os.path.dirname(os.path.abspath('move_and_delete_files_and_folders.py')))

# Append the parent directory of the current notebook's directory to the path
sys.path.append(str(pathlib.Path(notebook_path).parent.resolve()))

# FROM .py SCRIPT
from create_data_folders import *
from display_images import *
from get_data_stats import *
from get_patient_data import *
from load_and_read_data import *
from load_metadata import *
from neuroimaging_slices import *

#################### FUNCTIONS ####################

# Check the folder structure of the original data
# Get all the files with paths
def get_all_files(folder_path):
    all_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files

# Move the processed images into categories
def move_images_into_categories(data_folder):
    """
    Moves specified 'anat' directories to a new root directory, adjusting the path to include 'T2star'.

    :param directories: A set of 'anat' directory paths to move.
    :param destination_root: The root directory to move to, which will replace the original root in the path.
    """

    original_perprocessed_images_dir = os.path.join(data_folder, 'Preprocessed')
    # get_folder_structure(source_dir)

    categorised_preprocessed_image_dir = os.path.join(data_folder, 'Preprocessed_Categories')

    if not os.path.exists(categorised_preprocessed_image_dir):
        os.makedirs(categorised_preprocessed_image_dir)
        print(f"Created folder: {categorised_preprocessed_image_dir}")

    # Create the destination directory if it doesn't exist
    create_categories_folders(categorised_preprocessed_image_dir)

    files_dictonary = {}

    for root, dirs, files in os.walk(original_perprocessed_images_dir):
        if files == ".DS_Store": 
            continue
        
        for file in files:
            if file == ".DS_Store": 
                continue

            if file.endswith("png"):
                # Create dictionary with the file name as the key and the value as the full path
                file_full_path = os.path.join(root, file)
                # Add the file to the dictionary
                files_dictonary[file] = file_full_path

    # for file, file_full_path in files_dictonary.items():
    #    print(f"{file} : {file_full_path}")
    count = 0
    for file, file_full_path in files_dictonary.items():

        # Check file name if it conatins OAS1
    
        oasis1_cdr_csv = []
        oasis2_cdr_csv = []
        oasis3_cdr_csv = []
        oasis4_cdr_csv = []

        # Find the path to the CDR files
        if find_file_paths(data_folder, 'oasis1_cross-sectional.csv') != []:
            oasis1_cdr_csv = find_file_paths(data_folder, 'oasis1_cross-sectional.csv')
            oasis1_dcr_df = pd.read_csv(oasis1_cdr_csv[0])
        if find_file_paths(data_folder, 'oasis2_longitudinal_demographics.xlsx') != []:
            oasis2_cdr_csv = find_file_paths(data_folder, 'oasis2_longitudinal_demographics.xlsx')
            oasis2_dcr_df = pd.read_excel(oasis2_cdr_csv[0])
        if find_file_paths(data_folder, 'OASIS3_UDSb4_cdr.csv') != []:
            oasis3_cdr_csv = find_file_paths(data_folder, 'OASIS3_UDSb4_cdr.csv')
            oasis3_dcr_df = pd.read_csv(oasis3_cdr_csv[0])
        if find_file_paths(data_folder, 'OASIS4_data_CDR.csv') != []:
            oasis4_cdr_csv = find_file_paths(data_folder, 'OASIS4_data_CDR.csv')
            oasis4_dcr_df = pd.read_csv(oasis4_cdr_csv[0])

    
        # Get label from information file
        if "OAS1" in file:
            # Using this file name Slice_100_OAS1_0001_MR1_axial_img_1_anon extract the patient_id = 100 and mr_id = 1
            patient_id = file.split('_')[3]
            mr_id = file.split('_')[4]

            # Read the information file
            # OAS1_0001_MR1
            label_id = oasis1_dcr_df[oasis1_dcr_df['ID'] == f'OAS1_{patient_id}_{mr_id}']['CDR'].values[0]
            

        elif "OAS2" in file:
            # Slice_100_OAS2_0001_MR2_axial_img_3.png
            patient_id = file.split('_')[3]
            mr_id = file.split('_')[4]

            # check to see if oasis_dataset_number + patient_id is in OASISID column then return CDRTOT column
            label_id = oasis2_dcr_df[oasis2_dcr_df['Subject ID'] == f'OAS2_{patient_id}']['CDR'].values[0]


        elif "OAS3" in file:
            # Extract from "sub-OAS30036_sess-d1199_T2star_slice_11_Sagittal_img.png"  the "OAS30036"
            patient_id = file.split('_')[2]
            patient_id = patient_id[4:]

            # check to see if oasis_dataset_number + patient_id is in OASISID column then return CDRTOT column
            label_id = oasis3_dcr_df[oasis3_dcr_df['OASISID'] == patient_id]['CDRTOT'].values[0]
            
        elif "OAS4" in file:
            patient_id = file.split('_')[3]

            # check to see if oasis_dataset_number + patient_id is in OASISID column then return CDRTOT column
            label_id = oasis4_dcr_df[oasis4_dcr_df['oasis_id'] == patient_id]['cdr'].values[0]

        # Move each item to the destination directory
        dest_item = os.path.join(categorised_preprocessed_image_dir, get_cdr_label(float(label_id)), file)
        
        # Check if the destination item already exists
        if os.path.exists(dest_item):
            # If it's a directory, remove it before moving
            if os.path.isdir(dest_item):
                shutil.rmtree(dest_item)
            else:
                # It's a file, remove it to override
                os.remove(dest_item)
        
        # Move each item to the destination directory
        shutil.copy(file_full_path, dest_item)
        # print(f"Copy and/or overridden {file_full_path} to {dest_item}")

        count += 1
        print(f"Completed file: {count}/{len(files_dictonary.items())}")


# Move the folder if a file exists
def move_folder_if_file_exists(source_folder, destination_folder, file_to_check):
    """
    Moves the source folder to the destination folder if a specific file exists in the source folder.

    :param source_folder: The path to the source folder to be moved.
    :param destination_folder: The path to the destination folder where the source folder should be moved.
    :param file_to_check: The file whose existence triggers the move.
    """
    if os.path.exists(file_to_check):
        try:
            # Calculate the destination path including the folder name
            dest_path = os.path.join(destination_folder, os.path.basename(source_folder))
            # Move the folder
            shutil.move(source_folder, dest_path)
            print(f"Moved '{source_folder}' to '{dest_path}' because it contains the specified file.")
        except Exception as e:
            print(f"Error moving folder: {e}")
    else:
        print(f"The file '{file_to_check}' does not exist in '{source_folder}', not moving.")


# Get file path for all files in the original_data directory that end with .nii.gz
# Go through all folder in the original_data directory
def get_files_list(original_data, destination_folder, extension="_T2w.nii.gz"):
    files_list = []
    for root, dirs, files in os.walk(original_data):

        # Go through all files in the folder
        for file in files:
            # Check if the file ends with .nii.gz
            if file.endswith(extension):
                # Get the full file path
                file_path = os.path.join(root, file)
                
                files_list.append(file_path)

                for file in files_list:
                    # Define the specific file to check for before moving the folder
                    file_to_check = file

                    # Define the source folder (parent directory of the file)
                    source_folder = os.path.dirname(os.path.dirname(os.path.dirname(file_to_check)))

                    move_folder_if_file_exists(source_folder, destination_folder, file_to_check)

    return files_list

def find_anat_directories_containing_t2star(file_paths):
    """
    Identifies 'anat' directories containing a '_T2star.nii.gz' file.

    :param file_paths: List of file paths to check.
    :return: A set of unique 'anat' directories to be moved.
    """
    directories_to_move = set()
    for path in file_paths:
        print(path)
        if path.endswith("_T2w.nii.gz"):
            # Split the path and find the 'anat' segment
            print(path)
            parts = path.split(os.sep)
            anat_index = [i for i, part in enumerate(parts) if part.startswith('anat')]
            if anat_index:
                # Construct the directory path to move
                dir_to_move = os.sep.join(parts[:anat_index[0] + 1])
                directories_to_move.add(dir_to_move)
    return directories_to_move

def move_anat_directories(directories, destination_root):
    """
    Moves specified 'anat' directories to a new root directory, adjusting the path to include 'T2star'.

    :param directories: A set of 'anat' directory paths to move.
    :param destination_root: The root directory to move to, which will replace the original root in the path.
    """
    for dir_path in directories:
        print(f"Moving '{dir_path}'...")
        # Update the directory path to include 'T2star' instead of 'T2W'
        new_path = dir_path.replace("T2star","T2W")
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        # Move the directory
        shutil.move(dir_path, new_path)
        print(f"Moved '{dir_path}' to '{new_path}'.")


def delete_folder(folder_path):
    """
    Deletes the folder at the specified path along with all its contents.

    :param folder_path: The path to the folder to be deleted.
    """
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' has been deleted.")
    else:
        print(f"The specified path '{folder_path}' does not exist or is not a directory.")


def move_and_override(source_dir, dest_dir):
    """
    Moves all contents of source_dir to dest_dir, overriding existing files.

    :param source_dir: The path of the source directory.
    :param dest_dir: The path of the destination directory.
    """
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        dest_item = os.path.join(dest_dir, item)
        
        # Check if the destination item already exists
        if os.path.exists(dest_item):
            # If it's a directory, remove it before moving
            if os.path.isdir(dest_item):
                shutil.rmtree(dest_item)
            else:
                # It's a file, remove it to override
                os.remove(dest_item)
        
        # Move each item to the destination directory
        shutil.move(source_item, dest_item)
        print(f"Moved and/or overridden {source_item} to {dest_item}")