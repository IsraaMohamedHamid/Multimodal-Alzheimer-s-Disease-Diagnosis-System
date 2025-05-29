#################### IMPORTS ####################
# AS
import numpy as np
import nibabel as nib

#################### FUNCTIONS ####################

def get_orientation(affine):
    """
    Determines the orientation of the MRI scan based on the affine matrix.
    """
    # Identify the orientation by finding the axis with the largest absolute value in each row of the affine
    orientation = np.argmax(np.abs(affine[:3, :3]), axis=0)
    return orientation

def extract_slices(img_data, affine):
    """
    Extracts middle slices from the MRI data in axial, coronal, and sagittal orientations,
    adjusting based on the affine matrix.
    """
    orientation = get_orientation(affine)
    
    # Corrected approach to calculate slice_indices directly
    slice_indices = [img_data.shape[orientation[i]] // 2 for i in range(3)]
    
    # Extract slices based on determined orientation
    sagittal_slice = np.take(img_data, slice_indices[0], axis=orientation[0])
    coronal_slice = np.take(img_data, slice_indices[1], axis=orientation[1])
    axial_slice = np.take(img_data, slice_indices[2], axis=orientation[2])
    
    return sagittal_slice, coronal_slice, axial_slice


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


def guess_orientation_and_extract_slices(nii_path):
    nii_data = nib.load(nii_path)
    img_data = nii_data.get_fdata()

    # Guess orientations based on dimensions
    dimensions = img_data.shape
    # print(f"Dimensions: {dimensions}")
    sorted_dims = np.argsort(dimensions)  # Ascending order of dimensions
    # print(f"Sorted dimensions: {sorted_dims}")
    
    # Assuming the smallest dimension is Sagittal, next is Coronal, and largest is Axial
    sagittal_index, coronal_index, axial_index = sorted_dims
    # print(f"Sagittal index: {sagittal_index}, Coronal index: {coronal_index}, Axial index: {axial_index}")
    
    # Extract middle slices based on guessed orientation
    sagittal_slice = img_data.take(dimensions[sagittal_index] // 2, axis=sagittal_index)
    # print(f"Sagittal slice shape: {sagittal_slice.shape}")
    coronal_slice = img_data.take(dimensions[coronal_index] // 2, axis=coronal_index)
    # print(f"Coronal slice shape: {coronal_slice.shape}")
    axial_slice = img_data.take(dimensions[axial_index] // 2, axis=axial_index)
    # print(f"Axial slice shape: {axial_slice.shape}")
    
    return {'Sagittal': sagittal_slice, 'Coronal': coronal_slice, 'Axial': axial_slice}
