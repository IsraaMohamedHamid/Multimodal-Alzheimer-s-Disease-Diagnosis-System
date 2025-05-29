# Cell 1: Import libraries
import pandas as pd
import numpy as np
import os
import sys
import shutil

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
    return cdr_mapping.get(cdr_value, 'Unknown')

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

# Cell 2: Define the main function and any additional functions
def matching_up_the_data_upper_lower(scan_session_day, clinical_assesment_day, lower_bound, upper_bound):
    
    # Create a Day column from ID
    # Use the "dXXXX" value from the ID/label in the first column
    # pandas extract will pull that based on a regular expression no matter where it is.

   
    # Update scan_session_day to only consider subjects that are in both lists
    # scan_session_day = scan_session_day.loc[scan_session_day['OASISID'].isin(clinical_assesment_day['OASISID'])]

    # Create and populate the dataframe
    for index, row in clinical_assesment_day.iterrows():
        mask = (scan_session_day['OASISID'] == row['OASISID']) & ((scan_session_day['days_to_visit'] < row['days_to_visit'] + upper_bound) & (scan_session_day['days_to_visit'] > row['days_to_visit'] - lower_bound))   
        for name in row.index:
            scan_session_day.loc[mask, name +'_clinical_assesment_day'] = row[name]
    
    # Drop rows of which a match was not found
    #scan_session_day.dropna(inplace=True)
    # clinical_assesment_day_firstcolumnname=clinical_assesment_day.columns.values[0] + "_clinical_assesment_day"
    # scan_session_day.dropna(subset=[clinical_assesment_day_firstcolumnname])
    #clinical_assesment_day.dropna(subset=[clinical_assesment_day_firstcolumnname])

    # scan_session_day.to_csv(output_name, index=False)
    return scan_session_day

def create_df(new_data_df, files_dictionary, categorised_preprocessed_image_dir):
    # Create a mapping of file to label_id to avoid repeated .loc calls
    file_to_label_map = new_data_df.set_index('file')['CDR_clinical_assesment_day_label'].to_dict()

    save_rows = [{
        'file': file,
        'file_full_path': file_full_path,
        'dest_item': os.path.join(categorised_preprocessed_image_dir, file_to_label_map.get(file, 'unknown'), file)
    } for file, file_full_path in files_dictionary.items() if file in file_to_label_map]

    # Save save_rows to a csv file
    save_df = pd.DataFrame(save_rows, columns=['file', 'file_full_path', 'dest_item'])

    return save_df

# This function is used to move the images into the categories.
def move_images_into_categories(data_folder, file_moves_df):
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

    print(f"Total PNG files: {len(png_files)}")

    # Assuming create_df() function returns a DataFrame with 'file_full_path' and 'dest_item' for each file
    # file_moves_df = create_df(match_up_df, categorised_preprocessed_image_dir)

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

