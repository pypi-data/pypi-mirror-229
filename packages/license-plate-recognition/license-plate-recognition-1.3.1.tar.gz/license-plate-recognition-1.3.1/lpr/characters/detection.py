# detection.py

from typing import Optional, List, Tuple, TypeVar, Iterable
import math

import cv2
import numpy as np

from lpr.characters import PossibleChar
from lpr.definition import AreasDimensions, Colors
from lpr.plates import Plate
from lpr.process.model import k_nearest_model

__all__ = [
    "detect_plate_chars",
    "check_possible_char",
    "find_matching_chars",
    "distance_between_chars"
]

_P = TypeVar("_P", Iterable[Plate], Iterable[Plate])

def detect_plate_chars(possible_plates: _P) -> _P:
    """
    operates the chars' detection on the found license plates

    :param possible_plates: The possible plates list.

    :return: possible_plates_lst: The possible plates list.
    """

    for possible_plate in possible_plates:
        possible_chars = find_possible_chars_in_plate(possible_plate.thresh)
        matching_chars_container = find_matching_chars(possible_chars)

        if len(matching_chars_container) == 0:
            possible_plate.chars = ""

            continue
        # end if

        for i in range(0, len(matching_chars_container)):
            matching_chars_container[i].sort(
                key=lambda matching_char: matching_char.x_center
            )
            matching_chars_container[i] = (
                remove_inner_overlapping_chars(matching_chars_container[i])
            )
        # end for

        longest_chars_length = 0
        i = 0

        for i in range(0, len(matching_chars_container)):
            longest_chars_length = max(
                longest_chars_length, len(matching_chars_container[i])
            )
        # end for

        possible_plate.chars = recognize_chars_in_plate(
            possible_plate.thresh, matching_chars_container[i]
        )
    # end for

    return possible_plates
# end detect_plate_chars

