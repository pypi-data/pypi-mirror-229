import numpy as np
import cv2
import pandas as pd


# np.finfo(np.dtype("float32"))
# np.finfo(np.dtype("float64"))


class DepthImageLayer:
    """ Single channel of a ToF image.
        Supported sensor: Opnous 8508C
    """

    def __init__(self):
        self.y_max = 320  # Width
        self.x_max = 240  # Height

        self.y = 0
        self.x = 0

        self.arr = np.zeros((self.x_max, self.y_max),
                            dtype=np.uint16)  # type: ignore

        self.count = 0

    def add_pixel(self, pixel):
        self.arr[self.x, self.y] = pixel
        self.count += 1

        self.y += 1
        if self.y >= self.y_max:
            self.y = 0
            self.x += 1

    def add_image(self, image: np.array):  # type: ignore
        self.arr += image

    def write_to_file(self, name: str):
        cv2.imwrite(name, self.arr)

    def write_to_csv(self, name: str):
        df = pd.DataFrame(self.arr)
        df.to_csv(name, header=False, index=False)

    def rotate(self):
        self.arr = cv2.rotate(self.arr, cv2.ROTATE_90_CLOCKWISE)

    def scale_by_factor(self, factor: float):
        self.arr = self.arr / factor

    def reset(self):
        self.x = 0
        self.y = 0
        self.count = 0

        self.arr = np.zeros((self.x_max, self.y_max),
                            dtype=np.uint16)  # type: ignore