def main(data_folder):
    
    # Pre-fetch CDR file paths outside the loop
    cdr_file_paths = {
        'OAS1': find_file_paths(data_folder, 'oasis1_cross-sectional.csv'),
        'OAS2': find_file_paths(data_folder, 'oasis2_longitudinal_demographics.xlsx'),
        'OAS3': find_file_paths(data_folder, 'OASIS3_UDSb4_cdr.csv'),
        'OAS3Unchanged': find_file_paths(data_folder, 'OASIS3_unchanged_CDR_cognitively_healthy.csv'), # OASIS3_id	Min of CDRTOT	Max of CDRTOT
        'OAS4': find_file_paths(data_folder, 'OASIS4_data_CDR.csv')
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
    if cdr_file_paths['OAS3Unchanged']:
        cdr_dfs['OAS3Unchanged'] = pd.read_csv(cdr_file_paths['OAS3Unchanged'][0]).rename(columns={'OASIS3_id': 'OASISID', 'Max of CDRTOT': 'CDR'})
    if cdr_file_paths['OAS4']:
        cdr_dfs['OAS4'] = pd.read_csv(cdr_file_paths['OAS4'][0]).rename(columns={'oasis_id': 'OASISID', 'cdr_id': 'CLINICALDATAID', 'visit_days': 'days_to_visit', 'cdr': 'CDR'}) 

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

    print(f"Total PNG files: {len(png_files)}")

    files_dictionary = {file: os.path.join(root, file) for root, file in png_files}

    # convert dictionary to dataframe
    files_directory_df = pd.DataFrame(list(files_dictionary.items()),columns = ['file','file_full_path'])
    # Add OASISID column to the dataframe
    files_directory_df['OASISID'] = files_directory_df['file'].str.extract(r'(OAS\d{5})', expand=False).str.strip()

    # Add Day column to the dataframe id OASISID contain OAS3 or OAS4
    if "OAS3" in files_directory_df['file'].values.any() or "OAS4" in files_directory_df['file'].values.any():
        if files_directory_df['file'].str.contains(r'(d\d{4})').any():
            files_directory_df['CLINICALDATAID'] = files_directory_df['OASISID'] + "_scan_" + files_directory_df['file'].str.extract(r'(d\d{4})', expand=False).str.strip()
            files_directory_df['days_to_visit'] = files_directory_df['file'].str.extract(r'(d\d{4})', expand=False).str.strip().apply(lambda x: int(x.split('d')[1]) if isinstance(x, str) else 0)
        elif files_directory_df['file'].str.contains(r'(d\d{5})').any():
            files_directory_df['CLINICALDATAID'] = files_directory_df['OASISID'] + "_scan_" + files_directory_df['file'].str.extract(r'(d\d{5})', expand=False).str.strip()
            files_directory_df['days_to_visit'] = files_directory_df['file'].str.extract(r'(d\d{5})', expand=False).str.strip().apply(lambda x: int(x.split('d')[1]) if isinstance(x, str) else 0)

    print(files_directory_df)
    print(f"Total Files Dictionary Length: {len(files_dictionary)}")
    
    if "OAS3" in files_directory_df['file'].values.any():
        print(f"Files Dictionary Length before moving cognitively healthy files: {len(files_dictionary)}")
        for index, row in files_directory_df.iterrows():
            if row['OASISID'] in cdr_dfs['OAS3Unchanged']['OASISID'].values:
                # Get OASIS3_unchanged_CDR_cognitively_healthy['Max of CDRTOT'] to feed to get_cdr_label
                label_id = cdr_dfs['OAS3Unchanged'][cdr_dfs['OAS3Unchanged']['OASISID'] == row['OASISID']]['CDR'].values[0]
                # Move the file to the respective category folder
                source = row['file_full_path']
                destination = os.path.join(categorised_preprocessed_image_dir, get_cdr_label(label_id), row['file'])
                shutil.move(source, destination)
                # Remove row from the dataframe
                files_directory_df.drop(index, inplace=True)

        print(f"Files Dictionary Length after moving cognitively healthy files: {len(files_dictionary)}")
    
    if "OAS3" in files_directory_df['file'].values.any():
        new_clinical_df = cdr_dfs['OAS3'].copy()[['OASISID', 'CLINICALDATAID', 'days_to_visit', "CDR"]]
    elif "OAS4" in files_directory_df['file'].values.any():
        new_clinical_df = cdr_dfs['OAS4'].copy()[['OASISID', 'CLINICALDATAID', 'days_to_visit', "CDR"]]
    

    print(f"{files_directory_df}")
    print(f"Starting to match up the data...")

    match_up_df = matching_up_the_data_upper_lower(files_directory_df, new_clinical_df, 180, 180)

    print(match_up_df)
    print(f"Data matched up")
    
    match_up_df['CDR_clinical_assesment_day'] = pd.to_numeric(match_up_df['CDR_clinical_assesment_day'], errors='coerce')
    # Create a new column in the dataframe with the CDR label
    match_up_df['CDR_clinical_assesment_day_label'] = match_up_df['CDR_clinical_assesment_day'].apply(get_cdr_label)
    
    print(f"Data matched up and saved to output_name.csv")

    file_moves_df = create_df(match_up_df,files_dictionary, categorised_preprocessed_image_dir)
    
    print(f"Dataframe created for moving files")

    move_images_into_categories(data_folder, file_moves_df)

    print(f"Images moved into categories")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <data_folder> <cdr_data_path1> [<cdr_data_path2> ...]")
        sys.exit(1)
    
    data_folder = sys.argv[1]
    main(data_folder)