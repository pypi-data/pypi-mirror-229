from datetime import datetime
from glob import iglob
import logging
import os
import re
from tempfile import NamedTemporaryFile
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
import tator


logger = logging.getLogger(__name__)
FONT = os.path.join(os.path.dirname(__file__), "Cascadia.ttf")
FONT_SIZE = 36


def create_summary_image(
    host: str,
    token: str,
    media_type: int,
    directory: str,
    import_type: str,
    sail_date: Optional[str] = None,
    land_date: Optional[str] = None,
    hdd_recv_date: Optional[str] = None,
    hdd_sn: Optional[str] = None,
) -> Tuple[str, dict]:
    """Creates a summary image for a trip.

    :host: The Tator hostname
    :token: The Tator API token
    :media_type: The Tator media type to create
    :directory: The directory containing files to use to determine the vessel name
    :sail_date: The value for the Sail Date attribute
    :land_date: The value for the Land Date attribute
    :hdd_recv_date: The value for the HDD Date Received attribute
    :hdd_sn: The value for the HDD Serial Number attribute
    :returns: The created section name and shared attributes

    """

    vessel_name = trip_id = "UNKNOWN"
    section_name = f"Imported on {datetime.now()}"
    if import_type == "O2":
        # Get the vessel name and trip id from the first filename found starting with `stream-`
        filename = os.path.basename(next(iglob(os.path.join(directory, f"stream-*"))))
        vessel_trip_match = re.match(r"^stream-([^-]*)-([^-]*)-.*$", filename)
        if vessel_trip_match:
            try:
                vessel_name, trip_id = vessel_trip_match.groups()
            except Exception:
                logger.warning("Could not find vessel and trip name in '%s'", filename)
    elif import_type == "B3":
        video_list = list(iglob(os.path.join(directory, f"*.mp4")))
        video_path = video_list[0]
        filename = os.path.basename(video_path)
        filename_parts = os.path.splitext(filename)[0].split("-")
        if len(filename_parts) == 4:
            try:
                vessel_name = filename_parts[0]
            except Exception:
                logger.warning("Could not get the vessel or section name", exc_info=True)
    else:
        raise RuntimeError(f"Received unexepected import type argument: {import_type}")

    if not sail_date:
        sail_date = "N/A"
    if not land_date:
        land_date = "N/A"
    section_name = f"{vessel_name} ({sail_date})"
    img_sz = 1024
    shared_attrs = {
        "Vessel Name": vessel_name,
        "Trip ID": trip_id,
        "Sail Date": sail_date,
        "Land Date": land_date,
    }
    label_len = max(len(key) for key in shared_attrs.keys())
    image_text = "\n".join(f"{k: >{label_len}}: {v}" for k, v in shared_attrs.items())
    font = ImageFont.truetype(font=FONT, size=FONT_SIZE)
    image = Image.new("RGB", (img_sz, img_sz), color="black")
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = draw.textbbox((0, 0), image_text, font=font)
    x_pos = (img_sz - (right - left)) // 2
    y_pos = (img_sz - (bottom - top)) // 2
    draw.text((x_pos, y_pos), image_text, fill="white", font=font)

    with NamedTemporaryFile(suffix=".png") as temp_file:
        image.save(temp_file.name)
        tator_api = tator.get_api(host=host, token=token)
        attrs = {
            **shared_attrs,
            "HDD Date Received": hdd_recv_date,
            "HDD Serial Number": hdd_sn,
        }

        import_media_args = {
            "api": tator_api,
            "type_id": media_type,
            "path": temp_file.name,
            "section": section_name,
            "fname": os.path.basename(temp_file.name),
            "attributes": {k: v for k, v in attrs.items() if v is not None},
        }

        response = None
        try:
            for progress, response in tator.util.upload_media(**import_media_args):
                logger.debug("Upload progress for %s: %d%%", temp_file.name, progress)
        except Exception:
            logger.error(
                "Could not create trip summary with args:\n%s", import_media_args, exc_info=True
            )
        else:
            logger.debug("Uploaded image, received response: %s", response)

    return section_name, shared_attrs
