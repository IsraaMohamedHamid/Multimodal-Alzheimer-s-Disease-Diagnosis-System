# Multimodal Transformer Fusion for Alzheimer’s Disease Detection: Comparative Analysis of Image Modality Performance and Architectural Efficacy

## Overview
This project focuses on the use of multimodal transformer fusion techniques for the detection of Alzheimer's disease. It includes a comparative analysis of different image modalities and evaluates the efficacy of various architectural approaches.

This repository presents a comprehensive system for early detection of Alzheimer’s Disease using multimodal deep learning approaches. The project leverages MRI, CT, and PET neuroimaging data, applying advanced transformer-based fusion architectures to compare the efficacy of different image modalities and model designs. The workflow covers data preprocessing, model training, evaluation, and result visualization.

## Features
- Comparative analysis of image modality performance.
- Evaluation of different transformer architectures.
- Integration of multimodal data for improved detection accuracy.
- Detailed performance metrics and analysis.
- Multimodal fusion of MRI, CT, and PET scans for Alzheimer’s detection.
- Baseline CNN and advanced transformer-based models.
- Extensive data preprocessing and augmentation utilities.
- Automated result saving and visualization (classification reports, confusion matrices, ROC/PR curves).
- Modular scripts for data conversion, preprocessing, and statistics.

## Content
The project consists of a single document available in PDF format:
- **[Multimodal Alzheimer’s Disease Diagnosis System](Multimodal%20Alzheimer’s%20Disease%20Diagnosis%20System.pdf)**

## Project Structure

```
baseline-cnn-model-training.ipynb
multimodal-model.ipynb
multimodal-model-using-preload-numpy.ipynb
Multimodal Alzheimer’s Disease Diagnosis System.pdf
LICENSE
README.md
DataScript/
    convert_mri_to_image.ipynb
    convert_mri_to_image.py
    convert_to_128_shape.py
    create_data_folders.py
    display_images.py
    extract_slices.py
    get_data_stats.py
    get_patient_data.py
    load_and_read_data.py
    load_metadata.py
    match_up_and_move.ipynb
    match_up_and_move.py
    match_up.py
    move_and_delete_files_and_folders.py
    move_folders_from_one_path_to_another.ipynb
    move_folders_from_one_path_to_another.py
    neuroimaging_slices.py
    plot_charts_and_graphs.py
    preprocess_PET.ipynb
    ...
```

## Data Preparation

All data preparation and preprocessing steps are handled by scripts in the `DataScript` folder:

- **Conversion & Preprocessing:**
  - `convert_mri_to_image.py`: Converts MRI scans to image formats suitable for deep learning.
  - `convert_to_128_shape.py`: Resizes images to 128x128 pixels.
  - `preprocess_PET.ipynb`: Preprocesses PET scan data.
  - `extract_slices.py`: Extracts 2D slices from 3D neuroimaging data.

- **Data Organization:**
  - `create_data_folders.py`: Organizes images into class-based folders.
  - `move_and_delete_files_and_folders.py`: Manages file/folder movement and cleanup.
  - `move_folders_from_one_path_to_another.py`: Moves data folders as needed.
  - `match_up.py`, `match_up_and_move.py`: Ensures correct alignment of multimodal data for each patient.

- **Metadata & Statistics:**
  - `load_metadata.py`: Loads and parses metadata for patient scans.
  - `get_patient_data.py`: Retrieves patient-specific data.
  - `get_data_stats.py`: Computes statistics on the dataset (e.g., class distribution).
  - `display_images.py`: Visualizes sample images for inspection.
  - `plot_charts_and_graphs.py`: Generates visualizations for data analysis.

- **Loading Data:**
  - `load_and_read_data.py`: Loads images and labels into memory for model training.

## Model Training & Evaluation

- **Baseline Model:**
  - `baseline-cnn-model-training.ipynb`: Implements a baseline CNN (ResNet50) for single-modality (MRI) classification. Handles data loading, preprocessing, training, evaluation, and result visualization.

- **Multimodal Transformer Model:**
  - `multimodal-model.ipynb`: Main notebook for multimodal fusion using transformer architectures. Loads MRI, CT, and PET data, preprocesses and aligns them, and trains a transformer-based model for classification. Includes model validation and detailed evaluation (classification report, confusion matrix, ROC/PR curves, F1, MAE, MSE, log loss, MMCE).
  - `multimodal-model-using-preload-numpy.ipynb`: Variant that loads preprocessed numpy arrays for faster experimentation and training.

- **PDF Document:**
  - `Multimodal Alzheimer’s Disease Diagnosis System.pdf`: Contains the full write-up, methodology, results, and discussion.

## Scripts in DataScript

The `DataScript` folder contains all utility scripts for data handling. Use these scripts to:

1. Convert raw neuroimaging data to image files.
2. Resize, preprocess, and organize images into class folders.
3. Align multimodal data for each patient.
4. Extract slices and visualize data.
5. Compute statistics and generate plots for data exploration.

**Typical workflow:**
1. Use conversion scripts to process raw MRI/CT/PET data.
2. Organize data into folders using the provided scripts.
3. Run statistics and visualization scripts to inspect data quality.
4. Use the main notebooks for model training and evaluation.

## How to Use

1. Download the PDF file from the repository.
2. Open the document using any PDF reader.
3. Review the standards and guidelines outlined in the document.

**For code and experiments:**

1. **Prepare Data:**
   - Place your raw MRI, CT, and PET data in the appropriate folders.
   - Run scripts in `DataScript` to convert, preprocess, and organize the data.

2. **Train Models:**
   - For single-modality baseline: Open and run `baseline-cnn-model-training.ipynb`.
   - For multimodal fusion: Open and run `multimodal-model.ipynb` or `multimodal-model-using-preload-numpy.ipynb`.

3. **Evaluate Results:**
   - All results (classification reports, confusion matrices, ROC/PR curves, etc.) are saved in the results folder specified in the notebooks.

4. **Documentation:**
   - For a detailed explanation of the methodology and results, see the [Multimodal Alzheimer’s Disease Diagnosis System.pdf](Multimodal%20Alzheimer’s%20Disease%20Diagnosis%20System.pdf).

## Contributing
Contributions are welcome! You can:
- Provide feedback or suggest updates to the document.
- Share use cases or applications relevant to the project.
- Raise issues or discussions for additional topics.
- Suggest improvements to the code or documentation.
- Share new preprocessing or modeling techniques.
- Report issues or request new features.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact
For any questions or suggestions, please contact Israa Hassan Bashier at izzymohamed109@yahoo.com.