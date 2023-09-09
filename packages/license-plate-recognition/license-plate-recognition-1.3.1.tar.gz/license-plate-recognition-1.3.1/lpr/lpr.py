# lpr.py

import threading
import datetime as dt
import warnings
from typing import (
    Optional, Union, List, Iterable, ClassVar, overload
)

import numpy as np
import cv2

from attrs import define

from represent import represent, Modifiers

from lpr.interface import (
    write_plate_chars, write_plate_frame,
    create_image_window
)
from lpr.plates import Plate, read_plates, find_image_plates
from lpr.tesseract import (
    tesseract_read_image_plates, tesseract_find_image_plates
)
from lpr.process.image import (
    read_image_file, configure_image_file_data
)

__all__ = [
    "find_possible_plates",
    "write_plate",
    "show",
    "read_license_plates",
    "LicencePlate",
    "LicencePlates",
    "LPR",
    "TESSERACT"
]

TESSERACT = True

@define(repr=False)
@represent
class LicencePlate:
    """
    A class to represent the response object from license plate processes.

    The constractor parameters:

    - source:
        A path to a source image file with a license plate to find_image_plates_locations and read.

    - image:
        A numpy array to contain the data of an image to process_thresh.

    - processed:
        The image with the plate data written on the original image.

    - plate:
        The possible plate object detected in the image.

    - tesseract:
        The value to use tesseract for the license plate recognition.
    """

    __modifiers__: ClassVar[Modifiers] = Modifiers(
        excluded=["image", "processed"]
    )

    plate: Plate
    image: np.ndarray
    processed: np.ndarray
    source: Optional[str] = None
    tesseract: bool = False
# end LicencePlates

class LicencePlates:
    """
    A class to represent the response object from license plate processes.

    The constractor parameters:

    - source:
        A path to a source image file with a license plate to find_image_plates_locations and read.

    - image:
        A numpy array to contain the data of an image to process_thresh.

    - processed:
        The image with the plate data written on the original image.

    - plates:
        All possible plate objects detected in the image.

    - tesseract:
        The value to use tesseract for the license plate recognition.
    """

    __modifiers__: ClassVar[Modifiers] = Modifiers(
        excluded=["image", "processed_image"]
    )

    __slots__ = (
        "image", "processed", "plates", "source", "tesseract"
    )

    def __init__(
            self,
            image: np.ndarray,
            processed: np.ndarray,
            plates: Optional[Iterable[LicencePlate]] = None,
            source: Optional[str] = None,
            tesseract: Optional[bool] = False
    ) -> None:
        """
        Writes the license plate data on the image to visualize it.

        :param image: The image object.
        :param source: The file to read the image data from.
        :param plates: The license plates.
        :param tesseract: The value to run the process  with tesseract.

        :return: The image object.
        """

        self.tesseract = tesseract

        self.source = source

        self.processed = processed
        self.image = image

        self.plates = list(plates or [])
    # end __init__

    try:
        from typing import Self

    except ImportError:
        Self = Iterable[LicencePlate]
    # end try

    @overload
    def __getitem__(self, item: int) -> LicencePlate:
        """
        Returns the items.

        :param item: The slice item.

        :return: The items in the object to get with the slice.
        """
    # end __getitem__

    @overload
    def __getitem__(self, item: slice) -> Self:
        """
        Returns the items.

        :param item: The slice item.

        :return: The items in the object to get with the slice.
        """
    # end __getitem__

    def __getitem__(self, item: Union[slice, int]) -> Union[Self, LicencePlate]:
        """
        Returns the items.

        :param item: The slice item.

        :return: The items in the object to get with the slice.
        """

        data = self.plates[item]

        if isinstance(data, list):
            return type(self)(
                image=self.image,
                source=self.source,
                processed=self.processed,
                plates=data,
                tesseract=self.tesseract
            )
        # end if

        return data
    # end __getitem__

    def __len__(self) -> int:
        """
        The length of the assets.

        :return: The length of the assets.
        """

        return len(self.plates)
    # end __len__

    def __iter__(self) -> Iterable[LicencePlate]:
        """
        Returns the object as an iterable.

        :return: The iterable object.
        """

        yield from self.plates
    # end __iter__
