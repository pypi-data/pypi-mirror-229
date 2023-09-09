import os
import pickle
import time
from functools import wraps
import random
from typing import List

import opnous2

from scripts.depth_image import DepthImage


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__} Took {total_time:.9f} seconds')
        return result

    return timeit_wrapper


@timeit
def run_rust_function(file_list:List[str]):
    for index, image in enumerate(file_list):
        opnous2.convert_file(
            image,
            f'/tmp/rust_{index}.tiff',
            f'/tmp/rust_{index}.png',
            0.02,
            0.5,
            )


@timeit
def run_python_function(file_list:List[str]):
    for i in file_list:
        di = DepthImage()
        di.convert_image(i)
        di.write_exercise('/tmp/')


def scan_files(path: str) -> List[str]:
    raw_files: List[str] = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.raw'):
                raw_files.append(os.path.join(root, file))

    return raw_files


if __name__ == '__main__':
    print('start')

    N_SAMPLES = 100
    READ_IMAGES = False

    if READ_IMAGES:
        raw_file_list = scan_files(os.path.expanduser('~/deepcare/data-preperation/data/raw/sync/'))

        # Get random elements from list:
        raw_file_list_short = random.sample(raw_file_list, N_SAMPLES)

        with open('samples.pkl', 'wb') as f:
            pickle.dump(raw_file_list_short, f)
    else:
        with open('samples.pkl', 'rb') as f:
            raw_file_list_short = pickle.load(f)

    #with open(file_path, 'rb') as f:
    #    byte_buffer = f.read()

    # opnous2.calc_something(byte_buffer[0:1])

    try:
        print('RUST')
        run_rust_function(raw_file_list_short)
    except Exception as e:
        print(f'RUST FAIL!\n{e}')

    print('PYTHON')
    run_python_function(raw_file_list_short)
