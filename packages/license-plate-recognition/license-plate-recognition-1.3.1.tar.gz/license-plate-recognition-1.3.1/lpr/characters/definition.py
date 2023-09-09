# definition.py

import math

import numpy as np
import cv2

from represent import represent, Modifiers

__all__ = [
    "PossibleChar"
]

@represent
class PossibleChar:
    """A possible char class"""

    __modifiers__ = Modifiers(excluded=["contour"])
    
    __slots__ = (
        "contour", "x_position", "y_position", "width", "height",
        "area", "x_center", "y_center", "diagonal_size", "aspect_ratio"
    )

    def __init__(self, contour: np.ndarray) -> None:
        """
        Defines the class attributes.

        :param contour: The contour value.
        """

        self.contour = contour

        (
            self.x_position, self.y_position,
            self.width, self.height
        ) = cv2.boundingRect(self.contour)

        self.area = self.width * self.height
        self.x_center = (self.x_position + self.x_position + self.width) / 2
        self.y_center = (self.y_position + self.y_position + self.height) / 2
        self.diagonal_size = math.sqrt((self.width ** 2) + (self.height ** 2))
        self.aspect_ratio = float(self.width) / float(self.height)
    # end constructor
# end PossibleChar