# end LicencePlates

def find_possible_plates(
        source: Optional[str] = None,
        image: Optional[np.ndarray] = None,
        tesseract: Optional[bool] = False
) -> List[Plate]:
    """
    Reads the license plate from the image data.

    :param source: The file to read the image data from.
    :param image: The source-image.
    :param tesseract: The value to run the process  with tesseract.

    :return: The image object.
    """

    image = configure_image_file_data(source=source, image=image)

    if tesseract:
        possible_plates = tesseract_read_image_plates(image=image)

    else:
        possible_plates = read_plates(
            tesseract_find_image_plates(image) or find_image_plates(image)
        )

        possible_plates.sort(key=lambda plate: len(plate.chars), reverse=True)
    # end if

    return possible_plates
# end find_possible_plates

def write_plate(image: np.ndarray, plate: Plate) -> np.ndarray:
    """
    Writes the license plate data on the image to visualize it.

    :param image: The image object.
    :param plate: The plate object to read the data from.

    :return: The image object.
    """

    return write_plate_chars(
        image=write_plate_frame(image, plate),
        plate=plate
    )
# end write_plate

def read_license_plates(
        source: Optional[str] = None,
        image: Optional[np.ndarray] = None,
        tesseract: Optional[bool] = None
) -> LicencePlates:
    """
    Main function of the license plate recognition module

    :param source: The file to read the image data from.
    :param image: The source-image.
    :param tesseract: The value to run the process  with tesseract.

    :return: The results license plate list.
    """

    image = configure_image_file_data(source=source, image=image)

    auto = tesseract is None

    if auto:
        tesseract = TESSERACT
    # end if

    possible_plates = find_possible_plates(
        image=image, tesseract=tesseract
    )

    if auto and (not possible_plates):
        possible_plates = find_possible_plates(
            image=image, tesseract=not tesseract
        )
    # end if

    possible_plates = [plate for plate in possible_plates if plate.chars]

    total_processed_image = None

    processed_images = {}

    for possible_plate in possible_plates:
        total_processed_image = write_plate(
            image=(
                image if (total_processed_image is None)
                else total_processed_image
            ), plate=possible_plate
        )

        processed_images[possible_plate] = (
            write_plate(image=image, plate=possible_plate)
        )
    # end for

    if total_processed_image is None:
        total_processed_image = image
    # end if

    plates = [
        LicencePlate(
            tesseract=tesseract, source=source,
            image=image, plate=possible_plate,
            processed=total_processed_image
        ) for possible_plate, processed_image in
        processed_images.items()
    ]

    return LicencePlates(
        image=image, plates=plates,
        processed=total_processed_image,
        tesseract=tesseract, source=source
    )
# end read_license_plates

