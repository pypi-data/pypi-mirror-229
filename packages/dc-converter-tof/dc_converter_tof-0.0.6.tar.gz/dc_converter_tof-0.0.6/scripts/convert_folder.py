import os
import shutil
from typing import List

from opnous2 import opnous2


def scan_files(path: str, extension: str) -> List[str]:
    """ Find all raw files in folder. """
    raw_files: List[str] = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                raw_files.append(os.path.join(root, file))

    return raw_files


def convert_file_inplace(raw_file_name: str):
    # Remove 'raw' from filename:
    name_wo_extension = raw_file_name[0:-3]

    # Add target names:
    depth_file_name = name_wo_extension + 'tiff'
    infrared_file_name = name_wo_extension + 'png'

    if not os.path.exists(depth_file_name) and not os.path.exists(infrared_file_name):
        opnous2.convert_file(raw_file_name, depth_file_name, infrared_file_name, 0.015, 0.0)


def convert_to_folder(raw_file_name: str, target_folder: str):
    # Extract file name and remove 'raw':
    name_wo_extension = os.path.basename(raw_file_name)[0:-3]

    # Add target names:
    depth_file_name = os.path.join(target_folder, name_wo_extension + 'tiff')
    infrared_file_name = os.path.join(target_folder, name_wo_extension + 'png')

    if not os.path.exists(depth_file_name) and not os.path.exists(infrared_file_name):
        print(f'Converting {raw_file_name} to {depth_file_name} and {infrared_file_name}')
        opnous2.convert_file(raw_file_name, depth_file_name, infrared_file_name, 0.015, 0.0)


def copy_converted_files(target_file: str, target_folder: str):
    # Get filename without extension:
    name_wo_extension = os.path.basename(target_file)[0:-3]
    inplace_folder = os.path.dirname(target_file)
    target_tiff = os.path.join(inplace_folder, name_wo_extension + 'tiff')
    target_png = os.path.join(inplace_folder, name_wo_extension + 'png')
    if not os.path.exists(target_tiff) or not os.path.exists(target_png):
        shutil.copyfile(os.path.join(target_folder, name_wo_extension + 'tiff'), target_tiff)
        shutil.copyfile(os.path.join(target_folder, name_wo_extension + 'png'), target_png)
