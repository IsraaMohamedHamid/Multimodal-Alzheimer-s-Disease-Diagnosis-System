#################### IMPORTS ####################
# ALL
import os
import re

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
from DataScript.get_patient_data import *

#################### FUNCTIONS ####################

# This function will validate filename to ensure it is a valid OASIS Alzheimer's dataset filename
def validate_filename(filename):
    """
    Validate filename to ensure it is a valid OASIS Alzheimer's dataset filename.
    Checks against two patterns:
    - The original pattern for older OASIS file naming conventions.
    - A new pattern for BIDS-compliant NIfTI file naming.
    """
    # Original pattern
    pattern1 = re.compile(
        r'OAS(\d+)_(\d+)_MR(\d+)_mpr(?:-|_n)(\d+)_anon(?:_sbj_111|_111_t88(?:_masked)?_gfc(?:_fseg)?)?\.(\w+)$'
    )
    
    # Modified BIDS-compliant NIfTI pattern
    pattern2 = re.compile(
    r'sub-OAS(\d+)_ses(s)?-d(\d+)(_acq-hippocampus)?(_echo-\d+)?(_run-\d+)?_([a-zA-Z0-9]+)\.nii\.gz$'
    )

    # mpr-1.nifti.img
    pattern3 = re.compile(r'mpr-(\d+)\.nifti\.(\w+)$')

    pattern4 = re.compile(
        r'OAS(\d+)_(\d+)_MR(\d+)_(\d+)-(\d+)\.nifti\.(img|hdr)$'
    )
    # 3906-3.nifti.img

    pattern5 = re.compile(
        r'sub-OAS(\d{1})(\d+)_ses-d(\d+)_acq-(PIB|FDG|AV45)_pet\.nii\.gz'
    )
   
    # Check if the filename matches either of the two patterns
    return bool(pattern1.match(filename) or pattern2.match(filename) or pattern3.match(filename) or pattern4.match(filename)) or pattern5.match(filename)

# This function will get info from filename
def change_filename(folder, filename, layer_id=0):
    """
    Extract patient_id and layer_id from filename
    """
    if validate_filename(filename):
        return filename
    
    # if mpr-1 is followed by . then remove .nifti from name # Pattern to match '.nifti' or '.4dfp' right before the file extension
    pattern = re.compile(r'(\.nifti|\.4dfp)(?=\.\w+$)') #TODO: Change patterns to match other file formats

    # Replace '.nifti' or '.4dfp' with '_0' if it's right before the file extension
    filename = re.sub(pattern, f'_{layer_id}', filename)

    # Combine file and folder to one name a
    filename = folder + '_' + filename

    return filename