def show(
        image: np.array,
        title: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        timeout: Optional[Union[int, float, dt.timedelta]] = None,
        block: Optional[bool] = True
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
    :param block: The value to block the execution.
    """

    if block:
        create_image_window(
            image=image, timeout=timeout, width=width,
            height=height, title=title, x=x, y=y
        )

    else:
        threading.Thread(
            target=create_image_window,
            kwargs=dict(
                image=image, timeout=timeout, width=width,
                height=height, title=title, x=x, y=y
            )
        ).start()
    # end if
# end show

@represent
class LPR:
    """
    A class to represent the model of license plate recognition.

    This class can be used to create a License-Plate-Recognition pipeline.
    This class cen be used for the detection of license plates in an image,
    as well as reading the characters on the license plate.

    The constractor parameters:

    - source:
        A path to a source image file with a license plate to find_image_plates_locations and read.

    - image:
        A numpy array to contain the data of an image to process_thresh.

    - timeout:
        The timeout in seconds. to hold and display window before closing it.
    """

    __modifiers__ = Modifiers()
    __modifiers__.excluded.extend(["image", "processed_image"])

    DELAY = 0
    WIDTH = 700
    X = 650
    Y = 70

    TITLE = "detected"

    TESSERACT = None

    __slots__ = (
        "source", "image", "tesseract", "title", "width",
        "height", "x", "y", "timeout", "plates"
    )

    def __init__(
            self,
            source: Optional[str] = None,
            image: Optional[np.ndarray] = None,
            tesseract: Optional[bool] = None,
            title: Optional[str] = None,
            width: Optional[int] = None,
            height: Optional[int] = None,
            x: Optional[int] = None,
            y: Optional[int] = None,
            timeout: Optional[Union[int, float, dt.timedelta]] = None
    ) -> None:
        """
        Writes the license plate data on the image to visualize it.

        :param image: The image object.
        :param source: The file to read the image data from.
        :param tesseract: The value to run the process  with tesseract.
        :param title: The title of the window.
        :param timeout: The amount of seconds to keep the window on the screen.
        :param width: The width of the window.
        :param height: The height of the window.
        :param x: The x position of the window.
        :param y: The y position of the window.
        :param timeout: The amount of seconds to keep the window on the screen.

        :return: The image object.
        """

        if tesseract is None:
            tesseract = self.TESSERACT
        # end if

        self.source = source
        self.title = title or self.TITLE

        self.timeout = timeout or self.DELAY
        self.x = x or self.X
        self.y = y or self.Y
        self.width = width or self.WIDTH
        self.height = height

        self.tesseract = tesseract

        self.image = image

        self.plates: Optional[LicencePlates] = None
    # end __init__

    def read_image_file(self, source: Optional[str] = None) -> np.ndarray:
        """
        Reads the image data and returns an array of the data

        :param source: The file to read the image data from.

        :returns: The image object.
        """

        self.image = read_image_file(path=source or self.source)

        return self.image
        # end if
    # end read_image_file

    def read_license_plates(
            self,
            source: Optional[str] = None,
            image: Optional[str] = None,
            tesseract: Optional[bool] = None
    ) -> LicencePlates:
        """
        Main function of the license plate recognition module

        :param source: The file to read the image data from.
        :param image: The source-image.
        :param tesseract: The value to run the process  with tesseract.

        :return: The results license plate list.
        """

        image = configure_image_file_data(
            source=source or self.source,
            image=image or self.image
        )

        self.image = self.image or image

        self.plates = read_license_plates(
            image=image,
            tesseract=tesseract or self.tesseract,
            source=source or self.source
        )

        return self.plates
    # end read_license_plates

    def show(
            self,
            title: Optional[str] = None,
            width: Optional[int] = None,
            height: Optional[int] = None,
            x: Optional[int] = None,
            y: Optional[int] = None,
            timeout: Optional[Union[int, float, dt.timedelta]] = None,
            block: Optional[bool] = True
    ) -> None:
        """
        Creates the image window.

        :param title: The title of the window.
        :param timeout: The amount of seconds to keep the window on the screen.
        :param width: The width of the window.
        :param height: The height of the window.
        :param x: The x position of the window.
        :param y: The y position of the window.
        :param block: The value to block the execution.
        """

        if self.plates is None:
            raise ValueError(
                f"license_plate object is not processed. "
                f"Use the '{self.read_license_plates}' "
                f"method before visualizing the results."
            )

        elif not self.plates:
            warnings.warn(f"No license plates are present.")
        # end if

        show(
            image=self.plates.processed,
            timeout=timeout or self.timeout, width=width or self.width,
            height=height or self.height, title=title or self.title,
            x=x or self.x, y=y or self.y, block=block
        )
    # end show

    @staticmethod
    def wait_key(delay: Optional[int] = 0) -> int:
        """
        Waits for a key press or the delay.

        :param delay: The time to wait in milliseconds.

        :return: The pressed key ord.
        """

        return cv2.waitKey(delay)
    # end wait_key
# end LPR