from datetime import datetime, timezone
from glob import iglob
import logging
import os
from time import sleep
from typing import Any, Dict, List, Optional

import tator
from tator.openapi.tator_openapi import (
    CreateListResponse,
    File,
    FileType,
    Media,
    MediaType,
    TatorApi,
)
from tqdm import tqdm

from hms_import.b3.generate_states import generate_multis_and_states
from hms_import.util import validate_types
from hms_import.summary_image import create_summary_image

logger = logging.getLogger(__name__)
DATETIME_FORMAT = "%Y%m%dT%H%M%SZ"


def upload_and_import_videos(
    tator_api: TatorApi,
    video_list: List[str],
    media_type: MediaType,
    attrs: Dict[str, Any],
    file_list: List[File],
    section_name: str,
) -> List[int]:
    """Returns list of created media ids"""
    created_ids = []
    media_type_id = media_type.id
    project_id = media_type.project
    shared_attributes = {
        **attrs,
        "related_files": ",".join(str(file_obj.id) for file_obj in file_list),
    }

    for video_path in tqdm(video_list, desc="Video Imports", dynamic_ncols=True, position=0):
        # Initialize attributes with sentinel values
        try:
            filename = os.path.basename(video_path)
            filename_parts = os.path.splitext(filename)[0].split("-")
            start_datetime = datetime.min
            if len(filename_parts) == 4:
                start_date, start_time = filename_parts[2:4]
                try:
                    start_datetime = datetime.strptime(
                        f"{start_date}T{start_time}", DATETIME_FORMAT
                    ).replace(tzinfo=timezone.utc)
                except Exception:
                    logger.warning(
                        "Could not parse datetime from filename '%s'", filename, exc_info=True
                    )
            attributes = {**shared_attributes, "toc_start": start_datetime}
            vid_md5 = tator.util.md5sum(video_path)
            media_spec = {
                "attributes": attributes,
                "name": filename,
                "type": media_type_id,
                "section": section_name,
                "md5": vid_md5,
            }
            response = tator_api.create_media_list(project_id, body=[media_spec])
            if isinstance(response, CreateListResponse) and response.id:
                created_ids.append(response.id[0])
                pbar = tqdm(desc=filename, dynamic_ncols=True, position=1, total=100)
                last_progress = 0
                for p, _ in tator.util.upload_media(
                    api=tator_api,
                    type_id=media_type_id,
                    path=video_path,
                    md5=vid_md5,
                    section=section_name,
                    fname=filename,
                    attributes=attrs,
                    media_id=created_ids[-1],
                    timeout=120,
                ):
                    increment = max(p - last_progress, 1)
                    pbar.update(increment)
                    last_progress = p

            else:
                logger.warning("Could not create media object for '%s', skipping", video_path)
        except Exception:
            logger.error(
                "Encountered exception while processing '%s', skipping", video_path, exc_info=True
            )

    return created_ids


def upload_sensor_data(
    tator_api: TatorApi,
    sensor_list: List[str],
    file_type: FileType,
) -> List[File]:
    file_type_id = file_type.id
    file_list = []
    for sensor_path in tqdm(sensor_list, dynamic_ncols=True, desc="Sensor Import", position=0):
        filename = os.path.basename(sensor_path)
        try:
            pbar = tqdm(desc=filename, dynamic_ncols=True, position=1, total=100)
            last_progress = 0
            response = None
            for p, response in tator.util.upload_generic_file(
                api=tator_api,
                file_type=file_type_id,
                path=sensor_path,
                description="Raw sensor data",
                name=filename,
                timeout=120,
            ):
                increment = max(p - last_progress, 1)
                pbar.update(increment)
                last_progress = p
        except Exception:
            logger.warning(
                "Encountered exception while processing '%s', skipping", sensor_path, exc_info=True
            )
            continue
        if isinstance(response, File):
            file_list.append(response)
    return file_list


