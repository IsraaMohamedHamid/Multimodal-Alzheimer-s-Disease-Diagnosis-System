# ALL
import shutil
import os
import sys
import pathlib
import re

# AS
import pandas as pd
# Mapping of CDR numerical values to labels
cdr_mapping = {
    0: "non-demented",
    0.5: "very-mild-dementia",
    1: "mild-dementia",
    2: "moderate-dementia",
    "": "unknown"  # Add a new category
    }

def get_cdr_label(cdr_value):

    # Convert the CDR value to a label using the mapping
    # Use the get method to handle cases where cdr_value is not in cdr_mapping
    return cdr_mapping.get(cdr_value, 'unknown')

# This function will return the file path
def find_file_paths(root_folder, filename):
    """
    Finds paths to a file within the root folder.

    :param root_folder: The root directory to search in.
    :param filename: The name of the file to search for.
    :return: A list of full paths to files matching the filename within the root folder.
    """
    matching_paths = []

    # Walk through all directories and files in root_folder
    for root, dirs, files in os.walk(root_folder):
        if filename in files:
            # If the filename matches, append the full path to the list
            full_path = os.path.join(root, filename)
            matching_paths.append(full_path)

    return matching_paths
# This function is used to create the categories folders.
def create_categories_folders(preprocessed_data_path):
    
    # Define the paths for the different dementia levels
    categories_file_paths = [os.path.join(preprocessed_data_path, category) for category in cdr_mapping.values()]

    # Check if the directories exist, if not create them.
    for category, category_path in zip(cdr_mapping.values(), categories_file_paths):
        if not os.path.exists(category_path):
            os.makedirs(category_path)
            print(f"Created folder: {category_path}")
        else:
            print(f"Folder already exists: {category_path}")
def find_closest_match_using_upper_lower_bounds(list1_subject, list1_day, list2, lower_bound, upper_bound):
    
    # Calculate the absolute day difference between the current scan_session_day row and all rows in clinical_assesment_day with the same subject
    subject_matches = list2[list2['OASISID'] == list1_subject]
    
    if not subject_matches.empty:
        differences = subject_matches['Day'].sub(list1_day).abs()
        closest_idx = differences.idxmin()  # Get the index of the closest match

        # Filter for entries within the specified bounds
        bounded_matches = subject_matches[(subject_matches['Day'] >= list1_day - lower_bound) & 
                                        (subject_matches['Day'] <= list1_day + upper_bound)]
        
        # Find the closest day within bounds
        if not bounded_matches.empty:
            closest_match = bounded_matches.loc[closest_idx]
            return closest_match["CLINICALDATAID"]
        else:
            return None
    return None
def find_closest_match_using_nearest_distance(list1_subject, list1_day, list2):
    # Ensure list2 is a DataFrame to avoid AttributeError in case it's not.
    if not isinstance(list2, pd.DataFrame):
        raise ValueError("list2 must be a pandas DataFrame")
    
    # Find matches for the subject
    subject_matches = list2[list2['OASISID'] == list1_subject].copy()
    
    if not subject_matches.empty:
            
        # Calculate the absolute day difference
        subject_matches['Day_diff'] = (subject_matches['Day'] - list1_day).abs()
        
        # Find the index of the closest match
        closest_idx = subject_matches['Day_diff'].idxmin()
        
        # Retrieve the closest match based on the index
        closest_match = subject_matches.loc[closest_idx]
        
        return closest_match["CLINICALDATAID"]
    else:
        # Handle the case where there are no matches
        return None

def matching_up_the_data_upper_lower_full(scan_session_day, clinical_assessment_day, lower_bound, upper_bound):
    # Extract 'Day' from 'CLINICALDATAID'
    clinical_assessment_day['Day'] = clinical_assessment_day['CLINICALDATAID'].str.extract(r'(d\d{4})', expand=False).str.strip().apply(
        lambda x: int(x[1:]) if isinstance(x, str) else 0)

    print(f"scan_session_day: {len(scan_session_day)} | clinical_assessment_day: {len(clinical_assessment_day)}")

    # Filter scan sessions to include only those with matching 'OASISID'
    scan_session_day = scan_session_day[scan_session_day['OASISID'].isin(clinical_assessment_day['OASISID'])]

    for index, row in clinical_assessment_day.iterrows():
        mask = (scan_session_day['OASISID'] == row['OASISID']) & ((scan_session_day['Day'] <= row['Day'] + upper_bound) & (scan_session_day['Day'] >= row['Day'] - lower_bound))
        
        if not mask.any():
            # If no direct match found within bounds, find the closest match
            closest_day_id = find_closest_match_using_nearest_distance(row['OASISID'], row['Day'], scan_session_day)
            if closest_day_id is not None:
                # Extract the day number from CLINICALDATAID of the closest match
                closest_day = int(closest_day_id.split("_")[-1][1:]) if isinstance(closest_day_id, str) else 0
                mask = (scan_session_day['OASISID'] == row['OASISID']) & (scan_session_day['Day'] == closest_day)

        # Update scan_session_day with clinical assessment data
        for name in row.index:
            scan_session_day.loc[mask, f"{name}_clinical_assessment"] = row[name]

    return scan_session_day

