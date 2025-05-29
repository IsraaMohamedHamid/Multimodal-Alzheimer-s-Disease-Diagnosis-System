#################### IMPORTS ####################
# ALL
import os
import json

#################### FUNCTIONS ####################

# This function will extract the patients data from the json file
def parse_json_file(file_path):
    """
    Parses a JSON file and returns its content as a Python dictionary.

    :param file_path: The full path to the JSON file.
    :return: A dictionary containing the JSON file's content, or None if an error occurs.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    try:
        # Open and read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return None

# This function will extract the patients data from the text file
def parse_txt_file(file_path):
    data = {}  # Initialize an empty dictionary to store the extracted data
    scans = []  # List to hold multiple scan entries
    current_scan = {}  # Temporary dictionary to hold the current scan data

    with open(file_path, 'r') as file:
        for line in file:
            # Check if line contains a colon, indicating a key-value pair
            if ':' in line:
                key, value = line.split(':', 1)  # Split the line at the first colon
                key = key.strip()  # Remove any leading/trailing whitespace
                value = value.strip()  # Remove any leading/trailing whitespace
                
                # Handle scan-specific information
                if key.startswith('SCAN NUMBER'):
                    if current_scan:  # If there's already scan data, add it to the list of scans
                        scans.append(current_scan)
                        current_scan = {}  # Reset the current scan dictionary
                    current_scan[key] = value  # Add the scan number to the current scan dictionary
                elif key in ['TYPE', 'Vox res (mm)', 'Rect. Fov', 'Orientation', 'TR (ms)', 'TE (ms)', 'TI (ms)', 'Flip']:
                    current_scan[key] = value  # Add scan-specific information to the current scan dictionary
                else:
                    data[key] = value  # Add general information to the main data dictionary

    if current_scan:  # Add the last scan data to the list of scans, if present
        scans.append(current_scan)
    
    if scans:  # Add the list of scans to the main data dictionary
        data['SCANS'] = scans

    return data

# def parse_txt_file(file_path):
#     data = {
#         'SESSION ID': None,
#         'AGE': None,
#         'M/F': None,
#         'HAND': None,
#         'EDUC': None,
#         'SES': None,
#         'CDR': None,
#         'MMSE': None,
#         'eTIV': None,
#         'ASF': None,
#         'nWBV': None,
#         'Scans': []
#     }

#     with open(file_path, 'r') as file:
#         lines = file.readlines()
#         current_section = None
#         for line in lines:
#             line = line.strip()
#             if line.startswith('SESSION ID:'):
#                 data['SESSION ID'] = line.split(':')[1].strip()
#             elif line.startswith('AGE:'):
#                 data['AGE'] = int(line.split(':')[1].strip())
#             elif line.startswith('M/F:'):
#                 data['M/F'] = line.split(':')[1].strip()
#             elif line.startswith('HAND:'):
#                 data['HAND'] = line.split(':')[1].strip()
#             elif line.startswith('EDUC:'):
#                 data['EDUC'] = int(line.split(':')[1].strip())
#             elif line.startswith('SES:'):
#                 data['SES'] = int(line.split(':')[1].strip())
#             elif line.startswith('CDR:'):
#                 data['CDR'] = float(line.split(':')[1].strip())
#             elif line.startswith('MMSE:'):
#                 data['MMSE'] = int(line.split(':')[1].strip())
#             elif line.startswith('eTIV:'):
#                 data['eTIV'] = float(line.split(':')[1].strip())
#             elif line.startswith('ASF:'):
#                 data['ASF'] = float(line.split(':')[1].strip())
#             elif line.startswith('nWBV:'):
#                 data['nWBV'] = float(line.split(':')[1].strip())
#             elif line.startswith('mpr-'):
#                 scan_id, scan_type = line.split()
#                 data['Scans'].append({'SCAN NUMBER': scan_id, 'TYPE': scan_type})
#             elif line.startswith('SCAN NUMBER:'):
#                 current_section = line.split(':')[1].strip()
#             elif current_section and line.startswith('Vox res (mm):'):
#                 # Assuming the last scan in 'Scans' list is the current scan
#                 res = line.split(':')[1].strip().split(' x ')
#                 data['Scans'][-1]['Vox res (mm)'] = res
#             elif current_section and line.startswith('Rect. Fov:'):
#                 fov = line.split(':')[1].strip()
#                 data['Scans'][-1]['Rect. Fov'] = fov
#             elif current_section and line.startswith('Orientation:'):
#                 orientation = line.split(':')[1].strip()
#                 data['Scans'][-1]['Orientation'] = orientation
#             elif current_section and line.startswith('TR (ms):'):
#                 tr = line.split(':')[1].strip()
#                 data['Scans'][-1]['TR (ms)'] = tr
#             elif current_section and line.startswith('TE (ms):'):
#                 te = line.split(':')[1].strip()
#                 data['Scans'][-1]['TE (ms)'] = te
#             elif current_section and line.startswith('TI (ms):'):
#                 ti = line.split(':')[1].strip()
#                 data['Scans'][-1]['TI (ms)'] = ti
#             elif current_section and line.startswith('Flip:'):
#                 flip = line.split(':')[1].strip()
#                 data['Scans'][-1]['Flip'] = flip

#     return data

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

def getcdr(label):
    cdr_mapping = {
        "non-demented": 0,
        "very-mild-dementia": 0.5,
        "mild-dementia": 1,
        "moderate-dementia": 2,
        "unknown": ""
    }
    return cdr_mapping.get(label, 'Unknown')