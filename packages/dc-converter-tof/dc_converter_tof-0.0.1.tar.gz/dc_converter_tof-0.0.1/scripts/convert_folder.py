import datetime
import multiprocessing
import os
import shutil
from itertools import repeat
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


if __name__ == '__main__':
    # folder_to_convert = os.path.expanduser('~/deepcare/data-preperation/data/learn/headtracking/')
    # folder_to_convert = os.path.expanduser('/home/timo/tmp/Raham_office/')

    # folder_to_convert = os.path.expanduser('~/deepcare/data-preperation/data/learn/table_linear/')
    folder_to_convert = os.path.expanduser('~/deepcare/data-preperation/data/learn/table/')
    # folder_to_convert = os.path.expanduser('~/deepcare/data-preperation/data/learn/exercises/')
    # folder_to_convert = os.path.expanduser('/home/timo/tmp/work/')

    print(f'Converting all files in "{folder_to_convert}".')

    # target_folder = os.path.expanduser('/home/timo/deepcare/data-preperation/data/learn/headtracking/test/')
    target_folder = None  # <-- inplace

    cache_folder = os.path.expanduser('~/tmp/converted')

    print('convert')
    start = datetime.datetime.now()

    if target_folder:
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

        files = scan_files(folder_to_convert, '.raw')

        # Create a pool of worker processes to convert the files to target folder:
        with(multiprocessing.Pool(multiprocessing.cpu_count())) as p:
            p.starmap(convert_to_folder, zip(files, repeat(cache_folder)))

        converted_files = scan_files(cache_folder, '.tiff')

        # Copy all file from cache folder to target folder:
        print('copy')
        with(multiprocessing.Pool(multiprocessing.cpu_count())) as p:
            p.starmap(copy_converted_files, zip(files, repeat(target_folder)))

        dt = datetime.datetime.now() - start

        print(f'Conversion of {len(files)} took {dt}.')

    # Convert inplace:
    else:
        files = scan_files(folder_to_convert, '.raw')

        # Create a pool of worker processes to convert the files to target folder:
        with(multiprocessing.Pool(multiprocessing.cpu_count())) as p:
            p.map(convert_file_inplace, files)

    dt = datetime.datetime.now() - start

    if len(files):
        print(f'Conversion of {len(files)} took {dt}.')
    else:
        print('ERROR, now files converted!')
