#################### IMPORTS ####################
# AS
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nibabel as nib  # For neuroimaging data
import plotly.express as px

# FROM
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from PIL import Image
from scipy.stats import skew
from tqdm import tqdm

# FROM FILE
from DataScript.load_metadata import *

#################### FUNCTIONS ####################

# Load images from folders
def load_images_from_folders(root_dir, folder_names):
    images_dict = {folder: [] for folder in folder_names}
    
    for folder in folder_names:
        full_path = os.path.join(root_dir, folder)  # Make sure to specify your base path here
        if os.path.exists(full_path):
            for dirname, _, filenames in os.walk(full_path):
                for filename in filenames:
                    images_dict[folder].append(os.path.join(dirname, filename))
        else:
            print(f"Folder '{folder}' not found, skipping...")

    return images_dict

# Load the files based on their extension
def load_files_with_extension(folder_path, extension):
    """Load NIfTI files and their corresponding metadata from the given folder."""
    nifti_files = []
    nifti_files_with_path = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:

            if file.endswith(extension):
                # If os.path.join(root, file) containns 'PROCESSED' or 'FSL_SEG', skip
                if 'PROCESSED' in os.path.join(root, file) or 'FSL_SEG' in os.path.join(root, file):
                    continue

                # Special handling for '.nii.gz' extension
                nifti_files.append(remove_file_extension(file))
                nifti_files_with_path.append(os.path.join(root, file))


    return nifti_files, nifti_files_with_path

# This function will read a CSV file
def read_csv(file_path):
    return pd.read_csv(file_path)

# This function will read multiple CSV files
def read_multiple_csv(file_paths):
    dfs = []
    for file_path in file_paths:
        dfs.append(pd.read_csv(file_path))
    return dfs

# This function will load an image
def load_image(file_path):
    return np.array(Image.open(file_path).convert('L'))

# This function will load multiple images
def load_multiple_images(ref_df):
    labels = []
    images = []
    paths = []

    # to only load a subset of images
    # ref_df = ref_df.sample(n=100)
    for idx, row in tqdm(ref_df.iterrows(), total=ref_df.shape[0]):
        images.append(np.array(Image.open(row['path']).convert('L')))
        labels.append(row['label'])
        paths.append(row['path'])
    
    return images, labels, paths

# This function will load a neuroimaging data
def load_nii_data(file_path):
    mri = nib.load(file_path)

    # Extracting data from an MRI scan: .get_fdata()
    extracted_data = mri.get_fdata()
    return extracted_data

# This function will load multiple neuroimaging data
def load_multiple_nii_data(ref_df):
    images = []
    labels = []
    paths = []
    mri_images_data = []
    for idx, row in tqdm(ref_df.iterrows(), total=ref_df.shape[0]):
        # For neuroimaging data (e.g., MRI scans in NIFTI format), use nibabel
        mri = nib.load(row['path'])
        img = mri.get_fdata() 
        images.append(img)
        labels.append(row['label'])
        paths.append(row['path'])
        mri_images_data.append(img)
    return images, labels, paths

# This function will load the data
def load_data(ref_df, numbers='single'):

    if numbers == 'multi':
        file_format = ref_df['file_format']
        if (file_format == 'img').all():
            images, labels, paths = load_multiple_nii_data(ref_df)
            return images, labels, paths
        elif (file_format == 'jpg').all() or (file_format == 'png').all() or (file_format == 'jpeg').all():
            images, labels, paths = load_multiple_images(ref_df)
            return images, labels, paths
        elif (file_format == 'csv').all():
            images, labels, paths = read_multiple_csv(ref_df)
            return images, labels, paths
        else:
            return 'Invalid file format'
    
    else:
        # extract the file format from str as last 3 characters
        file_format = extract_file_format(ref_df)
        if (file_format == 'img'):
            return load_nii_data(ref_df)
        elif (file_format == 'jpg') or (file_format == 'png') or (file_format == 'jpeg'):
            return load_image(ref_df)
        elif (file_format == 'csv'):
            return read_csv(ref_df)
        else:
            return 'Invalid file format'