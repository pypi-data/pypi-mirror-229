import os.path

import cv2
import opnous2

from scripts.depth_image import DepthImage


def test_conversion():
    raw_file = os.path.join(os.getcwd(), 'data/DCG2202205000003_2023-01-26T11_15_17_280000.raw')

    target_rust_depth = os.path.join(os.getcwd(), 'data/rust.tiff')
    target_python_depth = os.path.join(os.getcwd(), 'data/python.tiff')
    if os.path.exists(target_rust_depth):
        os.remove(target_rust_depth)
    if os.path.exists(target_python_depth):
        os.remove(target_python_depth)

    # Convert with Python:
    di = DepthImage()
    di.convert_image(raw_file)
    di.write_exercise(os.path.join(os.getcwd(), 'data/python'))

    opnous2.convert_file(
        raw_file,
        target_rust_depth,
        os.path.join(os.getcwd(), 'data/rust.png'),
        0.015, 0.0
    )

    python_infrared_img = cv2.imread(os.path.join(os.getcwd(), 'data/python.png'))
    assert python_infrared_img.shape == (320, 240, 3)

    rust_infrared_img = cv2.imread(os.path.join(os.getcwd(), 'data/rust.png'))
    assert rust_infrared_img.shape == (320, 240, 3)

    python_depth_img = cv2.imread(os.path.join(os.getcwd(), 'data/python.tiff'), cv2.IMREAD_UNCHANGED)
    assert python_depth_img.shape == (320, 240)

    rust_depth_img = cv2.imread(os.path.join(os.getcwd(), 'data/rust.tiff'), cv2.IMREAD_UNCHANGED)
    assert rust_depth_img.shape == (320, 240)

    # Calc diff between Rust and Python:
    d = python_depth_img - rust_depth_img

    assert d.min() > -0.5, 'Difference more then rounding error!'
    assert d.max() < 0.5, 'Difference more then rounding error!'

    assert d.max != 0, 'Must always be error since Python is not rounding!'