# Extract patient ID and MR ID based on the dataset
def extract_ids(file, file_full_path, cdr_dfs):
    # print(f"File: {file} | File Full Path: {file_full_path}")

    day_match = re.search(r'd(\d{4})', file)
    
    patient_id, mr_id, slice_id, slice_type, OASISID, mr_type, img_id, day, run_id, dataset_marker, clinical_data_id = None, None, None, None, None, None, None, None, None, None, None
    
    if 'OAS1' in file:
        dataset_marker = 'OAS1'
        patient_id = file.split('_')[3]
        slice_id = file.split('_')[1]
        slice_type = "Axial"
        mr = file.split('_')[4]
        OASISID = f'OAS1_{patient_id}_{mr}'
        modaltiy = file_full_path.split('/')[5]
        # OAS1_0001_MR1
        clinical_data_id = f"OAS1_{patient_id}_{file.split('_')[4]}" # ID
        if modaltiy == "MRI":
            mr_id = file.split('_')[4][2:]
            mr_type = "T1w"
            if "img" in file and len(file.split('_')[-1].split('.')[0]) > 3:
                img_id = file.split('_')[-1].split('.')[0][3:]

    elif 'OAS2' in file:
        dataset_marker = 'OAS2'
        patient_id = file.split('_')[3]
        slice_id = file.split('_')[1]
        slice_type = "Axial"
        OASISID = f'OAS2_{patient_id}'
        modaltiy = file_full_path.split('/')[5]
        # OAS2_0001_MR1
        clinical_data_id = f"OAS2_{file.split('_')[3]}_{file.split('_')[4]}" # MRI ID
        if modaltiy == "MRI":
            mr_id = file.split('_')[4][2:]
            mr_type = "T1w" 
            if "img" in file and len(file.split('_')[-1].split('.')[0]) > 3:
                img_id = file.split('_')[-1].split('.')[0][3:]

    elif 'OAS3' in file:
        dataset_marker = 'OAS3'
        modaltiy = file_full_path.split('/')[5]
        # OAS30001_UDSb4_d0000
        # Slice_100_sub-OAS30001_ses-d0129_run-01_T1w_axial_img.png
        if modaltiy == "MRI":
            OASISID = file.split('_')[2].split('-')[1]
            patient_id = file.split('_')[2].split('-')[1][4:]
            slice_id = file.split('_')[1]
            slice_type = "Axial"
            day = int(day_match.group(1)) if day_match else 0
            clinical_data_id = "" # matching_up_the_data_upper_lower(file.split('_')[2].split('-')[1], day, cdr_dfs['OAS3'], 180, 180)
            if "run" in file:
                run_id = file.split('_')[4].split('-')[1]
            mr_type = "T1w" if "T1w" in file else "T2w"
            if "img" in file and len(file.split('_')[-1].split('.')[0]) > 3:
                img_id = file.split('_')[-1].split('.')[0][3:]
            
        if modaltiy == "CT":
            OASISID = file.split('_')[3]
            patient_id = file.split('_')[3][4:]
            slice_id = file.split('_')[2]
            slice_type = "Axial"
            day = int(day_match.group(1)) if day_match else 0
            clinical_data_id = "" # matching_up_the_data_upper_lower(file.split('_')[3], day, cdr_dfs['OAS3'], 180, 180)
            if "img" in file and len(file.split('_')[-1].split('.')[0]) > 3:
                img_id = file.split('_')[-1].split('.')[0][3:]

        if "PIB" in file or "AV45" in file or "FDG" in file:
            dataset_marker = "OAS3"
            OASISID = file.split("_")[2].split("-")[1]
            patient_id = file.split("_")[2].split("-")[1][4:]
            slice_id = file.split('_')[2]
            slice_type = "Axial"
            day = int(file.split("_")[3].split("-")[1][1:])
            clinical_data_id = ""
            
    elif 'OAS4' in file:
        # Slice_x_100_OAS42027_MR_d3034_img9.png
        dataset_marker = 'OAS4'
        patient_id = file.split('_')[3][4:]
        slice_id = file.split('_')[2]
        slice_type = "Axial"
        OASISID = file.split('_')[3]
        modaltiy = file_full_path.split('/')[5]
        clinical_data_id = f"{file.split('_')[3]}_CDR_{file.split('_')[5]}" # cdr_id
        if modaltiy == "MRI":
            mr_id = None
            mr_type = "T1w"
            day = int(day_match.group(1)) if day_match else 0
            clinical_data_id = "" # matching_up_the_data_upper_lower(file.split('_')[3], day, cdr_dfs['OAS4'], 180, 180)
            if "img" in file and len(file.split('_')[-1].split('.')[0]) > 3:
                img_id = file.split('_')[-1].split('.')[0][3:]

    return patient_id, mr_id, slice_id, slice_type, OASISID, mr_type, img_id, day, run_id, dataset_marker, clinical_data_id


