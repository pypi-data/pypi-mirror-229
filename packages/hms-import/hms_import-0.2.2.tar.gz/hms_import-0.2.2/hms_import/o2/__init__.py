from configparser import ConfigParser
import logging
from pprint import pformat

import tator

from hms_import.util import validate_type_from_config
from hms_import.o2.import_videos import import_videos
from hms_import.o2.import_metadata import import_metadata
from hms_import.summary_image import create_summary_image


logger = logging.getLogger(__name__)


def main(config_file: str):
    # Read and parse the config file
    logger.debug("Parsing config file %s", config_file)
    config = ConfigParser()
    config.read(config_file)

    # Validate config values
    host = config["Tator"]["Host"]
    token = config["Tator"]["Token"]
    project_id = config["Tator"].getint("ProjectId", -1)

    tator_api = tator.get_api(host=host, token=token)
    if project_id < 0:
        raise ValueError(f"Missing ProjectId value in the Tator section of the config file")
    try:
        tator_api.get_project(project_id)
    except Exception as exc:
        raise ValueError(f"Could not get project {project_id}") from exc

    file_type = validate_type_from_config(tator_api, config, "FileType", project_id, "file_type")
    media_type = validate_type_from_config(
        tator_api, config, "MediaType", project_id, "media_type", list_filters=[("dtype", "video")]
    )
    summary_type = validate_type_from_config(
        tator_api,
        config,
        "SummaryType",
        project_id,
        "media_type",
        list_filters=[("dtype", "image")],
    )
    directory = config["Local"]["Directory"]

    # Create trip summary image
    create_summary_kwargs = {
        "host": host,
        "media_type": summary_type,
        "directory": directory,
        "import_type": "O2",
        "sail_date": config["Trip"].get("SailDate", None),
        "land_date": config["Trip"].get("LandDate", None),
        "hdd_recv_date": config["Trip"].get("HddDateReceived", None),
        "hdd_sn": config["Trip"].get("HddSerialNumber", None),
    }
    logger.debug("Creating trip summary with configuration %s", pformat(create_summary_kwargs))
    section, shared_attrs = create_summary_image(token=token, **create_summary_kwargs)
    if section:
        logger.debug("Created trip summary in section %s", section)
    else:
        raise RuntimeError("Could not create trip summary and section")

    # Construct metadata argument dictionary for logging (do not log token for security)
    import_metadata_kwargs = {
        "host": host,
        "project_id": project_id,
        "directory": directory,
        "meta_ext": config["Local"]["MetadataExtension"],
        "file_type": file_type,
    }
    logger.debug("Starting metadata import with configuration %s", pformat(import_metadata_kwargs))
    file_ids = import_metadata(token=token, **import_metadata_kwargs)
    logger.debug("Metadata import complete!")

    # Construct video argument dictionary for logging (do not log token for security)
    import_video_kwargs = {
        "host": host,
        "directory": directory,
        "project_id": project_id,
        "file_ids": file_ids,
        "media_ext": config["Local"]["MediaExtension"],
        "media_type": media_type,
        "section": section,
        "shared_attrs": shared_attrs,
    }
    logger.debug("Starting video import with configuration %s", pformat(import_video_kwargs))
    media_ids = import_videos(token=token, **import_video_kwargs)
    logger.debug("Video import complete!")
    logger.info("Created the following media: %s", pformat(media_ids))

    logger.info(
        "Launching decryption workflow for %d media objects and %d metadata files",
        len(media_ids),
        len(file_ids),
    )

    # Launch one workflow for all media ids
    algorithm_name = config["Tator"]["AlgorithmName"]
    job_spec = {"algorithm_name": algorithm_name, "media_ids": media_ids}
    try:
        response = tator_api.create_job_list(project=project_id, job_spec=job_spec)
    except Exception:
        logger.error(
            "Could not launch job with job_spec=%s in project %d",
            pformat(job_spec),
            project_id,
            exc_info=True,
        )
    else:
        logger.info(
            "Launched workflow %s on media %s (received response %s)",
            algorithm_name,
            pformat(media_ids),
            pformat(response),
        )
