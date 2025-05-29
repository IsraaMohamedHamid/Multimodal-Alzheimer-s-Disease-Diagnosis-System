import matplotlib
import os
import sys

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

def find_highest_variance_time_points(img_data, num_points=5):
    """
    Identify time points with the highest variance in 4D PET scan data.

    Parameters:
    - img_data: 4D numpy array of the PET scan data.
    - num_points: Number of time points to select based on highest variance.

    Returns:
    - top_variance_time_points: Indices of time points with the highest variance.
    """
    variance_list = []
    for time_point in range(img_data.shape[-1]):
        time_point_data = img_data[..., time_point]
        variance_list.append(np.var(time_point_data))

    # Get indices of the top `num_points` variances
    top_variance_indices = np.argsort(variance_list)[-num_points:]

    # Sort the indices to maintain the temporal order
    top_variance_time_points = sorted(top_variance_indices)
    
    # Optionally, print the variance values for the selected time points
    # for idx in top_variance_time_points:
    #     print(f"Time point {idx} has variance: {variance_list[idx]}")

    return top_variance_time_points
def guess_orientation_and_extract_all_slices(img_data):

    # Guess orientations based on dimensions
    dimensions = img_data.shape
    sorted_dims = np.argsort(dimensions)  # Ascending order of dimensions
    
    # Assuming the smallest dimension is Sagittal, next is Coronal, and largest is Axial
    if len(sorted_dims) == 3:
        sagittal_index, coronal_index, axial_index = sorted_dims
    else:
        sagittal_index, coronal_index, axial_index, fourth_index = sorted_dims
    
    # Initialize dictionaries to hold all slices for each orientation
    sagittal_slices = {}
    coronal_slices = {}
    axial_slices = {}
    
    # Extract all slices for each orientation
    for i in range(dimensions[sagittal_index]):
        sagittal_slices[i] = img_data.take(i, axis=sagittal_index)
    for i in range(dimensions[coronal_index]):
        coronal_slices[i] = img_data.take(i, axis=coronal_index)
    for i in range(dimensions[axial_index]):
        axial_slices[i] = img_data.take(i, axis=axial_index)
    
    return {'Sagittal': sagittal_slices, 'Coronal': coronal_slices, 'Axial': axial_slices}
def extract_all_slices_optimized(img_data):
    """
    Optimized function to extract all slices from a 3D or 4D PET scan data in Sagittal, Coronal, and Axial orientations.

    Parameters:
    - img_data: 3D or 4D numpy array of the PET scan data.

    Returns:
    A dictionary containing all slices for Sagittal, Coronal, and Axial orientations.
    """
    # print(img_data.shape)
    # Guess orientations based on dimensions (excluding time if 4D)
    spatial_dimensions = img_data.shape[:-1] if img_data.ndim == 4 else img_data.shape
    # print(spatial_dimensions)
    sorted_dims = np.argsort(spatial_dimensions)  # Ascending order of dimensions
    
    # Assuming the smallest dimension is Sagittal, next is Coronal, and largest is Axial
    if len(spatial_dimensions) == 3:
        sagittal_index, coronal_index, axial_index = sorted_dims

    orientations = {}

    useful_time_points = find_highest_variance_time_points(img_data, 1) 
    # print(f"Useful time points: {useful_time_points}")
    
    for time_point in useful_time_points:

    # time_point = img_data.shape[-1] - 1

        # Extract slices for each orientation
        if img_data.ndim == 3:  # For 3D data
            orientations['Sagittal'] = img_data.swapaxes(0, sagittal_index)
            orientations['Coronal'] = img_data.swapaxes(0, coronal_index)
            orientations['Axial'] = img_data.swapaxes(0, axial_index)
        elif img_data.ndim == 4:  # For 4D data, selecting the first time point for simplicity
            orientations[f'Sagittal_time_point_{time_point}'] = img_data[:,:,:,time_point].swapaxes(0, sagittal_index)
            orientations[f'Coronal_time_point_{time_point}'] = img_data[:,:,:,time_point].swapaxes(0, coronal_index)
            orientations[f'Axial_time_point{time_point}'] = img_data[:,:,:,time_point].swapaxes(0, axial_index)

    return orientations
