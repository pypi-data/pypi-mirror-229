# visualize.py

import datetime as dt
from typing import Optional, Union, Tuple
import warnings

import numpy as np
import cv2

from lpr.definition import Colors
from lpr.plates import Plate

__all__ = [
    "write_plate_frame",
    "write_plate_chars",
    "create_image_window",
    "resize_image"
]

def get_scale_percent(scaler: float, origin_width: int) -> float:
    """
    Scales the image window dimensions to fit the screen.

    :param scaler: The value to scale.
    :param origin_width: The original value.

    :return: scale_percent: The scaling value to scale the window size with.
    """

    if origin_width <= 500:
        scaler += 150

    elif 500 < origin_width <= 1000:
        scaler += 70

    elif 1000 < origin_width <= 1800:
        scaler += 75

    elif origin_width > 1800:
        scaler += 50
    # end if

    return scaler
# end get_scale_percent

def resize_image(
        image: np.array,
        width: Optional[int] = None,
        height: Optional[int] = None
) -> np.ndarray:
    """
    Creates the image window.

    :param image: The original image object.
    :param width: The width of the window.
    :param height: The height of the window.
    """

    interpolation = cv2.INTER_CUBIC

    ratio = int(image.shape[0]) / int(image.shape[1])

    if (width is not None) and (height is None):
        height = int(ratio * width)

    elif (height is not None) and (width is None):
        width = int(ratio * height)

    elif (height is not None) and (width is not None):
        image = cv2.resize(
            image, dsize=(width, height),
            interpolation=cv2.INTER_CUBIC
        )

    else:
        orig_height = image.shape[1]
        orig_width = image.shape[0]

        width = int(orig_height * get_scale_percent(0, orig_width) / 100)
        height = int(orig_width * get_scale_percent(0, orig_width) / 100)

        interpolation = cv2.INTER_AREA
    # end if

    return cv2.resize(
        image, (width, height), interpolation=interpolation
    )
# end resize_image

def create_image_window(
        image: np.array,
        title: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        timeout: Optional[Union[int, float, dt.timedelta]] = None,
) -> None:
    """
    Creates the image window.

    :param image: The original image object.
    :param title: The title of the window.
    :param timeout: The amount of seconds to keep the window on the screen.
    :param width: The width of the window.
    :param height: The height of the window.
    :param x: The x position of the window.
    :param y: The y position of the window.
    """

    if title is None:
        title = "detection"
    # end if

    if x is None:
        x = 650
    # end if

    if y is None:
        y = 50
    # end if

    if timeout is None:
        timeout = 0
    # end if

    if isinstance(timeout, dt.timedelta):
        timeout = timeout.total_seconds()
    # end if

    resized = resize_image(
        image=image, width=width, height=height
    )

    cv2.imshow(title, resized)
    cv2.moveWindow(title, x, y)
    cv2.waitKey(timeout * 1000)
# end create_image_window

def write_plate_frame(
        image: np.array,
        plate: Plate,
        color: Optional[Tuple[int, int, int]] = Colors.GREEN
) -> np.ndarray:
    """
    Places the text of the found license plate and a rectangle around the detected plate on the image.

    :param image: The original image object.
    :param plate: The plate object to read the data from.
    :param color: The color to write the license plate in.

    :return: Returns the processed image.
    """

    warnings.filterwarnings("ignore")

    cv2.line(
        image, tuple(plate.location[0]),
        tuple(plate.location[1]), color, 2
    )
    cv2.line(
        image, tuple(plate.location[1]),
        tuple(plate.location[2]), color, 2
    )
    cv2.line(
        image, tuple(plate.location[2]),
        tuple(plate.location[3]), color, 2
    )
    cv2.line(
        image, tuple(plate.location[3]),
        tuple(plate.location[0]), color, 2
    )

    warnings.resetwarnings()

    return image
# end write_license_plate_result_on_image

def write_plate_chars(
        image: np.array,
        plate: Plate,
        color: Optional[Tuple[int, int, int]] = Colors.GREEN
) -> np.ndarray:
    """
    Places the text of the found license plate and a rectangle around the detected plate on the image.

    :param image: The original image object.
    :param plate: The plate object to read the data from.
    :param color: The color to write the license plate in.

    :return: Returns the processed image.
    """

    plate_height, plate_width, plate_num_channels = plate.plate.shape

    font_face = cv2.FONT_HERSHEY_SIMPLEX

    font_scale = float(plate_height) / 45.0
    font_thickness = int(font_scale * 2.5)

    # noinspection PyTypeChecker
    cv2.putText(
        image, plate.chars,
        (plate.location[0][0], plate.location[1][1] - 5),
        font_face, font_scale, color, font_thickness
    )

    return image
# end write_license_plate_chars_on_image