# Unify the filename based on predefined patterns
def unify_filename(filename):
    """
    Unify the filename based on predefined patterns including both original OASIS and BIDS-compliant nii.gz filenames.
    """
    patterns = {
    'individual_scan': ('OAS(\d+)_(\d+)_MR(\d+)_mpr-(\d+)_anon.(\w+$)', 'RAW', None, None),
    'averaged_across_scans': ('OAS(\d+)_(\d+)_MR(\d+)_mpr_n(\d+)_anon_sbj_111.(\w+$)', 'PROCESSED', 'sbj111', None),
    'gain_field_corrected_atlas_registered_average': ('OAS(\d+)_(\d+)_MR(\d+)_mpr_n(\d+)_anon_111_t88_gfc.(\w+$)', 'PROCESSED', 't88111', None),
    'brain_masked_version_of_atlas_registered_image': ('OAS(\d+)_(\d+)_MR(\d+)_mpr_n(\d+)_anon_111_t88_masked_gfc.(\w+$)', 'PROCESSED', 't88111', 'maskedgfc'),
    'brain_tissue_segmentation': ('OAS(\d+)_(\d+)_MR(\d+)_mpr_n(\d+)_anon_111_t88_masked_gfc_fseg.(\w+$)', 'FSL_SEG', None, 'maskedgfcfseg'),
    'oasis_3_tw1': ('sub-OAS(\d+)_ses(s)?-d(\d+)(_acq-hippocampus)?(_echo-\d+)?(_run-\d+)?_([a-zA-Z0-9]+)\.nii\.gz', 'NIFTI', None, None),
    'oasis_2':('mpr-(\d+).nifti\.(\w+)$', 'RAW', None, None),
    'PET_AV45': ('sub-OAS(\d{1}})(\d+)_ses-d(\d+)_acq-(PIB|FDG|AV45)_pet\.nii\.gz', 'NIFTI', None, None)   
}

    for key, (pattern_str, subdirectory, subsubdirectory, masked) in patterns.items():
        pattern = re.compile(pattern_str)
        match = pattern.match(filename)
        if match:
            if 'oasis_3_tw1' in key:
                # Adjustments for BIDS-compliant nii.gz filenames
                patient_id, session_id, run_id, mri_type, _ = match.groups()
                run_part = run_id if run_id else ''  # Including run part only if present
                unified_filename = f"OAS{patient_id}_ses-d{session_id}{run_part}_{mri_type}.nii.gz"
            elif 'oasis_2' in key:
                # Adjustments for BIDS-compliant nii.gz filenames
                scan_id_or_average_image_id = match.groups()
                unified_filename = f"mpr-{scan_id_or_average_image_id}.nii.gz"
            else:
                # Original OASIS dataset handling
                oasis_dataset_number, patient_id, mr_id, scan_id_or_average_image_id, file_format = match.groups()
                scan_id = scan_id_or_average_image_id if 'individual_scan' in key else None
                average_image_id = scan_id_or_average_image_id if 'individual_scan' not in key else None

                # Building unified filename
                unified_parts = [
                    f"OAS{oasis_dataset_number}_{patient_id}_MR{mr_id}",
                    f"mpr",
                    f"{'' if scan_id else 'n'}{scan_id or average_image_id}",
                    f"anon",
                    f"{subsubdirectory}" if subsubdirectory else "None",
                    f"{masked}" if masked else "None",
                ]
                unified_filename = "_".join(filter(None, unified_parts))  # Filter out any empty strings
                # join file format at the end
                unified_filename += '.' + file_format
            return unified_filename

    # If no pattern matches, return None or original filename
    return None