# This function is used to move the files from one folder to another.
def create_df(files_dictionary, data_folder, root_folder, categorised_preprocessed_image_dir):

    # Collect all PNG files into a list
    png_files = [(root, file) for root, dirs, files in os.walk(data_folder) 
             for file in files if file.endswith("png") and file != ".DS_Store"]

    print(f"Total PNG files: {len(png_files)}")

    files_dictionary = {file: os.path.join(root, file) for root, file in png_files}

    # convert dictionary to dataframe
    files_directory_df = pd.DataFrame(list(files_dictionary.items()),columns = ['file','file_full_path'])
    # Add OASISID column to the dataframe
    # files_directory_df['file'].split("_")[2].split("-")[1]
    files_directory_df['OASISID'] = files_directory_df['file'].str.extract(r'(OAS3\d{4})', expand=False).str.strip()


    # Add Day column to the dataframe id OASISID contain OAS3 or OAS4
    if "OAS3" in files_directory_df['file'].values.any() or "OAS4" in files_directory_df['file'].values.any():
        files_directory_df['CLINICALDATAID'] = files_directory_df['OASISID'] + "_scan_" + files_directory_df['file'].str.extract(r'(d\d{4})', expand=False).str.strip()
        files_directory_df['Day'] = files_directory_df['file'].str.extract(r'(d\d{4})', expand=False).str.strip().apply(lambda x: int(x.split('d')[1]) if isinstance(x, str) else 0)

    print(f"Total Files Dictionary Length: {len(files_dictionary)}")

    print(f"Loading CDR files...")
    
    # Pre-fetch CDR file paths outside the loop
    cdr_file_paths = {
        'OAS1': find_file_paths(root_folder, 'oasis1_cross-sectional.csv'),
        'OAS2': find_file_paths(root_folder, 'oasis2_longitudinal_demographics.xlsx'),
        'OAS3': find_file_paths(root_folder, 'OASIS3_UDSb4_cdr.csv'),
        'OAS3Unchanged': find_file_paths(root_folder, 'OASIS3_unchanged_CDR_cognitively_healthy.csv'), # OASIS3_id	Min of CDRTOT	Max of CDRTOT
        'OAS4': find_file_paths(root_folder, 'OASIS4_data_CDR.csv')
    }
    
    # Pre-load CDR data frames if files exist
    cdr_dfs = {}
    if cdr_file_paths['OAS1']:
        # copy ID column before changing the name 
        cdr_dfs['OAS1'] = pd.read_csv(cdr_file_paths['OAS1'][0])
        cdr_dfs['OAS1']['CLINICALDATAID'] = cdr_dfs['OAS1']['ID']
        cdr_dfs['OAS1'] = cdr_dfs['OAS1'].rename(columns={'ID': 'OASISID'})
    if cdr_file_paths['OAS2']:
        cdr_dfs['OAS2'] = pd.read_excel(cdr_file_paths['OAS2'][0]).rename(columns={'Subject ID': 'OASISID', "MRI ID": "CLINICALDATAID"})
    if cdr_file_paths['OAS3']:
        cdr_dfs['OAS3'] = pd.read_csv(cdr_file_paths['OAS3'][0]).rename(columns={'OASISID': 'OASISID', 'CDRTOT': 'CDR', 'OASIS_session_label': 'CLINICALDATAID'})
        # Create new column called day and extract the day from the OASIS_session_label using str.extract(r'(d\d{4})', expand=False).str.strip().apply(lambda x: int(x.split('d')[1]) if isinstance(x, str) else 0)
        cdr_dfs['OAS3']['Day'] = cdr_dfs['OAS3']['CLINICALDATAID'].str.extract(r'(d\d{4})', expand=False).str.strip().apply(lambda x: int(x.split('d')[1]) if isinstance(x, str) else 0)
    if cdr_file_paths['OAS3Unchanged']:
        cdr_dfs['OAS3Unchanged'] = pd.read_csv(cdr_file_paths['OAS3Unchanged'][0]).rename(columns={'OASIS3_id': 'OASISID', 'Max of CDRTOT': 'CDR'})
    if cdr_file_paths['OAS4']:
        cdr_dfs['OAS4'] = pd.read_csv(cdr_file_paths['OAS4'][0]).rename(columns={'oasis_id': 'OASISID', 'cdr_id': 'CLINICALDATAID'}) 
        cdr_dfs['OAS4']['Day'] = cdr_dfs['OAS3']['CLINICALDATAID'].str.extract(r'(d\d{4})', expand=False).str.strip().apply(lambda x: int(x.split('d')[1]) if isinstance(x, str) else 0)

    # Change the column names to uppercase
    for key in cdr_dfs:
        cdr_dfs[key].columns = [col.upper() for col in cdr_dfs[key].columns]

    # Now that all DataFrames have a common column name for the ID, concatenate them
    # cdr_df = pd.concat(cdr_dfs.values(), ignore_index=True)
       
    print(f"Successfully concatenated the CDR files and Starting extraction...")
    
    save_rows = []

    print(f"Starting match up...")

    if "OAS3" in files_directory_df['file'].values.any():
        files_directory_df = matching_up_the_data_upper_lower_full(files_directory_df, cdr_dfs['OAS3'], 180, 180)
    elif "OAS4" in files_directory_df['file'].values.any():
        files_directory_df = matching_up_the_data_upper_lower_full(files_directory_df, cdr_dfs['OAS4'], 180, 180)

    # print(files_directory_df)
        
    print(f"Successfully matched up the data and Starting extraction...")
    
    for file, file_full_path in files_dictionary.items():

        patient_id, mr_id, slice_id, slice_type, OASISID, mr_type, img_id, day, run_id, dataset_marker, clinical_data_id = extract_ids(file, file_full_path, cdr_dfs)

        # Get label_id based on the dataset
        label_id = None

        if dataset_marker in cdr_dfs:
            if "OAS3" in dataset_marker:
                # print(files_directory_df[files_directory_df['file'] == file])
                clinical_data_id = files_directory_df[files_directory_df['file'] == file]['CLINICALDATAID_clinical_assessment'].values[0] if files_directory_df[files_directory_df['file'] == file]['CLINICALDATAID_clinical_assessment'].values.any() else None

                # print(f"Patient ID: {patient_id} | MR ID: {mr_id} | Slice ID: {slice_id} | Slice Type: {slice_type} | OASISID: {OASISID} | MR Type: {mr_type} | Img ID: {img_id} | Day: {day} | Run ID: {run_id} | Dataset Marker: {dataset_marker} | Clinical Data ID: {clinical_data_id}")

                if clinical_data_id is None:
                    continue
                
                # Check the cdr_dfs['OAS3Unchanged'] df first and if not found there check cdr_dfs['OAS3']
                if OASISID in cdr_dfs['OAS3Unchanged']['OASISID'].values:
                    label_id = cdr_dfs['OAS3Unchanged'][cdr_dfs['OAS3Unchanged']['OASISID'] == OASISID]['CDR'].values[0]
                    # print(f"Label ID: {label_id}")
                elif clinical_data_id in cdr_dfs[dataset_marker]['CLINICALDATAID'].values:
                    # Check to see the file in files_directory_df and get the corresponding CLINICALDATAID
                    label_id = cdr_dfs[dataset_marker][cdr_dfs[dataset_marker]['CLINICALDATAID'] == clinical_data_id]['CDR'].values[0]
                    # print(f"{clinical_data_id} - Label ID: {label_id}")
                else:
                    print(f"Label ID not found for {clinical_data_id} -  {OASISID}")
                    label_id = None
            else:
                if clinical_data_id in cdr_dfs[dataset_marker]['CLINICALDATAID'].values:
                    label_id = cdr_dfs[dataset_marker][cdr_dfs[dataset_marker]['CLINICALDATAID'] == clinical_data_id]['CDR'].values[0]
                    print(f"Label ID: {label_id}")
                else:
                    print(f"Label ID not found for {clinical_data_id}")
                    label_id = None

        if label_id is not None or label_id != "":
            # Determine the destination based on the CDR label
            if label_id is not None and label_id != "":
                # Determine the destination based on the CDR label
                dest_item = os.path.join(categorised_preprocessed_image_dir, get_cdr_label(float(label_id)), file)
            else:
                # Determine the destination based on the CDR label
                dest_item = os.path.join(categorised_preprocessed_image_dir, "unknown", file)
            # print(f"file_full_path {file_full_path} - dest_item {dest_item}")
        else:
            # Determine the destination based on the CDR label
            dest_item = os.path.join(categorised_preprocessed_image_dir, "unknown", file)
            # print(f"file_full_path {file_full_path} - dest_item {dest_item}")

        label = get_cdr_label(float(label_id)) if label_id is not None else None
        save_rows.append({'patient_id': patient_id, 'mr_id': mr_id, 'slice_id': slice_id, 'slice_type': slice_type, 'OASISID': OASISID, 'mr_type': mr_type, 'img_id': img_id, 'day': day, 'run_id': run_id, 'dataset_marker': dataset_marker, 'clinical_data_id': clinical_data_id, 'label_id': label_id, 'label': label, 'file': file, 'file_full_path': file_full_path, 'dest_item': dest_item})

    # save save_rows to a csv file
    save_df = pd.DataFrame(save_rows, columns=['patient_id', 'mr_id', 'slice_id', 'slice_type', 'OASISID', 'mr_type', 'img_id', 'day', 'run_id', 'dataset_marker', 'clinical_data_id', 'label_id', 'label', 'file', 'file_full_path', 'dest_item'])
    save_df.to_csv('save_df.csv', index=False)

    return save_df