def find_possible_chars_in_plate(image: np.array) -> List[PossibleChar]:
    """
    Operates the preprocessing of the image before the search for the lp

    :param image: The thresh image object.

    :returns possible_chars_lst: The list of possible chars in the license plate.
    """

    possible_chars = []

    contours, npa_hierarchy = cv2.findContours(
        image.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:
        possible_char = PossibleChar(contour)

        if check_possible_char(possible_char):
            possible_chars.append(possible_char)
        # end if
    # end if

    return possible_chars
# end find_possible_chars_in_plate

def check_possible_char(possible_char: PossibleChar) -> bool:
    """
    Operates the preprocessing of the image before the search for the lp

    :param possible_char: The possible char.

    :returns: The value to set the char as valid.
    """

    return (
        possible_char.area > AreasDimensions.MIN_PIXEL_AREA and
        possible_char.width > AreasDimensions.MIN_PIXEL_WIDTH and
        possible_char.height > AreasDimensions.MIN_PIXEL_HEIGHT and
        (
            AreasDimensions.MIN_ASPECT_RATIO <
            possible_char.aspect_ratio <
            AreasDimensions.MAX_ASPECT_RATIO
        )
    )
# end check_if_possible_char

def find_matching_chars(possible_chars: List[PossibleChar]) -> List[List[PossibleChar]]:
    """
    Natches the chars list in the list.

    :param possible_chars: The possible list of chars.

    :return: The processed list of chars.
    """

    matching_chars_container = []

    for possible_char in possible_chars:
        matching_chars = matching_possible_chars(
            possible_char, possible_chars
        )

        matching_chars.append(possible_char)

        if (
            len(matching_chars) <
            AreasDimensions.MIN_NUMBER_OF_MATCHING_CHARS
        ):
            continue
        # end if

        matching_chars_container.append(matching_chars)

        for recursive_matching_chars in find_matching_chars(
            list(set(possible_chars) - set(matching_chars))
        ):
            matching_chars_container.append(recursive_matching_chars)
        # end for

        break
    # end for

    return matching_chars_container
# end find_list_of_lists_of_matching_chars

def matching_possible_chars(
        possible_char: PossibleChar, possible_chars: List[PossibleChar]
) -> List[PossibleChar]:
    """
    Operates the preprocessing of the image before the search for the lp

    :param possible_char: The possible char.
    :param possible_chars: The possible list of chars.

    :returns: The value to set the char as valid.
    """

    matching_chars = []

    for possible_matching_char in possible_chars:
        if possible_matching_char == possible_char:
            continue
        # end if

        chars_dis = distance_between_chars(
            possible_char, possible_matching_char
        )
        chars_angle = angle_between_chars(
            possible_char, possible_matching_char
        )

        area_change = float(
            abs(possible_matching_char.area - possible_char.area)
        ) / float(possible_char.area)

        width_change = float(
            abs(possible_matching_char.width - possible_char.width)
        ) / float(possible_char.width)

        height_change = float(
            abs(possible_matching_char.height - possible_char.height)
        ) / float(possible_char.height)

        max_chars_distance = (
            possible_char.diagonal_size *
            AreasDimensions.MAX_DIAG_SIZE_MULTIPLE_AWAY
        )

        if (
            chars_dis < max_chars_distance and
            chars_angle < AreasDimensions.MAX_ANGLE_BETWEEN_CHARS and
            area_change < AreasDimensions.MAX_CHANGE_IN_AREA and
            width_change < AreasDimensions.MAX_CHANGE_IN_WIDTH and
            height_change < AreasDimensions.MAX_CHANGE_IN_HEIGHT
        ):

            matching_chars.append(possible_matching_char)
        # end if
    # end for

    return matching_chars  # return result
# end find_list_of_matching_chars

def distance_between_chars(first_char: PossibleChar, second_char: PossibleChar) -> float:
    """
    Uses Pythagorean theorem to calculate distance between two chars

    :param first_char: The fist char.
    :param second_char: The second Char.

    :return: The distance between the chars.
    """

    x = abs(first_char.x_center - second_char.x_center)
    y = abs(first_char.y_center - second_char.y_center)

    return math.sqrt((x ** 2) + (y ** 2))
# end distance_between_chars

def angle_between_chars(first_char: PossibleChar, second_char: PossibleChar) -> float:
    """
    Uses Pythagorean theorem to calculate distance between two chars

    :param first_char: The fist char.
    :param second_char: The second Char.

    :return: The distance between the chars.
    """

    adjustment = float(
        abs(first_char.x_center - second_char.x_center)
    )

    if adjustment != 0.0:
        rad_angle = math.atan(
            float(abs(first_char.y_center - second_char.y_center)) /
            adjustment
        )

    else:
        rad_angle = 1.5708
    # end if

    return rad_angle * (180.0 / math.pi)
# end angle_between_chars

def remove_inner_overlapping_chars(matching_chars: List[PossibleChar]) -> List[PossibleChar]:
    """
    Removes the inner overlapping of the char.

    :param matching_chars: The list of matching chars.

    :return: The list of matching chars.
    """

    matching_chars_inner_removed = list(matching_chars)

    for current_char in matching_chars:
        for other_char in matching_chars:
            if current_char != other_char:
                if (
                    distance_between_chars(current_char, other_char) <
                    (
                        current_char.diagonal_size *
                        AreasDimensions.MIN_DIAG_SIZE_MULTIPLE_AWAY
                    )
                ):
                    if current_char.area < other_char.area:
                        if current_char in matching_chars_inner_removed:
                            matching_chars_inner_removed.remove(current_char)
                        # end if

                    else:
                        if other_char in matching_chars_inner_removed:
                            matching_chars_inner_removed.remove(other_char)
                        # end if
                    # end if
                # end if
            # end if
        # end for
    # end for

    return matching_chars_inner_removed
# end remove_inner_overlapping_chars

def recognize_chars_in_plate(
        image: np.array,
        possible_chars: List[PossibleChar],
        color: Optional[Tuple[int, int, int]] = Colors.GREEN,
        model: Optional[cv2.ml.KNearest_create] = None
) -> str:
    """
    Recognizes the chars in the plate

    :param possible_chars: The list of matching chars.
    :param image: The thresh image object.
    :param color: The color to write the license plate in.
    :param model: The model for the detection.

    :return: The list of matching chars.
    """

    if model is None:
        model = k_nearest_model
    # end if

    chars = ""

    height, width = image.shape

    img_thresh_color = np.zeros((height, width, 3), np.uint8)

    possible_chars.sort(key=lambda matching_char: matching_char.x_center)

    cv2.cvtColor(image, cv2.COLOR_GRAY2BGR, img_thresh_color)

    for current_char in possible_chars:
        pt1 = (current_char.x_position, current_char.y_position)
        pt2 = (
            (current_char.x_position + current_char.width),
            (current_char.y_position + current_char.height)
        )

        cv2.rectangle(img_thresh_color, pt1, pt2, color, 2)

        img_roi = image[
            current_char.y_position: (
                current_char.y_position + current_char.height
            ),
            current_char.x_position: (
                current_char.x_position + current_char.width
            )
        ]

        img_roi_resized = cv2.resize(
            img_roi, (
                AreasDimensions.RESIZED_CHAR_IMAGE_WIDTH,
                AreasDimensions.RESIZED_CHAR_IMAGE_HEIGHT
            )
        )

        npa_roi_resized = img_roi_resized.reshape(
            (
                1, AreasDimensions.RESIZED_CHAR_IMAGE_WIDTH *
                AreasDimensions.RESIZED_CHAR_IMAGE_HEIGHT
            )
        )

        _, npa_results, neigh_resp, dists = model.findNearest(
            np.float32(npa_roi_resized), k=1
        )

        chars += str(chr(int(npa_results[0][0])))
    # end for

    return chars
# end recognize_chars_in_plate