# This function will get info from filename
def get_info_from_filename(filename):
    """
    Extract information from a filename based on predefined patterns.
    """
    # itialize variables to ensure they are defined
    oasis_dataset_number, patient_id, mri_type, mr_id, run_id, acq, echo, scan_id, average_image_id, additional_id, subdirectory, subsubdirectory, masked, file_format = None, None, None, None, None, None, None, None, None, None, None, None, None, None
    # Define a single pattern that encompasses all variations
    pattern1 = re.compile(
        r'OAS(\d+)_(\d+)_MR(\d+)_mpr(?:-|_n)(\d+)_anon(?:_sbj_111|_111_t88(?:_masked)?_gfc(?:_fseg)?)?\.(\w+)$'
    )

    pattern2 = re.compile(
    r'sub-OAS(\d+)_ses(s)?-d(\d+)(_acq-hippocampus)?(_echo-\d+)?(_run-\d+)?_([a-zA-Z0-9]+)\.nii\.gz$'
    )

    pattern3 = re.compile(
    r'OAS(\d+)_(\d+)_MR(\d+)_mpr(?:-|_n)(\d+)\.nifti\.(\w+)$'
    )

    #OAS2_0012_MR2_3906-3.nifti.img
    pattern4 = re.compile(
        r'OAS(\d+)_(\d+)_MR(\d+)_(\d+)-(\d+)\.nifti\.(img|hdr)$'
    )

    
    pattern5 = re.compile(
        r'sub-OAS(\d{1})(\d+)_ses-d(\d+)_acq-(PIB|FDG|AV45)_pet\.nii\.gz'
    )

    oasis_dataset_number, patient_id, mr_id, scan_id, average_image_id, file_format,  = None, None, None, None, None, None

    if pattern1.match(filename) or pattern3.match(filename) or pattern4.match(filename) or pattern5.match(filename):
        if pattern1.match(filename):
            oasis_dataset_number, patient_id, mr_id, additional_id, file_format = pattern1.match(filename).groups()
        elif pattern3.match(filename):
            oasis_dataset_number, patient_id, mr_id, additional_id, file_format = pattern3.match(filename).groups()
        elif pattern4.match(filename):
            oasis_dataset_number, patient_id, mr_id, additional_id, file_format = pattern4.match(filename).groups()
        elif pattern5.match(filename):
            oasis_dataset_number, patient_id, session_id, run_id = pattern5.match(filename).groups()

        # Determine subdirectory and other attributes based on the filename structure
        if 'sbj_111' in filename:
            subdirectory = 'PROCESSED'
            subsubdirectory = 'SUBJ_111'
        elif 't88' in filename and 'masked' in filename and 'fseg' in filename:
            subdirectory = 'FSL_SEG'
            subsubdirectory = None
            masked = 'gfc_fseg'
        elif 't88' in filename and 'gfc' in filename:
            subdirectory = 'PROCESSED'
            subsubdirectory = 'T88_111'
            masked = 'gfc' if 'masked' not in filename else 'masked_gfc'
        else:
            subdirectory = 'RAW'
            subsubdirectory = None
            masked = None
        
        # Decide between scan_id and average_image_id based on the filename
        scan_id = None
        average_image_id = None
        if '_mpr-' in filename:
            scan_id = additional_id
        else:
            if additional_id != None:
                average_image_id = additional_id

        run_id, acq, echo = None, None, None

        if int(oasis_dataset_number) == 1 or int(oasis_dataset_number) == 2:
            mri_type = 'T1w'

        return oasis_dataset_number, patient_id, mri_type, mr_id, run_id, acq, echo, scan_id, average_image_id, subdirectory, subsubdirectory, masked, file_format

    elif pattern2.match(filename):

        oasis_dataset_number_and_patient_id, _, session_id, acq, echo, run_id, mri_type = pattern2.match(filename).groups()

        # Split first value  of oasis_dataset_number_and_patient_id as oasis_dataset_number and rest is patient_id
        oasis_dataset_number_and_patient_id_str = str(oasis_dataset_number_and_patient_id)

        # Splitting the string
        oasis_dataset_number = oasis_dataset_number_and_patient_id_str[0]  # First digit
        patient_id = oasis_dataset_number_and_patient_id_str[1:]  # Rest of the digits

        file_format = 'nii.gz'

        mr_id = session_id
        scan_id = None
        average_image_id = None
        subdirectory = 'NITFI'
        subsubdirectory = None
        masked = None


        return oasis_dataset_number, patient_id, mri_type, mr_id, run_id, acq, echo, scan_id, average_image_id, subdirectory, subsubdirectory, masked, file_format
    
    elif pattern4.match(filename):
        oasis_dataset_number, patient_id, mr_id, scan_id, average_image_id, file_format = pattern4.match(filename).groups()
        subdirectory = 'RAW'
        subsubdirectory = None
        masked = None

        return oasis_dataset_number, patient_id, mri_type, mr_id, run_id, acq, echo, scan_id, average_image_id, subdirectory, subsubdirectory, masked, file_format
    

    elif pattern5.match(filename):
        subdirectory = 'RAW'
        subsubdirectory = None
        masked = None

        return oasis_dataset_number, patient_id, mri_type, mr_id, run_id, acq, echo, scan_id, average_image_id, subdirectory, subsubdirectory, masked, file_format
    # Return None or raise an error if the filename does not match any pattern
    return None, None, None, None, None, None, None, None, None, None, None, None, None

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

# This function will extract file format
def extract_file_format(file_name):
    """
    Extracts the file format from a file name.
    
    Parameters:
    file_name (str): The name of the file including its extension.
    
    Returns:
    str: The file format (extension) of the file.
    """
    # Split the file name by '.' and get the last part as the file format
    if file_name.endswith('.nii.gz'):
        file_format = 'nii.gz'
    else:
        # Use os.path.splitext for other extensions
        file_format = file_name.split('.')[-1]
    return file_format

# This function will remove the file extension
def remove_file_extension(file_name):
    """
    Removes the file extension from a file name.
    
    Parameters:
    file_name (str): The name of the file including its extension.
    
    Returns:
    str: The file name without the extension.
    """
    # Split the file name by '.' and get the first part as the file name without the extension
    if file_name.endswith('.nii.gz'):
        file_name_without_extension = file_name[:-7]  # Remove last 7 characters ('.nii.gz')
    else:
        # Use os.path.splitext for other extensions
        file_name_without_extension, _ = os.path.splitext(file_name)
    return file_name_without_extension

