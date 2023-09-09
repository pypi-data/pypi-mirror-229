# tesseract.py

import os
from typing import (
    Optional, Union, List, Iterable, TypeVar, Tuple
)
from pathlib import Path
import tempfile

import cv2
import numpy as np

from lpr.base import tesseract, run_silent_command
from lpr.plates import Plate
from lpr.definition.colors import Colors

__all__ = [
    "tesseract_read_image_plates",
    "tesseract_find_image_plates",
    "tesseract_read_plates"
]

def order_points(points: np.ndarray) -> np.ndarray:
    """
    Orders the points of the plate.

    :param points: The points of the plate.

    :return: The license plate points.
    """

    rect = np.zeros((4, 2), dtype="float32")

    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]
    rect[2] = points[np.argmax(s)]

    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]
    rect[3] = points[np.argmax(diff)]

    return rect
# end order_points

def transform_points(image: np.ndarray, points: np.ndarray) -> np.ndarray:
    """
    Transforms the points of the plate.

    :param image: The image to process_thresh.
    :param points: The points of the plate.

    :return: The license plate points.
    """

    rect = order_points(points)
    (tl, tr, br, bl) = rect

    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))

    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(height_a), int(height_b))

    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, maxHeight))

    return warped
# end transform_points

def find_image_plates_locations(image: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """
    Detects the plates in the image.

    :param image: The image to process_thresh.

    :return: The images and their plates.
    """

    img = image.copy()
    input_height = image.shape[0]
    input_width = image.shape[1]
    hsv_frame = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    low_yellow = np.array([20, 100, 100])
    high_yellow = np.array([30, 255, 255])
    yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)
    yellow = cv2.bitwise_and(yellow_mask, yellow_mask, mask=yellow_mask)

    k = np.ones((5, 5), np.uint8)
    closing = cv2.morphologyEx(yellow, cv2.MORPH_CLOSE, k)

    contours, hierarchy = cv2.findContours(
        closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    crops = []
    locations = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        if (
                ((h * 6) > w > (2 * h)) and
                (h > (0.1 * w)) and
                ((w * h) > (input_height * input_width * 0.0001))
        ):
            crop_img = image[y:y + h, x - round(w / 10):x]
            crop_img = crop_img.astype('uint8')

            # noinspection PyBroadException
            try:
                hsv_frame = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
                low_bleu = np.array([100, 150, 0])
                high_bleu = np.array([140, 255, 255])
                bleu_mask = cv2.inRange(hsv_frame, low_bleu, high_bleu)
                bleu_summation = bleu_mask.sum()

            except Exception:
                bleu_summation = 0
            # end try

            if bleu_summation > 550:
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                crop_img_yellow = image[y:y + h, x:x + w]
                crop_img_yellow = crop_img_yellow.astype('uint8')

                hsv_frame = cv2.cvtColor(crop_img_yellow, cv2.COLOR_BGR2HSV)
                low_yellow = np.array([20, 100, 100])
                high_yellow = np.array([30, 255, 255])
                yellow_mask = cv2.inRange(hsv_frame, low_yellow, high_yellow)

                yellow_summation = yellow_mask.sum()

                if yellow_summation > 255 * crop_img.shape[0] * crop_img.shape[0] * 0.4:
                    crop_gray = gray_image[y:y + h, x:x + w]
                    crop_gray = crop_gray.astype('uint8')

                    th = cv2.adaptiveThreshold(
                        crop_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        cv2.THRESH_BINARY, 11, 2
                    )
                    contours2, hierarchy = cv2.findContours(
                        th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
                    )

                    chars = 0

                    for c in contours2:
                        area2 = cv2.contourArea(c)
                        x2, y2, w2, h2 = cv2.boundingRect(c)

                        if (
                                ((w2 * h2) > (h * w * 0.01)) and
                                (h2 > w2) and
                                (area2 < (h * w * 0.9))
                        ):
                            chars += 1
                        # end if
                    # end for

                    if 20 > chars > 4:
                        rect = cv2.minAreaRect(cnt)
                        box = cv2.boxPoints(rect)
                        box = np.intp(box)
                        pts = np.array(box)
                        warped = transform_points(img, pts)
                        crops.append(warped)

                        locations.append(box)

                        cv2.drawContours(
                            image, [box],
                            0, Colors.GREEN, 2
                        )
                    # end if
                # end if
            # end if
        # end if
    # end for

    return crops, locations
# end find_image_plates_locations

def adjust_image(
        image: np.ndarray, factor: Optional[int] = 0.10
) -> Tuple[np.ndarray, float, float]:
    """
    Adjusts the contrast and brightness of the image.

    :param image: The image.
    :param factor: The change percentage.

    :return: The adjusted image.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    hist = cv2.calcHist(
        [gray], [0], None,
        [256], [0, 256]
    )
    hist_size = len(hist)

    accumulator = [float(hist[0][0])]

    for index in range(1, hist_size):
        accumulator.append(accumulator[index - 1] + float(hist[index][0]))
    # end for

    maximum = accumulator[-1]

    factor *= 100
    factor *= (maximum / 100.0)
    factor /= 2.0

    minimum_gray = 0

    while accumulator[minimum_gray] < factor:
        minimum_gray += 1
    # end while

    maximum_gray = hist_size - 1

    while accumulator[maximum_gray] >= (maximum - factor):
        maximum_gray -= 1
    # end while

    alpha = 255 / (maximum_gray - minimum_gray)
    beta = - minimum_gray * alpha

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    return auto_result, alpha, beta
# end adjust_image

def process_thresh(image: np.ndarray) -> np.ndarray:
    """
    Processes the thresh of the image.

    :param image: The image.

    :return: The thresh of the image.
    """

    adjusted, *_ = adjust_image(image)

    gray = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return thresh
# end process_thresh

def tesseract_find_image_plates(image: np.ndarray) -> List[Plate]:
    """
    Detects the plates in the image.

    :param image: The image to process_thresh.

    :return: The plate objects.
    """

    crops, locations = find_image_plates_locations(image)

    return [
        Plate(
            image=image, plate=crop,
            thresh=process_thresh(crop), location=location
        ) for crop, location in zip(crops, locations)
    ]
# end find_plates

def clean_lp(lp: str) -> str:
    """
    Cleans the license plate string from special characters.

    :param lp: The license plate string.

    :return: The cleaned license plate string.
    """

    special_characters = [
        ',', '.', '"', ':', ')', '(', '-', '!', '?',
        '|', ';', "'", '$', '&', '/', '[', ']', '>', '%', '=',
        '#', '*', '+', '\\', '•', '~', '@', '£',
        '·', '_', '{', '}', '©', '^', '®', '`', '<', '→',
        '°', '€', '™', '›', '♥', '←', '×', '§', '″', '′',
        'Â', '█', '½', '…',
        '“', '★', '”', '–', '●', '►', '−', '¢', '²', '¬',
        '░', '¶', '↑', '±', '¿', '▾', '═', '¦', '║', '―',
        '¥', '▓', '—', '‹', '─',
        '▒', '：', '¼', '⊕', '▼', '▪', '†', '■', '’', '▀',
        '¨', '▄', '♫', '☆', '¯', '♦', '¤', '▲', '¸', '¾',
        'Ã', '⋅', '‘', '∞',
        '∙', '）', '↓', '、', '│', '（', '»', '，', '♪', '╩',
        '╚', '³', '・', '╦', '╣', '╔', '╗', '▬', '❤', 'Ø',
        '¹', '≤', '‡', '√', '«', ' ', '\n', "'", "\x0c"
    ]

    for char in special_characters:
        if char in lp:
            lp = lp.replace(char, '')
        # end if
    # end for

    return lp
# end clean_lp

def run_tesseract(
        source: Union[str, Path],
        destination: Union[str, Path],
        scripts: Optional[Union[str, Path]] = None
) -> None:
    """
    Runs the tesseract command.

    :param source: The source image file.
    :param destination: The destination license plate text file.
    :param scripts: The path to the tesseract scripts.
    """

    if scripts is None:
        scripts = tesseract()
    # end if

    run_silent_command(
        f'{scripts}/tesseract.exe '
        f'{source} {destination.replace(".txt", "")} '
        f'-l eng --psm 6 --dpi 300 --oem 1'
    )
# end run_tesseract

_P = TypeVar("_P", Iterable[Plate], Iterable[Plate])

def tesseract_read_plates(
        plates: _P, scripts: Optional[Union[str, Path]] = None
) -> _P:
    """
    Processes and extracts all the license plates from an image, and returns the plate images and texts.

    :param plates: The plate objects.
    :param scripts: The path to the tesseract scripts.

    :return: The plate images and texts.
    """

    for plate in plates:
        with tempfile.TemporaryFile(suffix=".jpg") as file:
            image_temp = file.name
        # end TemporaryFile

        with tempfile.TemporaryFile(suffix=".txt") as file:
            lp_temp = file.name
        # end TemporaryFile

        cv2.imwrite(image_temp, plate.thresh)

        run_tesseract(
            source=image_temp,
            destination=lp_temp,
            scripts=scripts
        )

        while not os.path.exists(lp_temp):
            pass
        # end while

        while True:
            with open(lp_temp, 'r') as file:
                chars = clean_lp(file.read())
            # end open

            if chars:
                break
            # end if
        # end while

        while os.path.exists(image_temp):
            try:
                os.remove(image_temp)

            except PermissionError:
                pass
            # end try
        # end while

        while os.path.exists(lp_temp):
            try:
                os.remove(lp_temp)

            except PermissionError:
                pass
            # end try
        # end while

        plate.chars = chars
    # end for

    return plates
# end tesseract_read_image_plates

def tesseract_read_image_plates(
        image: np.ndarray,
        scripts: Optional[Union[str, Path]] = None
) -> List[Plate]:
    """
    Processes and extracts all the license plates from an image, and returns the plate images and texts.

    :param image: The image object to process.
    :param scripts: The path to the tesseract scripts.

    :return: The plate images and texts.
    """

    return list(
        tesseract_read_plates(
            plates=tesseract_find_image_plates(image),
            scripts=scripts
        )
    )
# end tesseract_read_image_plates