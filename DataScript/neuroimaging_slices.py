
#################### IMPORTS ####################
# ALL
import os
import sys
import pathlib
import multiprocessing
import traceback
# Append the parent folder to the python path 
# Get the current notebook's path
notebook_path = os.path.join(os.path.dirname(os.path.abspath('convert_mri_to_image.ipynb')))

# Append the parent directory of the current notebook's directory to the path
sys.path.append(str(pathlib.Path(notebook_path).parent.resolve()))

# AS
import nibabel as nib
import matplotlib.pyplot as plt

# FROM
from functools import partial
from pathlib import Path

# FROM .py SCRIPT
from DataScript.display_images import *
from DataScript.extract_slices import *
from DataScript.get_data_stats import *
from DataScript.get_patient_data import *
from DataScript.load_and_read_data import *
from DataScript.load_metadata import *

#################### FUNCTIONS ####################

# This function is used to load the data from the given path.
def extract_slice_index(file):
    """Extract the slice index from the given file."""
    # remove the extension
    return file.split("_")[3].split("-")[1]

def convert_nueoimaging_to_images(original_data_path, preprocessed_data_path, ref_df):
    print('start')
    extensions = ['.img', '.hdr', '.nii.gz']
    filename_list = []
    file_path_list = []
    combined_dict = {}
    completed = 0

    for ext in extensions:
        filenames, files = load_files_with_extension(original_data_path, ext)  

        for filename, file_path in zip(filenames, files):
            file_path_list.append(file_path)
            combined_dict.setdefault(filename, []).append(file_path)

    # print(f"Combined dict: {combined_dict.values()}")

    # Compare missing files
    compare_missing_files_in_ref_df(ref_df, file_path_list)

    # Covert into batch download

    with multiprocessing.Pool() as pool:
        process_func = partial(process_file, ref_df=ref_df, preprocessed_data_path=preprocessed_data_path)
        completed_files = pool.imap(process_func, combined_dict.items())
        for i, filename in enumerate(completed_files, 1):
            print(f"Complete: {i}/{len(combined_dict)} - {filename}")

    print('end')

def load_nii_file(file_paths):
    if len(file_paths) == 2:  # .img and .hdr scenario
        return nib.Nifti1Image(nib.load(file_paths[0]).get_fdata(), None, header=nib.load(file_paths[1]).header)
    elif len(file_paths) == 1:  # .nii.gz scenario
        return nib.load(file_paths[0])
    else:
        raise ValueError("Unexpected number of files for a single dataset.")

def process_file(file_data, ref_df, preprocessed_data_path):
    filename, file_paths = file_data
    label = ref_df[ref_df['file_name_wout_format'] == filename]['label'].iloc[0] if not ref_df[ref_df['file_name_wout_format'] == filename].empty else "unknown"

    # Check if there are files inside the preprocessed_data_path, If it is, skip it
    if os.path.exists(preprocessed_data_path):
        for root, dirs, files in os.walk(preprocessed_data_path):
            for file in files:
                if filename in file:
                    # print(f"File {filename} already processed, skipping...")
                    return filename

    try:
        nii_data = load_nii_file(file_paths)
        img_data = nii_data.get_fdata()
        # print(f"Processing {filename}...")
        slices = guess_orientation_and_extract_all_slices(img_data)
        save_single_slice(filename, slices, preprocessed_data_path, label)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
    return filename

# def save_slice_image(file_name, img_data, start_slice, end_slice, output_directory, label):
#     """
#     Save specified slices of the image data as PNG files in the output directory.
#     """
#     # Ensure the output directory exists
#     output_path = os.path.join(output_directory, label)
#     os.makedirs(output_path, exist_ok=True)
    
#     # Loop through the specified range of slices
#     for slice_index in range(start_slice, min(end_slice, img_data.shape[1])):
#         # Define the filename for the slice image
#         filename = f"{file_name}_slice_{slice_index}_axial_img.png"
#         file_path = os.path.join(output_path, filename)

#         # Create a new figure and axis for plotting
#         fig, ax = plt.subplots()
#         ax.axis('off')  # Turn off axis
#         ax.imshow(img_data[:, slice_index, :], cmap='gray')  # Adjust as necessary for orientation

