import multiprocessing
import os
import pickle
import random
from itertools import repeat
from typing import List

import cv2
import mediapipe
import numpy as np
import opnous2
import pandas as pd

mp_face_mesh = mediapipe.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)


def run_rust_function(file_list: List[str], alpha=0.02, beta=0.5):

    tiff_file_list = [f'/tmp/rust_{index}.tiff' for index, _ in enumerate(file_list)]
    png_file_list = [f'/tmp/rust_{index}.png' for index, _ in enumerate(file_list)]

    with(multiprocessing.Pool(multiprocessing.cpu_count())) as p:
        p.starmap(opnous2.convert_file, zip(raw_file_list_short, tiff_file_list, png_file_list,repeat(a), repeat(b)))
    # for index, image in enumerate(file_list):
    #     opnous2.convert_file(
    #         image,
    #         f'/tmp/rust_{index}.tiff',
    #         f'/tmp/rust_{index}.png',
    #         alpha,
    #         beta,
    #     )


def scan_files(path: str) -> List[str]:
    raw_files: List[str] = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.raw'):
                raw_files.append(os.path.join(root, file))

    return raw_files


def check_images(n_images):
    success = 0

    for i in range(n_images):
        image = cv2.imread(f'/tmp/rust_{i}.png')
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # To improve performance
        image.flags.writeable = False

        # Get the result
        results = face_mesh.process(image)

        if results.multi_face_landmarks:
            success += 1

    return success


if __name__ == '__main__':
    print('start')

    N_SAMPLES = 1000
    READ_IMAGES = True

    if READ_IMAGES:
        raw_file_list = scan_files(os.path.expanduser('~/deepcare/data-preperation/data/learn/exercises/'))

        # Get random elements from list:
        raw_file_list_short = random.sample(raw_file_list, N_SAMPLES)

        with open('samples.pkl', 'wb') as f:
            pickle.dump(raw_file_list_short, f)
    else:
        with open('samples.pkl', 'rb') as f:
            raw_file_list_short = pickle.load(f)

    a_l = []
    b_l = []
    success_l = []

    # n_iter = 0
    # for a in np.arange(0.01, 0.02, 0.001):
    #     for b in np.arange(0, 100.0, 10):
    #         n_iter += 1
    # print(f'Number of iterations: {n_iter}')


    for a in np.arange(0.01, 0.025, 0.0001):
        b = 0.0
        try:
            run_rust_function(raw_file_list_short, a, b)
        except Exception as e:
            print(f'RUST FAIL!\n{e}')

        success = check_images(N_SAMPLES)

        print(f'Success: {success / N_SAMPLES * 100:4.2f}% A: {a:5.4f}, B: {b:3.2f}')

        a_l.append(a)
        b_l.append(b)
        success_l.append(float(success) / N_SAMPLES * 100)

    df = pd.DataFrame({'a': a_l, 'b': b_l, 'success': success_l})
    df.to_excel('success.xlsx')
