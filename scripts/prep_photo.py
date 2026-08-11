"""
prep_photo.py

Prepares a photo for conversion into ASCII art.

Steps:
  1. Load the source photo.
  2. Boost local contrast using CLAHE (contrast-limited adaptive
     histogram equalization) so a flatly-lit face gets real
     highlights and shadows.
  3. Composite onto pure white so the background maps to the blank
     end of the ASCII ramp (white -> spaces).

Note: background removal (rembg) is skipped here since that package
isn't installed. This works best with a photo that already has a
fairly plain/light background. If you install rembg later, we can
add background removal back in.

Usage:
    python3 prep_photo.py source-photo.jpg
Output:
    source-prepped.png (grayscale, contrast-boosted, white background)
"""

import sys
import cv2
import numpy as np
from PIL import Image


def prep_photo(input_path: str, output_path: str = "source-prepped.png") -> None:
    # Load image in color (BGR, since we're using OpenCV)
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Could not read image at {input_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Boost local contrast with CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)

    # Composite onto pure white.
    # Since we're not removing the background here, this mostly
    # just ensures very bright areas clip to true white (255) so
    # they map cleanly to blank space in the ASCII ramp.
    white_bg = np.full_like(contrasted, 255)
    # Blend: keep contrasted image, but push near-white pixels to
    # pure white so the "blank" ramp character reads cleanly.
    threshold = 235
    mask = contrasted >= threshold
    composited = contrasted.copy()
    composited[mask] = 255

    # Save as grayscale PNG
    out_img = Image.fromarray(composited, mode="L")
    out_img.save(output_path)
    print(f"Saved prepped image to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 prep_photo.py <input-photo>")
        sys.exit(1)

    input_photo = sys.argv[1]
    prep_photo(input_photo)
