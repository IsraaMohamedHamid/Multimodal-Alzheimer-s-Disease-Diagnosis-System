#################### IMPORTS ####################
# AS
import numpy as np
import pandas as pd

# FROM
from scipy.stats import skew
from tqdm import tqdm

#################### FUNCTIONS ####################

# This function will get image stats: mean, std, width, height, skewness
'''
The following statistics were extracted:

* **mean:** Mean pixel value of each image.
* **std:** Standard deviation of pixel values in each image.
* **width:** Width of each image.
* **height:** Height of each image.
* **skew:** Skewness of the histogram of pixel values in each image.
'''
def get_image_stats(images, labels, paths):
    means, stds, widths, heights = [], [], [], []
    skewnesses = []
    
    for image in tqdm(images):
        means.append(np.mean(image))
        stds.append(np.std(image))
        widths.append(image.shape[0])
        heights.append(image.shape[1])
        image_hist = np.histogram(image.flatten())[0]
        skewnesses.append(skew(image_hist))
    
    image_stats = pd.DataFrame({
        'mean': means,
        'std': stds,
        'width': widths,
        'height': heights,
        'skew': skewnesses
    })
    
    image_stats['label'] = labels
    image_stats['path'] = paths
    return image_stats

# This function will get neuroimaging data stats: mean, std, skewness
def get_nii_data_stats(images, labels, paths):
    means, stds, skewnesses = [], [], []
    
    for image in tqdm(images):
        means.append(np.mean(image))
        stds.append(np.std(image))
        image_hist = np.histogram(image.flatten())[0]
        skewnesses.append(skew(image_hist))
    
    nii_data_stats = pd.DataFrame({
        'mean': means,
        'std': stds,
        'skew': skewnesses
    })
    
    nii_data_stats['label'] = labels
    nii_data_stats['path'] = paths
    return nii_data_stats