#!/usr/bin/env python3

from glob import glob
import hashlib
import logging
import os
from pprint import pformat
from typing import Dict, List

import tator
from tator.openapi.tator_openapi.models import CreateListResponse, UploadInfo
from tator.util._upload_file import _upload_file
from tqdm import tqdm


logger = logging.getLogger(__name__)


def _calculate_md5(file_path):
    hash_md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def _import_video(
    host: str,
    token: str,
    path: str,
    project_id: int,
    media_type: int,
    file_ids: List[int],
    section: str,
    shared_attrs: Dict[str, str],
) -> int:
    tator_api = tator.get_api(host=host, token=token)

    # Perform idempotency check
    filename = os.path.basename(path)
    paginator = tator.util.get_paginator(tator_api, "get_media_list")
    page_iter = paginator.paginate(project=project_id, name=filename, type=media_type)
    try:
        media = next(media for page in page_iter for media in page)
    except (RuntimeError, StopIteration):
        # Bug in paginator will raise RuntimeError if zero entities are returned
        pass
    else:
        logger.debug("Found existing media %d with same file name, skipping upload", media.id)
        return media.id

    # Upload encrypted file to Tator
    logger.debug("Uploading %s", filename)
    response = None
    try:
        for progress, response in _upload_file(tator_api, project_id, path=path, filename=filename):
            logger.debug("Upload progress: %.1f%%", progress)
    except Exception as exc:
        raise RuntimeError(f"Raised exception while uploading '{filename}', skipping") from exc

    if not isinstance(response, UploadInfo) or response.key is None:
        raise RuntimeError(f"Did not upload '{filename}', skipping")

    logger.debug("Uploading %s successful!", filename)

    # Create a media object containing the key to the uploaded file
    media_spec = {
        "type": media_type,
        "section": section,
        "name": filename,
        "md5": _calculate_md5(path),
        "attributes": {
            **shared_attrs,
            "encrypted_path": response.key,
            "related_files": ",".join(str(file_id) for file_id in file_ids),
        },
    }

    logger.debug(
        "Creating media object in project %d with media_spec=%s", project_id, pformat(media_spec)
    )
    try:
        response = tator_api.create_media_list(project_id, [media_spec])
    except Exception as exc:
        raise RuntimeError(f"Could not create media with {project_id=} and {media_spec=}") from exc

    return response.id[0] if isinstance(response, CreateListResponse) and response.id else 0


def import_videos(
    *,
    host: str,
    token: str,
    directory: str,
    media_ext: str,
    project_id: int,
    media_type: int,
    section: str,
    file_ids: List[int],
    shared_attrs: Dict[str, str],
) -> List[int]:
    """
    Finds all encrypted video files in `directory`, uploads them to Tator, and creates a media
    object referencing the upload. A future algorithm will be responsible for decrypting and
    transcoding them. Disallows use of positional arguments.

    :param host: The hostname of the Tator deployment to upload to.
    :type host: str
    :param token: The Tator API token to use for authentication.
    :type token: str
    :param directory: The directory to search for encrypted video files.
    :type directory: str
    :param media_ext: The extension of the encrypted video files.
    :type media_ext: str
    :param project_id: The integer id of the project to upload the videos to.
    :type project_id: int
    :param media_type: The integer id of the media type to create.
    :type media_type: int
    :param section: The section to import the media to.
    :type section: str
    :param file_ids: The list of file ids to associate imported media with.
    :type file_ids: List[int]
    :param shared_attrs: The dict of shared attributes for all media.
    :type shared_attrs: Dict[str, str]
    """
    file_list = glob(os.path.join(directory, f"*{media_ext}-[0-9]*"))
    logger.debug("Found the following files:\n* %s", "\n* ".join(file_list))

    results = []
    for filename in tqdm(
        file_list, total=len(file_list), desc="Video Imports", dynamic_ncols=True, position=0
    ):
        try:
            media_id = _import_video(
                host, token, filename, project_id, media_type, file_ids, section, shared_attrs
            )
        except Exception:
            logger.error("Failed to import '%s'", os.path.basename(filename), exc_info=True)
        else:
            if media_id:
                results.append(media_id)
    return results
