import numpy as np
from PIL import Image, UnidentifiedImageError
import os
import sys
import shutil
# Define the main directory where the original images are located and the results directory

root_dir = sys.argv[1]
main_dir = root_dir + "/Original/"
results_dir = root_dir + "/RESULTS/"
categories = {
    "non-demented" : 0,
        "very-mild-dementia" : 1,
        "mild-dementia" : 2,
        "moderate-dementia" : 3,
        "unknown" : 4,
}
data = []
result = []


# Assuming 'categories' is a dictionary that holds categories as keys and labels as values
for category, label in categories.items():
    print(f"Processing category: {category}")

    # Construct paths for the current category in both main and results directories
    category_main_dir = os.path.join(main_dir, category)
    category_results_dir = os.path.join(results_dir, category)

    # Create the category directory in the results folder if it doesn't exist
    os.makedirs(category_results_dir, exist_ok=True)

    # Get a list of all image files in the category's main directory
    image_paths = [os.path.join(category_main_dir, f) for f in os.listdir(category_main_dir) if os.path.isfile(os.path.join(category_main_dir, f))]
    total_paths = len(image_paths)
    processed_paths = 0

    for path in image_paths:
        try:
            # Open and resize the image
            img = Image.open(path)
            img = img.resize((128, 128))

            # Construct the corresponding results path for the resized image
            relative_path = os.path.relpath(path, main_dir)  # Get the relative path from the main directory
            results_path = os.path.join(results_dir, relative_path)  # Construct the results path

            # Save the resized image in the results directory
            img.save(results_path)

            # Update your data and result lists, assuming you need to keep the resized images in memory
            img_array = np.array(img)[:,:,:3]
            # data.append(img_array)
            # result.append(label)

            processed_paths += 1
            print(f"Processed {processed_paths}/{total_paths} images in category '{category}'")

        except UnidentifiedImageError:
            print(f"Unable to identify image file: {path}")
        except Exception as e:
            print(f"An error occurred while processing {path}: {e}")

    print(f"Completed processing category: {category}")