#         # Save the figure
#         fig.savefig(file_path, bbox_inches='tight', pad_inches=0)
#         plt.close(fig)  # Close the figure to free memory

def save_single_slice(file_name, slices, output_directory, label):
    """
    Saves slices of MRI data as PNG images in specific orientation folders.

    Parameters:
    - file_name: Base name for the output files.
    - slices: Dictionary of slices for each orientation.
    - output_directory: The base directory to save the images.
    - label: Label for the subdirectory structure.
    """

    # Define the output base Path object for clarity and ease of use
    output_base_path = Path(output_directory)

    # Iterate over each orientation to save the slices
    for orientation, slice_list in slices.items():
        # Calculate start and end slices based on orientation
        start_slice, end_slice = determine_slice_range(orientation, slice_list)

        # Define the full path for the current orientation and ensure it exists
        orientation_path = output_base_path / label / orientation
        orientation_path.mkdir(parents=True, exist_ok=True)

        # Iterate through the specified range of slices and save each as an image
        for slice_index in range(start_slice, end_slice):
            if slice_index in slice_list:
                slice_img = slice_list[slice_index]
                save_slice_as_image(orientation_path, file_name, slice_index, orientation, slice_img)
            else:
                print(f"Slice index {slice_index} not found in {orientation} slices. Length: {len(slice_list)}")

def determine_slice_range(orientation, slice_list):
    """
    Determines the start and end slice indices based on the orientation and available slices.
    """
    if orientation == 'Sagittal':
        start_slice = len(slice_list) // 4
        end_slice = len(slice_list) - start_slice
    else:
        start_slice = 100
        end_slice = min(161, len(slice_list))
    return start_slice, end_slice

def save_slice_as_image(orientation_path, file_name, slice_index, orientation, slice_img):
    """
    Saves a single slice image to the specified orientation folder.
    """
    filename = f"Slice_{slice_index}_{file_name}_{orientation.lower()}_img.png"
    file_path = orientation_path / filename
    fig, ax = plt.subplots()
    ax.imshow(slice_img.T, cmap='gray', origin='lower')
    ax.axis('off')
    fig.savefig(file_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)





# #################### IMPORTS ####################
# # ALL
# import os
# import re
# import json
# import sys
# import pathlib
# import matplotlib
# import multiprocessing
# import traceback
# # Append the parent folder to the python path 
# # Get the current notebook's path
# notebook_path = os.path.join(os.path.dirname(os.path.abspath('convert_mri_to_image.ipynb')))

# # Append the parent directory of the current notebook's directory to the path
# sys.path.append(str(pathlib.Path(notebook_path).parent.resolve()))

# # AS
# import nibabel as nib
# import matplotlib.pyplot as plt

# # FROM
# from functools import partial

# # FROM .py SCRIPT
# from DataScript.display_images import *
# from DataScript.extract_slices import *
# from DataScript.get_data_stats import *
# from DataScript.get_patient_data import *
# from DataScript.load_and_read_data import *
# from DataScript.load_metadata import *

# #################### FUNCTIONS ####################

# # This function is used to load the data from the given path.
# def extract_slice_index(file):
#     """Extract the slice index from the given file."""
#     # remove the extension
#     return file.split("_")[3].split("-")[1]

# def convert_nueoimaging_to_images(original_data_path, preprocessed_data_path, ref_df):
#     print('start')
#     extensions = ['.img', '.hdr', '.nii.gz']
#     filename_list = []
#     file_path_list = []
#     combined_dict = {}
#     completed = 0

#     for ext in extensions:
#         filenames, files = load_files_with_extension(original_data_path, ext)  

#         for filename, file_path in zip(filenames, files):
#             file_path_list.append(file_path)
#             combined_dict.setdefault(filename, []).append(file_path)

#     # print(f"Combined dict: {combined_dict.values()}")

#     # Compare missing files
#     compare_missing_files_in_ref_df(ref_df, file_path_list)

#     first_100_items = list(combined_dict.items())[:100]

#     # Covert into batch download

#     with multiprocessing.Pool() as pool:
#         process_func = partial(process_file, ref_df=ref_df, preprocessed_data_path=preprocessed_data_path)
#         completed_files = pool.map(process_func, combined_dict.items())

