"""
QR Code Generator with Custom Styling & Center Logo Overlay
Supports local paths, URLs, and Base64 logo sources with aspect-ratio preservation,
error correction elevation (Level H), and input/format validation safeguards.
"""

import base64
import io
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional, Tuple, Union

import qrcode
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_M
from PIL import Image, ImageDraw

# Supported foreground color choices
PALETTE = {
    1: "black",
    2: "blue",
    3: "green",
    4: "red",
    5: "orange",
    6: "purple",
    7: "pink",
    8: "brown",
    9: "darkblue",
    10: "darkgreen",
}


def validate_input_data(data: Union[str, bytes]) -> str:
    """
    Validates input data string/URL for QR code generation.
    Raises ValueError for null, non-string, or empty/whitespace values.
    """
    if data is None:
        raise ValueError("Data cannot be None.")

    if not isinstance(data, (str, bytes)):
        raise TypeError(f"Data must be a string or bytes, got {type(data).__name__}.")

    if isinstance(data, bytes):
        data = data.decode("utf-8", errors="replace")

    cleaned = data.strip()
    if not cleaned:
        raise ValueError("Input data cannot be empty or pure whitespace.")

    # Practical safety limit for standard QR code capacity (max ~7089 numeric, ~4296 alphanumeric)
    if len(cleaned) > 4000:
        raise ValueError(
            f"Input data length ({len(cleaned)} chars) exceeds standard safe QR code capacity (~4000 chars)."
        )

    # URL structure sanity check
    parsed = urllib.parse.urlparse(cleaned)
    if parsed.scheme in ("http", "https") and not parsed.netloc:
        raise ValueError(f"Invalid URL structure: '{cleaned}'. Missing host/domain.")

    return cleaned


def load_logo_image(logo_source: Union[str, Path, Image.Image]) -> Image.Image:
    """
    Loads a logo image from:
      1. An existing PIL.Image object
      2. A local file path
      3. An HTTP/HTTPS URL
      4. A Base64-encoded image string (raw or data URI)
    """
    if isinstance(logo_source, Image.Image):
        return logo_source.copy()

    if not logo_source or not isinstance(logo_source, (str, Path)):
        raise ValueError("Logo source must be a valid file path, URL, Base64 string, or PIL Image.")

    logo_str = str(logo_source).strip()

    # 1. Base64 Data URI or raw base64 string
    if logo_str.startswith("data:image/") or (
        len(logo_str) > 60 and re.match(r"^[A-Za-z0-9+/=\r\n]+$", logo_str)
    ):
        try:
            raw_b64 = logo_str.split("base64,")[-1] if "base64," in logo_str else logo_str
            image_bytes = base64.b64decode(raw_b64.encode("ascii"))
            return Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            raise ValueError(f"Failed to decode base64 logo: {e}") from e

    # 2. Web URL
    parsed = urllib.parse.urlparse(logo_str)
    if parsed.scheme in ("http", "https"):
        try:
            req = urllib.request.Request(
                logo_str,
                headers={"User-Agent": "QRCodeGenerator/1.0 (Python PIL)"},
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                image_bytes = response.read()
            return Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            raise ValueError(f"Failed to download logo from URL '{logo_str}': {e}") from e

    # 3. Local filesystem path
    local_path = Path(logo_str)
    if not local_path.is_file():
        raise FileNotFoundError(f"Logo file not found on disk: '{local_path.resolve()}'")

    try:
        return Image.open(local_path)
    except Exception as e:
        raise ValueError(f"Cannot read image file '{logo_str}': {e}") from e


def overlay_logo(
    qr_img: Image.Image,
    logo_img: Image.Image,
    max_ratio: float = 0.22,
    padding: int = 8,
    bg_color: str = "white",
) -> Image.Image:
    """
    Positions the logo precisely in the center of the QR code with:
      - Aspect-ratio preservation (no image distortion).
      - Bounded size (default max 22% of QR dimensions to protect scannability).
      - Background padding badge separating the logo from QR data modules.
    """
    # Ensure working in RGBA mode for transparency support
    base_qr = qr_img.convert("RGBA")
    logo = logo_img.convert("RGBA")

    qr_w, qr_h = base_qr.size

    # Clamp ratio between 10% and 25% for QR scannability safety
    clamped_ratio = max(0.10, min(max_ratio, 0.25))
    max_logo_w = int(qr_w * clamped_ratio)
    max_logo_h = int(qr_h * clamped_ratio)

    # Maintain aspect ratio using thumbnail
    resample_filter = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)
    logo.thumbnail((max_logo_w, max_logo_h), resample_filter)
    logo_w, logo_h = logo.size

    # Calculate centered badge (background padding)
    pad = max(2, padding)
    badge_w = logo_w + (pad * 2)
    badge_h = logo_h + (pad * 2)

    badge_x = (qr_w - badge_w) // 2
    badge_y = (qr_h - badge_h) // 2

    # Draw rounded badge background
    draw = ImageDraw.Draw(base_qr)
    badge_coords = [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h]

    if hasattr(draw, "rounded_rectangle"):
        draw.rounded_rectangle(badge_coords, radius=pad, fill=bg_color)
    else:
        draw.rectangle(badge_coords, fill=bg_color)

    # Center logo inside the badge
    logo_x = (qr_w - logo_w) // 2
    logo_y = (qr_h - logo_h) // 2
    base_qr.paste(logo, (logo_x, logo_y), mask=logo)

    return base_qr


