# dimensions.py

__all__ = [
    "AreasDimensions",
    "Dimensions"
]

class AreasDimensions:
    """Defines the dimensions"""

    MIN_PIXEL_WIDTH = 2
    MIN_PIXEL_HEIGHT = 8
    MIN_ASPECT_RATIO = 0.25
    MAX_ASPECT_RATIO = 1.0
    MIN_PIXEL_AREA = 80
    MIN_DIAG_SIZE_MULTIPLE_AWAY = 0.3
    MAX_DIAG_SIZE_MULTIPLE_AWAY = 5.0

    MAX_CHANGE_IN_AREA = 0.5
    MAX_CHANGE_IN_WIDTH = 0.8
    MAX_CHANGE_IN_HEIGHT = 0.2
    MAX_ANGLE_BETWEEN_CHARS = 12.0
    MIN_NUMBER_OF_MATCHING_CHARS = 3
    RESIZED_CHAR_IMAGE_WIDTH = 20
    RESIZED_CHAR_IMAGE_HEIGHT = 30
    MIN_CONTOUR_AREA = 100
# end AreasDimensions

class Dimensions:
    """Defines the dimensions"""

    GAUSSIAN_SMOOTH_FILTER_SIZE = (5, 5)
    ADAPTIVE_THRESH_BLOCK_SIZE = 19
    ADAPTIVE_THRESH_WEIGHT = 9
# end Dimensions