#     for i, filename in enumerate(completed_files, 1):
#         print(f"Complete: {i}/{len(completed_files)} - {filename}")

#     # for filename, file_paths in combined_dict.items():
#     #     label = ref_df[ref_df['file_name_wout_format'] == filename]['label'].values[0] if not ref_df[ref_df['file_name_wout_format'] == filename].empty else "unknown"

#     #     # Assume all relevant files have been paired properly; for .nii.gz or unpaired, it's just one file
#     #     if len(file_paths) == 2:  # .img and .hdr scenario
#     #         img_path, hdr_path = file_paths
#     #         nii_data = nib.Nifti1Image(nib.load(img_path).get_fdata(), None, header=nib.load(hdr_path).header)
#     #     elif len(file_paths) == 1:  # .nii.gz scenario
#     #         nii_data = nib.load(file_paths[0])
#     #     else:
#     #         continue

#     #     img_data = nii_data.get_fdata()
        
#     #     # Example slice indices
#     #     slices = guess_orientation_and_extract_all_slices(img_data)

#     #     # Save the slices as images
#     #     save_single_slice(filename, img_data, slices, preprocessed_data_path, label)
#     #     # save_slice_image(oasis_dataset_number, filename, img_data, start_slice, end_slice, preprocessed_data_path, label)

#     #     completed += 1

#     #     # Show how many files are complete
#     #     print(f"Complete: {completed}/{len(first_100_items)} - {filename}")

#     print('end')

# def process_file(file_data, ref_df, preprocessed_data_path):
#     filename, file_paths = file_data
#     label = ref_df[ref_df['file_name_wout_format'] == filename]['label'].values[0] if not ref_df[ref_df['file_name_wout_format'] == filename].empty else "unknown"

#     if len(file_paths) == 2:  # .img and .hdr scenario
#         img_path, hdr_path = file_paths
#         nii_data = nib.Nifti1Image(nib.load(img_path).get_fdata(), None, header=nib.load(hdr_path).header)
#     elif len(file_paths) == 1:  # .nii.gz scenario
#         nii_data = nib.load(file_paths[0])
#     else:
#         return

#     # Check if there are files inside the preprocessed_data_path
#     # If there are check if the file is already processed
#     # check by seeing if "filename" in filename of the file inside preprocessed_data_path
#     # If it is, skip it
#     # If it's not, process it
#     if os.path.exists(preprocessed_data_path):
#         for root, dirs, files in os.walk(preprocessed_data_path):
#             for file in files:
#                 if filename in file:
#                     print(f"File {filename} already processed, skipping...")
#                     return filename

#     img_data = nii_data.get_fdata()
#     slices = guess_orientation_and_extract_all_slices(img_data)
#     try:
#         save_single_slice(filename, img_data, slices, preprocessed_data_path, label)
#         print(f"Complete: {filename}")
#     except TypeError as e:
#         print(f"Image shape: {img_data.shape} - Slice indices for {filename} are invalid image size.")
#         print(f"Skipping {filename} due to error: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred while processing {filename}: {e}")
#         traceback.print_exc()

#     return filename

# # This fucntion will save a slice of the image data as a PNG file in the output directory
# # This adjustment is optional and might be necessary if you're running this in a headless environment

# def save_slice_image_v(oasis_dataset_number, file_name, img_data, start_slice, end_slice, output_directory, label):
#     """ Save specified slices of the image data as PNG files in the output directory. """
#     if start_slice < img_data.shape[1] and end_slice < img_data.shape[1]:
#         for slice_index in range(start_slice, end_slice):

#             # Create a new figure and axis for plotting
#             fig, ax = plt.subplots()
#             ax.axis('off')  # Turn off axis

#             for folder_name in ['Axial', 'Coronal', 'Sagittal']:
#                 # Define the filename for the slice image
#                 filename = f"{file_name}_slice_{slice_index}_{folder_name}_img.png"
#                 file_path = os.path.join(os.path.join(output_directory, folder_name, label), filename)