# Cell 2: Define the main function and any additional functions
def matching_up_the_data_upper_lower(scan_session_day, clinical_assesment_day, lower_bound, upper_bound):
   
    # Update scan_session_day to only consider subjects that are in both lists
    # scan_session_day = scan_session_day.loc[scan_session_day['OASISID'].isin(clinical_assesment_day['OASISID'])]

    # Create and populate the dataframe
    for index, row in clinical_assesment_day.iterrows():
        mask = (scan_session_day['OASISID'] == row['OASISID']) & ((scan_session_day['days_to_visit'] < row['days_to_visit'] + upper_bound) & (scan_session_day['days_to_visit'] > row['days_to_visit'] - lower_bound))   
        for name in row.index:
            scan_session_day.loc[mask, name +'_clinical_assesment_day'] = row[name]
            
    return scan_session_day

def create_match_up_df(new_data_df, files_dictionary):
    # Create a mapping of file to label_id to avoid repeated .loc calls
    file_to_label_map = new_data_df.set_index('file')['CDR_clinical_assesment_day_label'].to_dict()

    save_rows = [{
        'file': file,
        'file_full_path': file_full_path,
        'label': file_to_label_map.get(file, 'unknown')
    } for file, file_full_path in files_dictionary.items() if file in file_to_label_map]

    # Save save_rows to a csv file
    save_df = pd.DataFrame(save_rows, columns=['file', 'file_full_path', 'label'])

    return save_df

