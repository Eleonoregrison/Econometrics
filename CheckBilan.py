# CHECKING FOR EACH SIREN IF WE HAVE THE FINANCIAL STATEMENTS BETWEEN 2016 AND 2023
target_years = set(str(year) for year in range(2016, 2024))


# Ensure that the folder being analyzed contains all the documents for a specific first SIREN digit, including the problematic ones done manually
# Before running this code, it’s advisable to check if all possible financial statements have been downloaded using the INPI API code


import os
import shutil
from collections import defaultdict


# Define the folder path
folder_path = "./probable_siren4"  # Replace with the path to your folder with PDFs for a certain 1st digit siren (for TXTs too, but in this case have to change .pdf in Step 1)
trash_folder = os.path.join(folder_path, "Trash")


# Create a trash folder in the folder path to put financial statements out of the interval 2016-2023 and incomplete siren
if not os.path.exists(trash_folder):
    os.makedirs(trash_folder)


# Dictionary to keep track of documents for each SIREN
siren_documents = defaultdict(set)


# Step 1: Move PDFs outside the target range to the trash folder (for TXTs just change the .pdf to .txt)
for file_name in os.listdir(folder_path):
    if file_name.endswith(".pdf"):
        try:
            siren, date = file_name.split("_")
            year = date.split("-")[0]
            # Check if the year is within the target range
            if year in target_years:
                siren_documents[siren].add(year)
            else:
                # Move the file to the trash folder if outside the range
                shutil.move(os.path.join(folder_path, file_name), os.path.join(trash_folder, file_name))
        except ValueError:
            print(f"Skipping file with unexpected format: {file_name}")


# Step 2: Check for completeness of documents for each SIREN and move incomplete SIRENs to Trash
complete_count = 0
incomplete_count = 0

for siren, years in siren_documents.items():
    siren_files = [f for f in os.listdir(folder_path) if f.startswith(siren)]
    
    if years == target_years:
        complete_count += 1
    else:
        incomplete_count += 1
        # Move all files for this incomplete SIREN to the trash folder
        for file_name in siren_files:
            shutil.move(os.path.join(folder_path, file_name), os.path.join(trash_folder, file_name))

# Print results
print(f"Number of COMPLETE SIRENs (2016-2023): {complete_count}")
print(f"Number of incomplete SIRENs (2016-2023): {incomplete_count}")