#                 if folder_name == 'Axial':
#                     if oasis_dataset_number == 1 or oasis_dataset_number == 2:
#                         ax.imshow(img_data[:, slice_index, :], cmap='gray')  # Adjust as necessary for orientation
#                     elif oasis_dataset_number == 3:
#                         ax.imshow(img_data[:, :, slice_index], cmap='gray')  # Adjust as necessary for orientation
#                     elif oasis_dataset_number == 4:
#                         ax.imshow(img_data[:, :, slice_index], cmap='gray')  # Adjust as necessary for orientation
#                     else:
#                         print(f"Invalid dataset number: {oasis_dataset_number}")
#                         return
#                 elif folder_name == 'Coronal':
#                     return
#                 elif folder_name == 'Sagittal':
#                     return
            

#             # Save the figure
#             fig.savefig(file_path, bbox_inches='tight', pad_inches=0)
#             plt.close(fig)  # Close the figure to free memory
#     else:
#         print(f"Slice indices for {file_name} are out of bounds.")
#         print(f"Image shape: {img_data.shape}")


# # def save_slice_image(file_name, img_data, start_slice, end_slice, output_directory, label):
# #     """
# #     Save specified slices of the image data as PNG files in the output directory.
# #     """
# #     # Ensure the output directory exists
# #     output_path = os.path.join(output_directory, label)
# #     os.makedirs(output_path, exist_ok=True)
    
# #     # Loop through the specified range of slices
# #     for slice_index in range(start_slice, min(end_slice, img_data.shape[1])):
# #         # Define the filename for the slice image
# #         filename = f"{file_name}_slice_{slice_index}_axial_img.png"
# #         file_path = os.path.join(output_path, filename)

# #         # Create a new figure and axis for plotting
# #         fig, ax = plt.subplots()
# #         ax.axis('off')  # Turn off axis
# #         ax.imshow(img_data[:, slice_index, :], cmap='gray')  # Adjust as necessary for orientation

# #         # Save the figure
# #         fig.savefig(file_path, bbox_inches='tight', pad_inches=0)
# #         plt.close(fig)  # Close the figure to free memory

# def save_single_slice(file_name, img_data, slices, output_directory, label):
#     """
#     Saves slices of MRI data as PNG images in specific orientation folders.

#     :param file_name: Base name for the output files.
#     :param img_data: The 3D MRI data array (not used in this modified function but kept for compatibility).
#     :param slices: Dictionary of slices for each orientation.
#     :param output_directory: The base directory to save the images.
#     :param label: Label for the subdirectory structure.
#     """
    
#     for folder_name in ['Axial', 'Coronal', 'Sagittal']: #
#         # print(f"-------------------------------------------------- Folder name: {folder_name} --------------------------------------------------")
        
#         # Set start and end slice indices
#         if folder_name == 'Sagittal':
#             start_slice = len(slices[folder_name]) // 4
#             end_slice = len(slices[folder_name]) - start_slice
#         else:
#             start_slice = 100
#             end_slice = 161

#         if start_slice < img_data.shape[1] and end_slice < img_data.shape[1]:
#             for slice_index in range(start_slice, end_slice):
#                 if slice_index in slices[folder_name]:
#                     # Create a new figure and axis for plotting
#                     fig, ax = plt.subplots()
#                     ax.axis('off')  # Turn off axis
                    
#                     # Define the filename for the slice image
#                     # Slice_144_OAS1_0002_MR1_axial_img_2_anon.png
#                     filename = f"Slice_{slice_index}_{file_name}_{folder_name.lower()}_img.png"
#                     file_path = os.path.join(output_directory, folder_name, label, filename)

#                     # Ensure the output directory exists
#                     os.makedirs(os.path.dirname(file_path), exist_ok=True)

#                     # Get the current slice based on orientation and index
#                     slice_img = slices[folder_name][slice_index]
                    
#                     # Plot and save the slice image
#                     ax.imshow(slice_img.T, cmap='gray', origin='lower')  # Adjust as necessary for orientation
#                     fig.savefig(file_path, bbox_inches='tight', pad_inches=0)
#                     plt.close(fig)

#                     # print(f"Saved {folder_name} slice {slice_index} to {file_path}")
#                 else:
#                     print(f"Slice index {slice_index} not found in {folder_name} slices. Length: {len(slices[folder_name])}")

#         else:
#             print(f"Image shape: {img_data.shape} - Slice indices for {file_name} are out of bounds.")