# This function is used to move the images into the categories.
def move_images_into_categories(data_folder):
    original_preprocessed_images_dir = os.path.join(data_folder, 'Preprocessed')
    categorised_preprocessed_image_dir = os.path.join(data_folder, 'Preprocessed_Categories')

    # Ensure the categorized directory exists
    os.makedirs(categorised_preprocessed_image_dir, exist_ok=True)
    print(f"Ensured or created folder: {categorised_preprocessed_image_dir}")

    # Assuming create_categories_folders() creates necessary category directories
    create_categories_folders(categorised_preprocessed_image_dir)

    # Collect all PNG files into a list
    png_files = [(root, file) for root, dirs, files in os.walk(original_preprocessed_images_dir) 
             for file in files if file.endswith("png") and file != ".DS_Store"]

    print(f"Total PNG files in Original: {len(png_files)}")

    # Assuming create_df() function returns a DataFrame with 'file_full_path' and 'dest_item' for each file
    file_moves_df = create_df({file: os.path.join(root, file) for root, file in png_files}, original_preprocessed_images_dir, data_folder, categorised_preprocessed_image_dir)

    print(f"DataFrame rows (file moves planned): {len(file_moves_df)}")

    # Move files based on the DataFrame
    for index, row in file_moves_df.iterrows():
        dest_dir = os.path.dirname(row["dest_item"])
        os.makedirs(dest_dir, exist_ok=True)  # Ensure destination directory exists

        if os.path.exists(row["dest_item"]):
            if os.path.isdir(row["dest_item"]):
                shutil.rmtree(row["dest_item"])
            else:
                os.remove(row["dest_item"])
        
        shutil.move(row["file_full_path"], row["dest_item"])
        print(f"Moved: {row['file_full_path']} to {row['dest_item']}")

    print(f"Completed moving {len(file_moves_df)} files.")
# Define the root destination directory (you might need to adjust this)
destination_root = sys.argv[1]

move_images_into_categories(destination_root)