def get_slice_range(scan, tracer):
    """
    Determine the ideal range of slices to analyze based on the tracer used.
    """
    num_slices = scan # scan.shape[2]

    # print(f"Number of slices: {num_slices}")
    
    if tracer.lower() == 'av45' or tracer.lower() == 'pib':
        # Middle to upper slices for cortical amyloid plaques
        start_slice = int(num_slices * 0.2) # 0.4
        end_slice = int(num_slices * 0.9) # 0.7
    elif tracer.lower() == 'fdg':
        # Broad range for hypometabolism in Alzheimer's
        start_slice = int(num_slices * 0.3)
        end_slice = int(num_slices * 0.8)
    else:
        raise ValueError("Unknown tracer. Please use 'AV45', 'PIB', or 'FDG'.")
        
    return start_slice, end_slice
def extract_and_select_slices(img_data, tracer):
    """
    Extract slices for Sagittal, Coronal, and Axial orientations and select a range based on the tracer type.
    """
    
    # Extract slices for each orientation
    orientations = extract_all_slices_optimized(img_data)

    selected_axial_slices_dictionary = {}
    
    # Assuming axial orientation is of interest
    for key, value in orientations.items():
        # print(key, value.shape)
        if 'Axial' in key:
            axial_slices = orientations[key]
            # print(axial_slices.shape)
            num_axial_slices = axial_slices.shape[-1] if img_data.ndim == 4 else axial_slices.shape[2]
            
            # Get start and end slice based on tracer
            start_slice, end_slice = get_slice_range(num_axial_slices, tracer)
            
            # Select the slice range for axial orientation
            selected_axial_slices = axial_slices[:, :, start_slice:end_slice+1]

            # save in selected_axial_slices_dictionary
            selected_axial_slices_dictionary[key] = selected_axial_slices
    
    return selected_axial_slices_dictionary
def display_selected_slices(selected_axial_slices, filename, key, output_base_directory):
    """
    Display the selected axial slices.
    """
    # print(selected_axial_slices.shape)
    num_slices = selected_axial_slices.shape[2]
    cols = 5  # Number of columns in the plot grid
    rows = num_slices // cols + (1 if num_slices % cols else 0)  # Calculate rows needed

    # fig, axs = plt.subplots(rows, cols, figsize=(20, 4 * rows))
    # axs = axs.flatten()

    for i in range(num_slices):
        plt.figure(figsize=(20, 15))
        plt.imshow(selected_axial_slices[:, :, i].T, cmap='hot', origin='lower')
        plt.axis('off')
        plt.title(f'{key} Slice {i}', fontsize=16)
        plt.tight_layout()
        # plt.show()
        plt.savefig(f"{output_base_directory}/Slice_{i}_{filename}_{key}.png")
        plt.close()
def return_tracer(file_path):
    """
    Return the tracer used in the PET scan based on the file name.
    """
    file_name = os.path.basename(file_path)
    
    if 'av45' in file_name.lower():
        return 'AV45'
    elif 'pib' in file_name.lower():
        return 'PIB'
    elif 'fdg' in file_name.lower():
        return 'FDG'
    else:
        raise ValueError("Unknown tracer. Please use 'AV45', 'PIB', or 'FDG'.")
                
    
def main(root_directory_path):

    # Example usage
    original_directory_path = root_directory_path + "/Original"
    processed_directory_path = root_directory_path + "/Processed"

    os.makedirs(processed_directory_path, exist_ok=True)

    # %matplotlib inline
    matplotlib.use('Agg')

    completed_files_count = 0  # Initialize the counter

    # get length of files that end with .nii.gz
    scan_length = 0
    for root, dirs, files in os.walk(original_directory_path):
        for file in files:
            if file.endswith(".nii.gz"):
                scan_length += 1

    for root, dirs, files in os.walk(original_directory_path):
        for file in files:
            if file.endswith(".nii.gz"):
                nii_gz_file_path = os.path.join(root, file)
                img_data = nib.load(nii_gz_file_path).get_fdata()
                result = extract_and_select_slices(img_data, return_tracer(nii_gz_file_path))
                for key, value in result.items():
                    # print(key, value.shape)
                    display_selected_slices(value, file, key, processed_directory_path)
                
                completed_files_count += 1  # Increment the counter after processing each file
                print(f"Completed: {completed_files_count}/{scan_length} - {file}")

    print(f"Total files processed: {completed_files_count}")


if __name__ == "__main__":
    root_directory_path = sys.argv[1]
    main(root_directory_path)           