from datetime import datetime, timezone
from glob import iglob
import json
import logging
import os
from typing import Any, Dict, List

import tator
from tator.openapi.tator_openapi import CreateListResponse, File, FileType, MediaType, TatorApi
from tqdm import tqdm

from hms_import.util import validate_types

logger = logging.getLogger(__name__)
DATETIME_FORMAT = "%Y%m%dT%H%M%SZ"


def upload_and_import_videos(
    tator_api: TatorApi,
    video_list: List[str],
    media_type: MediaType,
    attrs: Dict[str, Any],
    file_list: List[File],
) -> bool:
    """Returns False if any media fail to upload for any reason"""
    success = True
    video_path = video_list[0]
    filename = os.path.basename(video_path)
    section = "TBD"  # TODO construct from attrs
    media_type_id = media_type.id
    project_id = media_type.project
    shared_attributes = {
        **attrs,
        "related_files": ",".join(str(file_obj.id) for file_obj in file_list),
    }

    for video_path in tqdm(video_list, desc="Video Imports", dynamic_ncols=True, position=0):
        # Initialize attributes with sentinel values
        sensor_name = vessel_name = "UNKNOWN"
        try:
            filename = os.path.basename(video_path)
            filename_parts = os.path.splitext(filename)[0].split("-")
            start_datetime = datetime.min
            if len(filename_parts) == 4:
                vessel_name, sensor_name, start_date, start_time = filename_parts
                try:
                    start_datetime = datetime.strptime(
                        f"{start_date}T{start_time}", DATETIME_FORMAT
                    ).replace(tzinfo=timezone.utc)
                except Exception:
                    logger.warning(
                        "Could not parse datetime from filename '%s'", filename, exc_info=True
                    )
            attributes = {**shared_attributes, "Vessel Name": vessel_name, "toc_start": start_datetime}
            vid_md5 = tator.util.md5sum(video_path)
            media_spec = {
                "attributes": attributes,
                "name": filename,
                "type": media_type_id,
                "section": section,
                "md5": vid_md5,
            }
            response = tator_api.create_media_list(project_id, body=[media_spec])
            if isinstance(response, CreateListResponse) and response.id:
                media_id = response.id[0]
                pbar = tqdm(desc=filename, dynamic_ncols=True, position=1, total=100)
                last_progress = 0
                for p, _ in tator.util.upload_media(
                    api=tator_api,
                    type_id=media_type_id,
                    path=video_path,
                    md5=vid_md5,
                    section=section,
                    fname=filename,
                    attributes=attrs,
                    media_id=media_id,
                    timeout=120,
                ):
                    increment = max(p - last_progress, 1)
                    pbar.update(increment)
                    last_progress = p

            else:
                logger.warning("Could not create media object for '%s', skipping", video_path)
                success = False
        except Exception:
            logger.error(
                "Encountered exception while processing '%s', skipping", video_path, exc_info=True
            )

    return success


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


def upload_main(
    host: str,
    token: str,
    media_type_id: int,
    file_type_id: int,
    directory: str,
    attrs_str: str,
    media_ext: str,
    sensor_ext: str,
) -> bool:
    """
    :host: The Tator domain
    :token: The REST API token
    :media_type_id: The unique ID of the type of video to create
    :file_type_id: The unique ID of the type of file to create for storing GPS data
    :directory: The folder containing the files to import
    :attrs_str: The JSON string of attributes to attach to each media object, must be interpretable
                by `json.loads()`
    :media_ext: The file extension of importable videos
    :sensor_ext: The file extension of importable sensor data
    :returns: True if the import was successful, False if any part of it fails
    """
    success = False

    # Parse json string and abort if it raises
    try:
        attrs = json.loads(attrs_str)
    except json.JSONDecodeError:
        logger.error("Could not parse '%s' as valid JSON, aborting", attrs_str)
        return success
    except Exception:
        logger.error(
            "Encountered unhandled exception parsing `attrs_str`: %s", attrs_str, exc_info=True
        )
        return success

    # Validate the given media and file types, abort if they do not exist or are incompatible
    tator_api = tator.get_api(host=host, token=token)
    media_type, file_type = validate_types(tator_api, media_type_id, file_type_id)
    if media_type is None:
        logger.error("Could not get media type %d from Tator, aborting", media_type_id)
        return success
    if file_type is None:
        logger.error("Could not get file type %d from Tator, aborting", file_type_id)
        return success
    if media_type.project != file_type.project:
        logger.error(
            "Received MediaType %d and FileType %d, which are from different projects, aborting",
            media_type_id,
            file_type_id,
        )
        return success

    # Locate sensor data for import
    sensor_list = list(iglob(os.path.join(directory, f"*{sensor_ext}")))
    if sensor_list:
        file_list = upload_sensor_data(tator_api, sensor_list, file_type)
    else:
        file_list = []
        logger.warning("No sensor data found, only videos will be imported")

    # Locate media for import
    video_list = list(iglob(os.path.join(directory, f"*{media_ext}")))
    if video_list:
        success = upload_and_import_videos(tator_api, video_list, media_type, attrs, file_list)
    else:
        logger.error("No media found, aborting")
    return success
