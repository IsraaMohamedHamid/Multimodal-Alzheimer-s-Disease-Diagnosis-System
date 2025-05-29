#################### IMPORTS ####################
# ALL
import os
import sys
import pathlib
import matplotlib
# Append the parent folder to the python path 
# Get the current notebook's path
notebook_path = os.path.join(os.path.dirname(os.path.abspath('convert_mri_to_image.py')))

# Append the parent directory of the current notebook's directory to the path
sys.path.append(str(pathlib.Path(notebook_path).parent.resolve()))

matplotlib.use('Agg')

# FROM .py SCRIPT
from DataScript.create_data_folders import *
from DataScript.display_images import *
from DataScript.get_data_stats import *
from DataScript.get_patient_data import *
from DataScript.load_and_read_data import *
from DataScript.load_metadata import *
from DataScript.neuroimaging_slices import *

#################### FUNCTIONS ####################

if __name__ == "__main__":
    
    # Get root directory from cmdline
    root_directory = sys.argv[1]

    # Path for the original data
    original_data_path = root_directory + '/Original/'

    # Path for the preprocessed data
    preprocessed_data_path = root_directory + '/Preprocessed/'

    # if this file doesn't exist, create it
    if not os.path.exists(preprocessed_data_path):
        os.makedirs(preprocessed_data_path)

    # Create the folders for the preprocessed data
    # create_categories_folders(preprocessed_data_path)
    create_full_folders_folders(preprocessed_data_path)

    # Check the folder structure of the original data
    # get_folder_structure(original_data_path)

    # Create a reference dataframe for the original data
    ref_df = create_ref_df(root_directory)

    # Save the reference dataframe as a csv file
    ref_df.to_csv(preprocessed_data_path + 'nii_ref_df.csv', index=False)

    # Convert the neuroimaging data to images
    convert_nueoimaging_to_images(original_data_path, preprocessed_data_path, ref_df)
