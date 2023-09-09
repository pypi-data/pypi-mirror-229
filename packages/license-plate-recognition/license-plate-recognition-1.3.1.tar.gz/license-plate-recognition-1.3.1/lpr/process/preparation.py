# preparation.py

import cv2
import numpy as np

from lpr.definition import Dimensions

__all__ = [
    "preprocess",
    "grayscale_image",
    "maximize_contrast"
]

def preprocess(image: np.array) -> np.ndarray:
    """
    Operates the preprocessing of the image before the search for the lp

    :param image: The original image object.
    """

    img_grayscale = grayscale_image(image=image)
    img_max_contrast_grayscale = maximize_contrast(image=img_grayscale)

    img_blurred = cv2.GaussianBlur(
        img_max_contrast_grayscale,
        Dimensions.GAUSSIAN_SMOOTH_FILTER_SIZE, 0
    )

    return cv2.adaptiveThreshold(
        img_blurred, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, Dimensions.ADAPTIVE_THRESH_BLOCK_SIZE,
        Dimensions.ADAPTIVE_THRESH_WEIGHT
    )
# end preprocess

def grayscale_image(image: np.array) -> np.array:
    """
    Operates the preprocessing of the image before the search for the lp

    :param image: The original image object.
    """

    return cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2HSV))[-1]
# end grayscale_image

def maximize_contrast(image: np.array) -> np.array:
    """
    Operates the preprocessing of the image before the search for the lp

    :param image: The black and white image.
    """

    structure = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    img_top_hat = cv2.morphologyEx(image, cv2.MORPH_TOPHAT, structure)
    img_black_hat = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, structure)

    img_grayscale_top_hat = cv2.add(image, img_top_hat)
    img_max_contrast = cv2.subtract(img_grayscale_top_hat, img_black_hat)

    return img_max_contrast
# end maximize_contrast