# definition.py

from typing import Optional

import numpy as np

from represent import represent, Modifiers

__all__ = [
    "Plate"
]

@represent
class Plate:
    """The class to represent a possible plate"""

    __modifiers__ = Modifiers(
        excluded=[
            "image", "modifiers", "thresh",
            "plate", "location"
        ]
    )

    __slots__ = "image", "plate", "thresh", "location", "chars"

    def __init__(
            self,
            image: Optional[np.ndarray] = None,
            plate: Optional[np.ndarray] = None,
            thresh: Optional[np.ndarray] = None,
            location: Optional[np.ndarray] = None,
            chars: Optional[str] = None
    ) -> None:
        """
        Creates the possible class attributes.

        :param plate: The vehicle-image.
        :param plate: The plate-image.
        :param thresh: The thresh-image.
        :param location: The location of the plate in the source image.
        :param chars: The characters on the plate.
        """

        if (plate is None) and (image is not None) and (location is not None):
            plate = image[
                np.min(location[:, 1]):np.max(location[:, 1]),
                np.min(location[:, 0]):np.max(location[:, 0])
            ]
        # end if

        self.image = image
        self.plate = plate
        self.thresh = thresh
        self.location = location
        self.chars = chars
    # end constructor
# end Plate