# This function will create a reference dataframe
def create_ref_df(root_directory):
    """
    Create a reference dataframe with columns based on the file and folder structure.
    """

    dataset_path = root_directory + '/Original/'
    columns = ['oasis_dataset_number', 'path', 'folder', 'label_id', 'label', 'patient_id', 'mri_type', 'mr_id', 'run_id', "acq", "echo", 'scan_id', 'average_image_id', 'subdirectory', 'subsubdirectory', 'masked','file_name_wout_format', 'file_format']
    data = {col: [] for col in columns}

    cdr_csv = []

    # Ensure dcr_df is defined before being used
    # dcr_df = pd.DataFrame()

    # # Find the path to the OASIS3_UDSb4_cdr.csv file
    # if find_file_paths(dataset_path, 'OASIS3_UDSb4_cdr.csv') != []:
    #     cdr_csv = find_file_paths(dataset_path, 'OASIS3_UDSb4_cdr.csv')
    #     dcr_df = pd.read_csv(cdr_csv[0])
    # elif find_file_paths(dataset_path, 'oasis_longitudinal_demographics.xlsx') != []:
    #     cdr_csv = find_file_paths(dataset_path, 'oasis_longitudinal_demographics.xlsx')
    #     dcr_df = pd.read_excel(cdr_csv[0])
    
    # Pre-fetch CDR file paths outside the loop
    cdr_file_paths = {
        'OAS1': find_file_paths(root_directory, 'oasis1_cross-sectional.csv'),
        'OAS2': find_file_paths(root_directory, 'oasis2_longitudinal_demographics.xlsx'),
        'OAS3': find_file_paths(root_directory, 'OASIS3_UDSb4_cdr.csv'),
        'OAS3Unchanged': find_file_paths(root_directory, 'OASIS3_unchanged_CDR_cognitively_healthy.csv'), # OASIS3_id	Min of CDRTOT	Max of CDRTOT
        'OAS4': find_file_paths(root_directory, 'OASIS4_data_CDR.csv')
    }

    # Collect all PNG files into a list
    nii_gz_files = [(root, file) for root, dirs, files in os.walk(dataset_path) 
                for file in files if ".nii.gz" in file or "img" in file or "hdr" in file  and file != ".DS_Store"]

    print(f"Total nii.gz files: {len(nii_gz_files)}")

    files_dictionary = {file: os.path.join(root, file) for root, file in nii_gz_files}
    
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
        cdr_dfs['OAS4'] = pd.read_csv(cdr_file_paths['OAS4'][0]).rename(columns={'oasis_id': 'OASISID', 'cdr_id': 'CLINICALDATAID', 'visit_days': 'days_to_visit', 'cdr': 'CDR'}) # convert dictionary to dataframe
    
    
    files_directory_df = pd.DataFrame(list(files_dictionary.items()),columns = ['file','file_full_path'])
    files_directory_df['OASISID'] = files_directory_df['file'].str.extract(r'(OAS\d{5})', expand=False).str.strip()

    # print(files_directory_df['file'])

    # Add Day column to the dataframe id OASISID contain OAS3 or OAS4
    if "OAS3" in files_directory_df['file'].values.any() or "OAS4" in files_directory_df['file'].values.any():
        if files_directory_df['file'].str.contains(r'(d\d{4})').any():
            files_directory_df['CLINICALDATAID'] = files_directory_df['OASISID'] + "_scan_" + files_directory_df['file'].str.extract(r'(d\d{4})', expand=False).str.strip()
            files_directory_df['days_to_visit'] = files_directory_df['file'].str.extract(r'(d\d{4})', expand=False).str.strip().apply(lambda x: int(x.split('d')[1]) if isinstance(x, str) else 0)
        elif files_directory_df['file'].str.contains(r'(d\d{5})').any():
            files_directory_df['CLINICALDATAID'] = files_directory_df['OASISID'] + "_scan_" + files_directory_df['file'].str.extract(r'(d\d{5})', expand=False).str.strip()
            files_directory_df['days_to_visit'] = files_directory_df['file'].str.extract(r'(d\d{5})', expand=False).str.strip().apply(lambda x: int(x.split('d')[1]) if isinstance(x, str) else 0)

    # print(files_directory_df)
    print(f"Total Files Dictionary Length: {len(files_dictionary)}")
    
    if "OAS3" in files_directory_df['file'].values.any():
        print(f"Files Dictionary Length before moving cognitively healthy files: {len(files_dictionary)}")
        for index, row in files_directory_df.iterrows():
            if row['OASISID'] in cdr_dfs['OAS3Unchanged']['OASISID'].values:
                # Get OASIS3_unchanged_CDR_cognitively_healthy['Max of CDRTOT'] to feed to get_cdr_label
                label_id = cdr_dfs['OAS3Unchanged'][cdr_dfs['OAS3Unchanged']['OASISID'] == row['OASISID']]['CDR'].values[0]

        print(f"Files Dictionary Length after moving cognitively healthy files: {len(files_dictionary)}")
    
    if "OAS3" in files_directory_df['file'].values.any():
        new_clinical_df = cdr_dfs['OAS3'].copy()[['OASISID', 'CLINICALDATAID', 'days_to_visit', "CDR"]]
    elif "OAS4" in files_directory_df['file'].values.any():
        new_clinical_df = cdr_dfs['OAS4'].copy()[['OASISID', 'CLINICALDATAID', 'days_to_visit', "CDR"]]
    
    if "OAS3" in files_directory_df['file'].values.any() or "OAS4" in files_directory_df['file'].values.any():
        print(f"Beginning to match up data")
        match_up_df = matching_up_the_data_upper_lower(files_directory_df, new_clinical_df, 180, 180)
    
        match_up_df['CDR_clinical_assesment_day'] = pd.to_numeric(match_up_df['CDR_clinical_assesment_day'], errors='coerce')
        # Create a new column in the dataframe with the CDR label
        match_up_df['CDR_clinical_assesment_day_label'] = match_up_df['CDR_clinical_assesment_day'].apply(get_cdr_label)
        
        print(f"Data matched up")

        created_match_up_df = create_match_up_df(match_up_df, files_dictionary)

        print(f"Created match up dataframe")


    for index, row in files_directory_df.iterrows():
        if not validate_filename(row['file']):
            continue  # Skip files that do not match the validation criteria
        
        # Extracting information from path_parts here. Adjust as necessary.
        full_path = row['file_full_path']
        path_parts = full_path.split(os.sep)[len(dataset_path.split(os.sep)):]

        # /Users/izzymohamed/Desktop/untitled folder/OASIS 2/MRI/Original/OAS2_0008_MR1/RAW/mpr-2.nifti.img
        # Extract OAS2_0008_MR1
        if "OAS2" in full_path:
            patient_folder_name = full_path.split(os.sep)[8]
            # print(f"{patient_folder_name}_{file}")

        # Extracting information from path_parts here. Adjust as necessary.
        file_name_wout_format = remove_file_extension(row['file'])
        subdirectory = path_parts[1]
        file_format = extract_file_format(row['file'])

        # Skip undesired subdirectories
        if 'PROCESSED' in full_path or 'FSL_SEG' in full_path:
            continue
        # Skip undesired file formats
        if file_format in ['ifh', "4dfp.img.rec", "json", "csv"]:
            continue  # Skip undesired file formats

        # Dummy values for demonstration. Replace these with actual extracted values.
        if "OAS2" in full_path:
            oasis_dataset_number, patient_id, mri_type, mr_id, run_id, acq, echo, scan_id, average_image_id, subdirectory, subsubdirectory, masked, file_format = get_info_from_filename(f"{patient_folder_name}_{row['file']}")
        else:
            oasis_dataset_number, patient_id, mri_type, mr_id, run_id, acq, echo, scan_id, average_image_id, subdirectory, subsubdirectory, masked, file_format = get_info_from_filename(row['file'])

        # Extracting information from path_parts here. Adjust as necessary.
        folder = f"OAS{oasis_dataset_number}_{patient_id}_MR{mr_id}"
        
        # Get label from information file
        if "OAS1" in row['file']:
            # Read the information file
            label_id = cdr_dfs["OAS1"][cdr_dfs["OAS1"]['OASISID'] == folder]['CDR'].values[0]
            label = get_cdr_label(float(label_id)) if label_id != '' else 'unknown'

        elif "OAS2" in row['file']:

            # check to see if oasis_dataset_number + patient_id is in OASISID column then return CDRTOT column
            label_id = cdr_dfs["OAS2"][cdr_dfs["OAS2"]['CLINICALDATAID'] == folder]['CDR'].values[0]
            label = get_cdr_label(float(label_id)) if label_id != '' else 'unknown'

        elif "OAS3" in row['file'] or "OAS4" in row['file']:
            # go through created_match_up_df['file'] anf if it matches row['file'] then get the label_id
            label = created_match_up_df[created_match_up_df['file'] == row['file']]['label']
            label_id = getcdr(label_id)

        # Append the extracted values to the data dictionary
        for col, value in zip(columns, [oasis_dataset_number, full_path, folder, label_id, label, patient_id, mri_type, mr_id, run_id, acq, echo, scan_id, average_image_id, subdirectory, subsubdirectory, masked, file_name_wout_format, file_format]):
            data[col].append(value)

    ref_df = pd.DataFrame(data)

    return ref_df

