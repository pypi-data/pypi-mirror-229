# image.py

import os

import cv2
import numpy as np

__all__ = [
    "configure_image_file_data",
    "read_image_file",
    "save_image"
]

def read_image_file(path: str) -> np.ndarray:
    """
    Reads the image data from the given file path.

    :param path: The file to read the image data from.

    :return: The image object.
    """

    return cv2.imread(path)
# end read_image_file

def save_image(image: np.ndarray, path: str) -> None:
    """
    Saves the image file.

    :param image: The image to save.
    :param path: The saving path.
    """

    if not os.path.exists(location := os.path.split(path)[0]):
        os.makedirs(location)
    # end if

    cv2.imwrite(path, image)
# end save_image

def configure_image_file_data(source: str, image: np.ndarray) -> np.ndarray:
    """
    Reads the image data from the given file path.

    :param source: The file to read the image data from.
    :param image: The image object.

    :return: The image object.
    """

    if (
        isinstance(source, str) and
        not isinstance(image, np.ndarray) and
        os.path.exists(source)
    ):
        return read_image_file(path=source)

    elif image is not None:
        return image

    else:
        raise ValueError(
            "At least one if source and image "
            "parameters must be defined."
        )
    # end if
# end configure_image_file_data