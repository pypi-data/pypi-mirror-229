import os
from pathlib import Path
from typing import Any, Dict, Tuple

from scripts.depth_image_layer import DepthImageLayer


class WrongRawImageSize(Exception):
    pass


class RawFileNotFound(Exception):
    pass


class DepthImage:

    def __init__(self) -> None:

        self.depth_image = DepthImageLayer()  # Depth image raw part
        self.depth_image_fine = DepthImageLayer()  # Depth image fine part
        self.pixel_status = DepthImageLayer()  # Pixel status
        self.infrared_image = DepthImageLayer()  # Infrared image
        self.background_image = DepthImageLayer()  # Background image

        self.file_name = None

    def convert_image(self, file_path: str | Path):

        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            raise RawFileNotFound

        with open(file_path, 'rb') as f:
            self.convert_image_buffer(f.read())

        self.file_name = Path(file_path).stem

    def convert_image_buffer(self, raw_data: bytes):
        """ Convert an image from raw to all layers. """

        # Check image size for Opnous 8505C:
        if len(raw_data) != 345600:
            raise WrongRawImageSize

        self.reset()

        n: int
        for n, j in enumerate(range(0, len(raw_data), int(320 * (12 / 8)))):

            for i in range(j, j + int(320 * (12 / 8)), 6):

                v = int.from_bytes(
                    raw_data[i:i + 6], byteorder='little', signed=False)

                # Depth:
                if n % 3 == 0:
                    self.add_depth_pixel(v)
                # Fine depth + Status + Background:
                elif (n + 2) % 3 == 0:
                    self.add_mixed_pixel(v)
                # IR:
                elif (n + 1) % 3 == 0:
                    self.add_ir_pixel(v)

        # Combine course and fine depth images:
        self.depth_image.add_image(self.depth_image_fine.arr)

        # Scale to mm:
        self.depth_image.scale_by_factor(3.59704310345)

        # Rotate to be heads up:
        self.depth_image.rotate()
        self.infrared_image.rotate()
        self.pixel_status.rotate()

    def add_ir_pixel(self, v):
        # Always 4 pixel inverse order:
        p4 = ((v & 0xfff000000000) >> (3 * 12)) * 16
        p3 = ((v & 0x000fff000000) >> (2 * 12)) * 16
        p2 = ((v & 0x000000fff000) >> (1 * 12)) * 16
        p1 = ((v & 0x000000000fff) >> (0 * 12)) * 16
        self.infrared_image.add_pixel(p1)
        self.infrared_image.add_pixel(p2)
        self.infrared_image.add_pixel(p3)
        self.infrared_image.add_pixel(p4)

    def add_mixed_pixel(self, v):
        # Status: 0c0
        p4 = ((v & 0x0c0000000000) >> ((3 * 12) + 6))
        p3 = ((v & 0x0000c0000000) >> ((2 * 12) + 6))
        p2 = ((v & 0x0000000c0000) >> ((1 * 12) + 6))
        p1 = ((v & 0x0000000000c0) >> ((0 * 12) + 6))
        # Status: 0 normal, 1 underexposure, 2 overexposure, 3 bad pixel
        self.pixel_status.add_pixel(p1)
        self.pixel_status.add_pixel(p2)
        self.pixel_status.add_pixel(p3)
        self.pixel_status.add_pixel(p4)
        # Background:
        p4 = ((v & 0x03f000000000) >> ((3 * 12) + 0))
        p3 = ((v & 0x00003f000000) >> ((2 * 12) + 0))
        p2 = ((v & 0x00000003f000) >> ((1 * 12) + 0))
        p1 = ((v & 0x00000000003f) >> ((0 * 12) + 0))
        self.background_image.add_pixel(p1)
        self.background_image.add_pixel(p2)
        self.background_image.add_pixel(p3)
        self.background_image.add_pixel(p4)
        # Fine depth:
        p4 = ((v & 0xf00000000000) >> ((3 * 12) + 8))
        p3 = ((v & 0x000f00f00000) >> ((2 * 12) + 8))
        p2 = ((v & 0x000000f00000) >> ((1 * 12) + 8))
        p1 = ((v & 0x000000000f00) >> ((0 * 12) + 8))
        self.depth_image_fine.add_pixel(p1)
        self.depth_image_fine.add_pixel(p2)
        self.depth_image_fine.add_pixel(p3)
        self.depth_image_fine.add_pixel(p4)

    def add_depth_pixel(self, v):
        # Always 4 pixel inverse order:
        p4 = ((v & 0xfff000000000) >> (3 * 12)) * 16
        p3 = ((v & 0x000fff000000) >> (2 * 12)) * 16
        p2 = ((v & 0x000000fff000) >> (1 * 12)) * 16
        p1 = ((v & 0x000000000fff) >> (0 * 12)) * 16
        self.depth_image.add_pixel(p1)
        self.depth_image.add_pixel(p2)
        self.depth_image.add_pixel(p3)
        self.depth_image.add_pixel(p4)

    def reset(self):
        # Enable reuse of DepthImage object for multiple images:
        self.depth_image.reset()
        self.depth_image_fine.reset()
        self.pixel_status.reset()
        self.infrared_image.reset()
        self.background_image.reset()

    def write_all(self, target_folder: str):

        # Write to files:
        # TODO: Save runtime: self.dp.write_to_file(os.path.join(target_folder, 'depth.png'))
        self.depth_image.write_to_file(os.path.join(target_folder, 'depth.tiff'))
        # TODO: Save runtime: self.dp.write_to_csv(os.path.join(target_folder, 'depth.csv'))
        self.infrared_image.write_to_file(os.path.join(target_folder, 'infrared.png'))
        self.background_image.write_to_file(os.path.join(target_folder, 'infrared_bg.png'))
        self.pixel_status.write_to_file(os.path.join(target_folder, 'sensor_status.png'))

        self.store_color_map(self.depth_image, os.path.join(target_folder, 'depth_color_map.png'),
                             (200.0, 12000.0),
                             {'Title': 'Depth as Heatmap',
                              'Copyright': 'Deep Care GmbH',
                              'Description': 'Depth as Heatmap'
                              })

        self.store_color_map(self.infrared_image, os.path.join(target_folder, 'infrared_color_map.png'),
                             (200.0, 25000.0),
                             {'Title': 'Infrared image',
                              'Copyright': 'Deep Care GmbH',
                              'Description': 'Infrared image'
                              })
        self.store_color_map(self.pixel_status, os.path.join(target_folder, 'sensor_status_color_map.png'),
                             (0.0, 3.0),
                             {'Title': 'Pixel Status',
                              'Copyright': 'Deep Care GmbH',
                              'Description': 'Pixel Status (0 normal, 1 underexposure, 2 overexposure, 3 bad pixel)'
                              })

    def write_exercise(self, target_folder: str):

        # Write to files:
        self.depth_image.write_to_file(os.path.join(target_folder, target_folder + '.tiff'))
        self.infrared_image.write_to_file(os.path.join(target_folder, target_folder + '.png'))




    def write_tiff(self, target_folder: str):
        self.depth_image.write_to_file(os.path.join(target_folder, 'depth.tiff'))

    def write_infrared_colored(self, target_folder: str):
        self.store_color_map(self.infrared_image, os.path.join(target_folder, 'infrared_color_map.png'),
                             (200.0, 25000.0),
                             {'Title': 'Infrared image',
                              'Copyright': 'Deep Care GmbH',
                              'Description': 'Infrared image'
                              })

    @staticmethod
    def store_color_map(dp, file_name: str, value_limits: Tuple[float, float], metadata: Dict[str, Any] = None):
        # Lazy load, not needed for writing only tiff:
        import matplotlib.pyplot as plt

        if metadata is None:
            metadata = {}
        plt.clf()
        plt.imshow(dp.arr, clim=value_limits)
        plt.colorbar()
        plt.savefig(file_name, bbox_inches="tight",
                    pad_inches=0.02, dpi=250,
                    metadata=metadata)