# compare ref_df["folder"] with file[0] and get the missing files
def compare_missing_files_in_ref_df(ref_df, load_files_with_extension_files):
    ref_df_file_name_list = ref_df["path"].tolist()

    for path in ref_df_file_name_list:
        if path not in load_files_with_extension_files:
            print(f"Missing from load_files_with_extension: {path}")

    for path in load_files_with_extension_files:
        if path not in ref_df_file_name_list:
            print(f"Missing from ref_df: {path}")

# This function will create a reference dataframe
def get_folder_structure(root_dir):
    """
    Returns a set of paths representing the structure of the directory
    rooted at `root_dir`, relative to `root_dir`.
    """
    structure = set()
    for root, dirs, _ in os.walk(root_dir, topdown=True):
        for name in dirs:
            structure.add(os.path.relpath(os.path.join(root, name), root_dir))
    return structure

# Get the structure of the data and the sturcture of all the folders inside and files
def get_file_and_folder_structure(path):
    structure = {}
    for root, dirs, files in os.walk(path):
        current_dir = structure
        for dir in root.split('/'):
            current_dir = current_dir.setdefault(dir, {})
        for file in files:
            current_dir[file] = None
    return structure

# This function will print the folder structure
def print_folder_structure(startpath):
    """
    Prints the folder structure of the directory at 'startpath'
    and its subdirectories.
    """
    for root, dirs, _ in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for d in dirs:
            print(f'{subindent}{d}/')

# This function will compare the folder structure
def compare_folders_structure(base_path):
    """
    Checks if all top-level folders within `base_path` have the same structure.
    """
    structures = []
    for name in os.listdir(base_path):
        dir_path = os.path.join(base_path, name)
        if os.path.isdir(dir_path):
            structures.append(get_folder_structure(dir_path))

    # Compare all structures
    if all(s == structures[0] for s in structures):
        return True
    else:
        return False
