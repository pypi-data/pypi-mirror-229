from argparse import ArgumentParser, RawDescriptionHelpFormatter
import logging
from logging.handlers import TimedRotatingFileHandler
import os

import tator


def get_parser():
    parser = ArgumentParser(
        description="Script for importing video and metadata in O2 and B3 formats.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Changes the console log level from DEBUG to INFO"
    )
    cmd_parser = parser.add_subparsers(title="Commands", dest="command")

    upload_parser = cmd_parser.add_parser(
        "b3-upload", help="Imports video and GPS files from unlocked LUKS-encrypted device"
    )
    upload_parser = tator.get_parser(upload_parser)
    upload_parser.add_argument("--media-type-id", type=int)
    upload_parser.add_argument("--file-type-id", type=int)
    upload_parser.add_argument("--multi-type-id", type=int)
    upload_parser.add_argument("--state-type-id", type=int)
    upload_parser.add_argument("--image-type-id", type=int)
    upload_parser.add_argument("--directory", type=str)
    upload_parser.add_argument("--sail-date", type=str, required=False)
    upload_parser.add_argument("--land-date", type=str, required=False)
    upload_parser.add_argument("--hdd-recv-date", type=str, required=False)
    upload_parser.add_argument("--hdd-sn", type=str, required=False)

    import_parser = cmd_parser.add_parser(
        "o2-upload", help="Script for uploading raw, encrypted video files."
    )
    import_parser.add_argument(
        "config_file", type=str, help=f"The configuration .ini file used to initialize {__name__}."
    )
    return parser


def main() -> None:
    # Parse arguments
    parser = get_parser()
    args = parser.parse_args()
    argdict = vars(args)

    # Log everything to file, configure console level based on `--quiet` flag
    console_log_level = logging.INFO if argdict.pop("quiet") else logging.DEBUG
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)
    file_handler = TimedRotatingFileHandler(
        os.path.join(os.getcwd(), f"{__name__.split('.')[0]}.log"), when="midnight", backupCount=7
    )
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s - %(levelname)s - %(name)s]: %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Import the desired main function
    command = argdict.pop("command")
    if command == "o2-upload":
        from hms_import.o2 import main
    elif command == "b3-upload":
        from hms_import.b3 import main
    else:
        raise RuntimeError(f"Received unhandled command '{command}'")

    main(**argdict)
