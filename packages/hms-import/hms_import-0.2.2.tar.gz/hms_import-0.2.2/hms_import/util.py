import logging
from typing import Any, Callable, Optional, Tuple

from tator.openapi.tator_openapi import FileType, MediaType, TatorApi

logger = logging.getLogger(__name__)


def validate_type_from_config(api, config, config_field, project_id, tator_type, list_filters=None):
    if tator_type not in ["media_type", "file_type"]:
        raise ValueError(f"Cannot validate {config_field=} for {tator_type=}")

    type_id = config["Tator"].getint(config_field, -1)
    if type_id > 0:
        try:
            getattr(api, f"get_{tator_type}")(type_id)
        except Exception as exc:
            raise ValueError(f"Could not find {config_field} with id {type_id}") from exc
    else:
        try:
            types = getattr(api, f"get_{tator_type}_list")(project_id)
        except Exception as exc:
            raise RuntimeError(f"Could not list {config_field}s from project {project_id}") from exc
        if list_filters:
            for attr, value in list_filters:
                types = [
                    _type
                    for _type in types
                    if hasattr(_type, attr) and getattr(_type, attr) == value
                ]
        if len(types) > 1:
            raise ValueError(
                f"Project {project_id} has more than one {config_field}, specify one of the "
                f"following in the config: {types}"
            )
        type_id = types[0].id
    return type_id


def safe_get_type(type_id: int, type_getter: Callable[[int], Any]):
    type_inst = None
    try:
        type_inst = type_getter(type_id)
    except Exception:
        logger.error("Could not find type %d", type_id, exc_info=True)
    return type_inst


def validate_types(
    tator_api: TatorApi, media_type_id: int, file_type_id: int
) -> Tuple[Optional[MediaType], Optional[FileType]]:
    """Validates media and file types by ensuring they both exist and belong to the same project."""
    return (
        safe_get_type(media_type_id, tator_api.get_media_type),
        safe_get_type(file_type_id, tator_api.get_file_type),
    )
