# model.py

from typing import Optional
import os

import cv2
import numpy as np

from lpr.base import dataset

__all__ = [
    "load_model",
    "k_nearest_model"
]

def load_nupy_text_file(file: str) -> np.array:
    """
    Loads the content of the file.

    :param file: The file to load the text from

    :return: The value to return the text with
    """

    return np.loadtxt(file, np.float32)
# end load_nupy_text_file

def load_model(
        flattened: Optional[str] = None,
        classifications: Optional[str] = None
) -> cv2.ml.KNearest:
    """
    Loads the training data.

    :param flattened: The file for the images' data.
    :param classifications: The file for the classifications' data.

    :return: The k nearest neighbour model.
    """

    location = dataset()

    if (flattened is None) or (not os.path.exists(flattened)):
        flattened = f"{location}\\flattened_images.txt"
    # end if

    if (classifications is None) or (not os.path.exists(classifications)):
        classifications = f"{location}\\classifications.txt"
    # end if

    npa_classifications = load_nupy_text_file(file=classifications)
    npa_flattened_images = load_nupy_text_file(file=flattened)

    npa_classifications = npa_classifications.reshape(
        (npa_classifications.size, 1)
    )

    model = cv2.ml.KNearest_create()

    model.setDefaultK(1)
    model.train(
        npa_flattened_images, cv2.ml.ROW_SAMPLE,
        npa_classifications
    )

    return model
# end load_model

k_nearest_model = load_model()