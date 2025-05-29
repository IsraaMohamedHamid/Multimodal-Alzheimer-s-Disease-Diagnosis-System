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

# FROM .py SCRIPT
from DataScript.extract_slices import *

#################### FUNCTIONS ####################

# Function to display images with text indicating the category
def display_images_with_text(file_paths, category_name, endings=['150', '151', '152']):
    plt.figure(figsize=(15, 5))
    plt.suptitle(f"Images from {category_name}", fontsize=16)

    for ending in endings:
        matching_files = [img for img in file_paths if img.endswith(ending + '.jpg')]
        for i in range(min(3, len(matching_files))):
            img_path = matching_files[i]
            img = Image.open(img_path)
            plt.subplot(1, 3, i + 1)
            plt.imshow(img)
            plt.axis('off')
            
            # Add text indicating the category
            plt.text(0, -10, f"{category_name.split()[0]} {i + 1}", color='white', fontsize=12, weight='bold', ha='left', va='bottom', bbox=dict(facecolor='black', alpha=0.7))

    plt.show()

def display_slice_images(img_data, cmap='gray', title='MRI Slices'):
    """
    Display the MRI slices for the given image data
    Args:
    img_data (3D numpy array): Image data
    cmap (str): Color map for displaying the image
    title (str): Title of the plot
    """
    # Calculate the middle slice index for each orientation
    sagittal_middle = img_data.shape[0] // 2
    coronal_middle = img_data.shape[1] // 2
    axial_middle = img_data.shape[2] // 2

    # Extract the middle slice for each orientation
    sagittal_slice = img_data[sagittal_middle, :, :]
    coronal_slice = img_data[:, coronal_middle, :]
    axial_slice = img_data[:, :, axial_middle]

    # Plotting the slices
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(sagittal_slice.T, cmap=cmap, origin='lower')
    axes[0].set_title('Sagittal Slice')
    axes[1].imshow(coronal_slice.T, cmap=cmap, origin='lower')
    axes[1].set_title('Coronal Slice')
    axes[2].imshow(axial_slice.T, cmap=cmap, origin='lower')
    axes[2].set_title('Axial Slice')

    for ax in axes:
        ax.axis('off')

    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.show()

def display_sample_slice_images(ref_df, cmap='gray', title='MRI Slices'):
    """
    Display the MRI slices for the given image data
    Args:
    img_data (3D numpy array): Image data
    cmap (str): Color map for displaying the image
    title (str): Title of the plot
    """

    samples = ref_df.sample(20)
    sample_path_list = samples["path"]

    for sample_path in sample_path_list:
        # Title should be the "file_name_wout_format" column from sample
        title = samples[samples["path"] == sample_path]["file_name_wout_format"].values[0]

        # Load the NIfTI file
        nii_data = nib.load(sample_path)
        img_data = nii_data.get_fdata()

        # Calculate the middle slice index for each orientation
        sagittal_middle = img_data.shape[0] // 2
        coronal_middle = img_data.shape[1] // 2
        axial_middle = img_data.shape[2] // 2

        # Extract the middle slice for each orientation
        sagittal_slice = img_data[sagittal_middle, :, :]
        coronal_slice = img_data[:, coronal_middle, :]
        axial_slice = img_data[:, :, axial_middle]

        # Plotting the slices
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(sagittal_slice.T, cmap=cmap, origin='lower')
        axes[0].set_title('Sagittal Slice')
        axes[1].imshow(coronal_slice.T, cmap=cmap, origin='lower')
        axes[1].set_title('Coronal Slice')
        axes[2].imshow(axial_slice.T, cmap=cmap, origin='lower')
        axes[2].set_title('Axial Slice')

        for ax in axes:
            ax.axis('off')

        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        plt.show()

def display_slices_according_to_type(sagittal, coronal, axial, img_title='Slices'):
    """
    Displays the extracted sagittal, coronal, and axial slices.

    :param sagittal: The sagittal slice to be displayed.
    :param coronal: The coronal slice to be displayed.
    :param axial: The axial slice to be displayed.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    titles = ['Sagittal Slice', 'Coronal Slice', 'Axial Slice']
    slices = [sagittal, coronal, axial]
    
    for ax, slice, title in zip(axes, slices, titles):
        ax.imshow(slice.T, cmap='gray', origin='lower')  # Adjust as necessary for orientation
        ax.set_title(f"{title}")
        ax.axis('off')

    fig.suptitle(img_title)
    plt.tight_layout()
    plt.show()

def display_slices(slices, title='Slices'):
    fig, axes = plt.subplots(1, len(slices), figsize=(15, 5))
    for i, (orientation, slice) in enumerate(slices.items()):
        axes[i].imshow(slice.T, cmap='gray', origin='lower')
        axes[i].set_title(f'{orientation} Slice')
        axes[i].axis('off')
    plt.title(title)
    plt.tight_layout()
    plt.show()

def display_single_slice(slice_img, title="Slice"):
    """
    Displays a single slice.

    :param slice_img: The slice image to display.
    :param title: Title for the plot.
    """
    plt.figure(figsize=(5, 5))
    plt.imshow(slice_img.T, cmap='gray', origin='lower')  # Adjust as necessary for orientation
    plt.title(title)
    plt.axis('off')
    plt.show()

def display_all_three_slice(sagittal, coronal, axial, title="Slice"):
    """
    Displays a single slice.

    :param slice_img: The slice image to display.
    :param title: Title for the plot.
    """
    plt.figure(figsize=(5, 5))
    plt.imshow(sagittal.T, cmap='gray', origin='lower')  # Adjust as necessary for orientation
    plt.title(title)
    plt.axis('off')
    plt.show()