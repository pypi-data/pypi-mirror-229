# test.py

import os
import pickle

from lpr import LPR, save_image

SOURCE = "images"
DESTINATION = "processed"

REPEAT = True

WIDTH = 700

def main() -> None:
    """Tests the program."""

    for file_name in os.listdir(SOURCE):
        name, extension = file_name.split(".")

        if os.path.exists(f"{DESTINATION}/{name}") and (not REPEAT):
            continue
        # end if

        lpr = LPR(source=f"{SOURCE}\\{file_name}")

        lpr.read_license_plates(tesseract=False)

        for lp in lpr.plates:
            print(f"license plate ({lpr.source}): {lp.plate.chars}")
        # end if

        lpr.show(width=WIDTH)

        save_image(
            image=lpr.plates.processed,
            path=f"{DESTINATION}/{name}/detected.{extension}"
        )

        with open(f"{DESTINATION}/{name}/plates.pkl", "wb") as file:
            pickle.dump(lpr.plates, file)
        # end open

        lpr.wait_key()
    # end for
# end main

if __name__ == "__main__":
    main()
# end if