def generate_qr_code(
    data: Union[str, bytes],
    fill_color: str = "black",
    back_color: str = "white",
    logo_source: Optional[Union[str, Path, Image.Image]] = None,
    max_logo_ratio: float = 0.22,
    output_filename: Optional[str] = None,
    box_size: int = 10,
    border: int = 4,
) -> Image.Image:
    """
    Generates a customized QR code image with optional center logo overlay.
    Automatically elevates error correction to Level H (High) when a logo is used.
    """
    valid_data = validate_input_data(data)

    # Elevate error correction to Level H (~30% recovery) if a logo is attached
    has_logo = logo_source is not None and bool(str(logo_source).strip())
    error_correction = ERROR_CORRECT_H if has_logo else ERROR_CORRECT_M

    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(valid_data)
    qr.make(fit=True)

    # Generate base QR code
    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color)

    # Apply center logo overlay if requested
    if has_logo:
        try:
            logo_img = load_logo_image(logo_source)
            qr_img = overlay_logo(
                qr_img=qr_img,
                logo_img=logo_img,
                max_ratio=max_logo_ratio,
                padding=8,
                bg_color=back_color,
            )
        except Exception as e:
            print(f"[Warning] Failed to embed logo: {e}. Generating clean QR code without logo.")

    # Save to file if output filename is provided
    if output_filename:
        save_qr_image(qr_img, output_filename)

    return qr_img


def sanitize_filename(name: str, default: str = "qrcode.png") -> str:
    """Cleans user-supplied filename and ensures valid image extension."""
    if not name or not name.strip():
        return default

    # Remove invalid characters for cross-platform filesystem safety
    cleaned = re.sub(r'[\\/*?:"<>|]', "_", name.strip())
    if not cleaned or cleaned.startswith("."):
        cleaned = "qrcode" + cleaned

    if not cleaned.lower().endswith((".png", ".jpg", ".jpeg")):
        cleaned += ".png"

    return cleaned


def save_qr_image(img: Image.Image, filepath: str) -> str:
    """Safely saves QR code image, handling JPEG RGB conversion and OS errors."""
    clean_path = sanitize_filename(filepath)
    target_img = img

    # JPEG does not support RGBA transparency; composite onto RGB if needed
    if clean_path.lower().endswith((".jpg", ".jpeg")):
        if target_img.mode in ("RGBA", "LA") or (
            target_img.mode == "P" and "transparency" in target_img.info
        ):
            rgb_canvas = Image.new("RGB", target_img.size, (255, 255, 255))
            alpha_mask = target_img.convert("RGBA").split()[3]
            rgb_canvas.paste(target_img, mask=alpha_mask)
            target_img = rgb_canvas
        else:
            target_img = target_img.convert("RGB")

    target_img.save(clean_path)
    return clean_path


def interactive_cli():
    """Interactive command-line interface with full safeguards and logo option."""
    print("=" * 40)
    print("      QR Code Generator & Styler      ")
    print("=" * 40)

    # 1. Data input
    data = ""
    while not data.strip():
        raw_data = input("\nEnter the text or URL: ")
        try:
            data = validate_input_data(raw_data)
        except (ValueError, TypeError) as err:
            print(f"Error: {err}")

    # 2. Foreground color choice
    print("\nSelect foreground color:")
    for num, name in PALETTE.items():
        print(f"  {num}: {name}")

    color_choice = None
    while color_choice not in PALETTE:
        raw_choice = input("Enter color number (default 1 - black): ").strip()
        if not raw_choice:
            color_choice = 1
            break
        try:
            parsed = int(raw_choice)
            if parsed in PALETTE:
                color_choice = parsed
            else:
                print("Invalid number. Choose from the list above.")
        except ValueError:
            print("Please enter a valid integer.")

    fill_color = PALETTE[color_choice]

    # 3. Logo input (Optional)
    print("\nCenter Logo (Optional):")
    logo_input = input("Enter file path, URL, or Base64 (leave empty for none): ").strip()
    logo_source = logo_input if logo_input else None

    # 4. Output filename
    raw_name = input("\nEnter file name (default: 'qrcode.png'): ").strip()
    filename = sanitize_filename(raw_name)

    # 5. Generate and save
    try:
        generate_qr_code(
            data=data,
            fill_color=fill_color,
            back_color="white",
            logo_source=logo_source,
            output_filename=filename,
        )
        print(f"\n[Success] QR code saved to: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"\n[Error] Could not generate QR code: {e}")


if __name__ == "__main__":
    interactive_cli()