def main(
    host: str,
    token: str,
    media_type_id: int,
    file_type_id: int,
    multi_type_id: int,
    state_type_id: int,
    image_type_id: int,
    directory: str,
    sail_date: Optional[str] = None,
    land_date: Optional[str] = None,
    hdd_recv_date: Optional[str] = None,
    hdd_sn: Optional[str] = None,
) -> bool:
    """
    :host: The Tator domain
    :token: The REST API token
    :media_type_id: The unique ID of the type of video to create
    :file_type_id: The unique ID of the type of file to create for storing GPS data
    :multi_type_id: The unique ID of the type of multiview to create
    :state_type_id: The unique ID of the type of State to create
    :image_type_id: The unique ID of the type of summary image to create
    :directory: The folder containing the files to import
    :sail_date: The sail date of the trip
    :land_date: The land date of the trip
    :hdd_recv_date: The date the hard drive was received
    :hdd_sn: The hard drive serial number
    :returns: True if the import was successful, False if any part of it fails
    """

    # Validate the given media and file types, abort if they do not exist or are incompatible
    tator_api = tator.get_api(host=host, token=token)
    media_type, file_type = validate_types(tator_api, media_type_id, file_type_id)
    if media_type is None:
        logger.error("Could not get media type %d from Tator, aborting", media_type_id)
        return False
    if file_type is None:
        logger.error("Could not get file type %d from Tator, aborting", file_type_id)
        return False
    if media_type.project != file_type.project:
        logger.error(
            "Received MediaType %d and FileType %d, which are from different projects, aborting",
            media_type_id,
            file_type_id,
        )
        return False

    # Locate media for import and create section name
    video_list = list(iglob(os.path.join(directory, f"*.mp4")))
    video_path = video_list[0]
    filename = os.path.basename(video_path)
    filename_parts = os.path.splitext(filename)[0].split("-")
    section_name = f"Imported on {datetime.now()}"
    vessel_name = "UNKNOWN"
    if len(filename_parts) == 4:
        try:
            vessel_name = filename_parts[0]
            section_name = f"{vessel_name} - ({sail_date})"
        except Exception:
            logger.warning("Could not get the vessel or section name", exc_info=True)
    section_name, shared_attrs = create_summary_image(
        host=host,
        token=token,
        media_type=image_type_id,
        import_type="B3",
        directory=directory,
        sail_date=sail_date,
        land_date=land_date,
        hdd_recv_date=hdd_recv_date,
        hdd_sn=hdd_sn,
    )

    # Locate sensor data for import
    sensor_list = list(iglob(os.path.join(directory, f"*.log")))
    if sensor_list:
        file_list = upload_sensor_data(tator_api, sensor_list, file_type)
    else:
        file_list = []
        logger.warning("No sensor data found, only videos will be imported")

    if video_list:
        created_ids = upload_and_import_videos(
            tator_api, video_list, media_type, shared_attrs, file_list, section_name
        )
    else:
        logger.error("No media found, aborting")
        return False

    # Wait for imports to generate thumbnails
    logger.info("Waiting for transcodes to generate thumbnails for all uploads...")
    pbar = tqdm(total=len(created_ids), dynamic_ncols=True, position=0)
    while created_ids:
        media = None
        media_id = created_ids.pop(0)
        try:
            media = tator_api.get_media(media_id)
        except Exception:
            logger.warning("Could not get media '%d'", media_id, exc_info=True)
        if not isinstance(media, Media) or (media.media_files and media.media_files.thumbnail_gif):
            # Do not put the id back on the list if it is invalid or it is ready; check the next one
            pbar.update()
            continue

        # Put the id at the end to check later and sleep to avoid a tight loop
        created_ids.append(media_id)
        sleep(1.0)

    # Generate associated multiviews and GPS States
    generate_multis_and_states(
        host=host,
        token=token,
        media_type_id=media_type_id,
        multi_type_id=multi_type_id,
        state_type_id=state_type_id,
        section_name=section_name,
    )
    return True
