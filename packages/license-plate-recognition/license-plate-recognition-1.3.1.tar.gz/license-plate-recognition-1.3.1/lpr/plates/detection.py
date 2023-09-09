# detection.py

import math
from typing import List, Iterable, TypeVar

import numpy as np
import cv2

from lpr.process.preparation import preprocess
from lpr.characters import (
    PossibleChar, find_matching_chars, detect_plate_chars,
    check_possible_char, distance_between_chars
)
from lpr.plates import Plate

__all__ = [
    "read_image_plates",
    "read_plates",
    "find_image_plates"
]

def find_image_plates(image: np.array) -> List[Plate]:
    """
    Operates the preprocessing of the image before the search for the lp

    :param image: The original image object.
    """

    possible_plates = []

    img_thresh_scene = preprocess(image)

    possible_chars = find_possible_chars(img_thresh_scene)

    matching_chars_container = find_matching_chars(
        possible_chars
    )

    for matching_chars in matching_chars_container:
        possible_plate = extract_plate(image, matching_chars)

        if possible_plate.plate is not None:
            possible_plates.append(possible_plate)
        # end if
    # end for

    return possible_plates
# end read_image_plates

_P = TypeVar("_P", Iterable[Plate], Iterable[Plate])

def read_plates(plates: _P) -> _P:
    """
    Operates the preprocessing of the image before the search for the lp

    :param plates: The plate objects.
    """

    return detect_plate_chars(plates)
# end read_image_plates

def read_image_plates(image: np.array) -> List[Plate]:
    """
    Operates the preprocessing of the image before the search for the lp

    :param image: The original image object.
    """

    return read_plates(find_image_plates(image))
# end read_image_plates

def find_possible_chars(image: np.array) -> List[PossibleChar]:
    """
    Operates the preprocessing of the image before the search for the lp

    :param image: The thresh image object.

    :returns possible_chars_lst: The list of possible chars in the license plate.
    """

    contours, npa_hierarchy = cv2.findContours(
        image.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )

    possible_chars = []

    for contour in contours:
        possible_char = PossibleChar(contour)

        if check_possible_char(possible_char):
            possible_chars.append(possible_char)
        # end if
    # end for

    return possible_chars
# end find_possible_chars

# noinspection PyShadowingNames
def extract_plate(image: np.array, matching_chars: List[PossibleChar]) -> Plate:
    """
    Operates the preprocessing of the image before the search for the lp

    :param image: The original image object.
    :param matching_chars: The chars list.

    :returns possible_chars_lst: The list of possible chars in the license plate.
    """

    matching_chars.sort(
        key=lambda matching_char: matching_char.x_center
    )

    plate_center_x = (
        matching_chars[0].x_center +
        matching_chars[len(matching_chars) - 1].x_center
    ) / 2.0
    plate_center_y = (
        matching_chars[0].y_center +
        matching_chars[len(matching_chars) - 1].y_center
    ) / 2.0

    pt_plate_center = (plate_center_x, plate_center_y)

    plate_width = int(
        (
            matching_chars[len(matching_chars) - 1].x_position +
            matching_chars[len(matching_chars) - 1].width -
            matching_chars[0].x_position
        ) * 1.3
    )

    total_char_heights = 0

    for matching_char in matching_chars:
        total_char_heights = (
            total_char_heights + matching_char.height
        )
    # end for

    average_char_height = total_char_heights / len(matching_chars)
    plate_height = int(average_char_height * 1.5)

    opposite = (
        matching_chars[len(matching_chars) - 1].y_center -
        matching_chars[0].y_center
    )
    hypotenuse = distance_between_chars(
        matching_chars[0], matching_chars[len(matching_chars) - 1]
    )

    correction_angle_in_rad = math.asin(opposite / hypotenuse)
    correction_angle_in_deg = correction_angle_in_rad * (180.0 / math.pi)

    location = cv2.boxPoints(
        (
            tuple(pt_plate_center),
            (plate_width, plate_height),
            correction_angle_in_deg
        )
    ).astype(int)

    rotation_matrix = cv2.getRotationMatrix2D(
        tuple(pt_plate_center), correction_angle_in_deg, 1.0
    )
    height, width, num_channels = image.shape

    img_rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
    img_cropped = cv2.getRectSubPix(
        img_rotated, (plate_width, plate_height), tuple(pt_plate_center)
    )

    thresh = preprocess(img_cropped)

    thresh = cv2.resize(thresh, (0, 0), fx=1.6, fy=1.6)
    _, thresh = cv2.threshold(
        thresh, 0.0, 255.0,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )

    return Plate(
        image=image, plate=img_cropped,
        location=location, thresh=thresh
    )
# end extract_plate