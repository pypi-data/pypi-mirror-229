"""[crctools](https://github.com/DavidRodriguezSoaresCUI/crctools) - A simple tool to check file integrity using CRC32 hash in filename

see README for more info
"""

import argparse
import json
import logging
import re
import time
from collections import defaultdict
from pathlib import Path

from .utils import (
    ChangeDetectDict,
    Status,
    contains_subdirectories,
    get_available_file_path,
    human_parse_int,
    string_crc32_str,
    verify_file,
)

CWD = Path(".").resolve()
DVD_CONTENT_DIRECTORY = "VIDEO_TS"
BDMV_CONTENT_DIRECTORY = "BDMV"
DEFAULT_FROZEN_DIRECTORIES = {
    DVD_CONTENT_DIRECTORY,
    BDMV_CONTENT_DIRECTORY,
}
DEFAULT_FROZEN_DIRECTORIES_TYPICAL_FILE_EXTENSIONS = {
    "BUP",
    "IFO",
    "VOB",
    "BDMV",
    "CLPI",
    "MPLS",
    "M2TS",
}
LOG_LEVEL = logging.INFO
LOG = logging.getLogger(__file__)


def get_args() -> argparse.Namespace:
    """Parses and processes user-given CLI arguments"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "PATH",
        help="Can be file path or directory (all files in directory will be processed)",
    )
    parser.add_argument(
        "--skip_verify",
        action="store_true",
        help="Skip verification; only process files with no hash in filename (useful to resume interrupted execution)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite CRC in filename when verification fails",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="(Only with PATH a directory) Enables recursive search for files to verify",
    )
    parser.add_argument(
        "--extensions",
        action="store",
        nargs="*",
        help="Restrict files to process with extension whitelist (default: no restriction; you may list extensions with leading dot separator)",
    )
    parser.add_argument(
        "--min_size",
        action="store",
        default="0",
        help="Restrict files to ones of at least <min_size> bytes; accepts values like '-4.4k', '99G' or '0.5M' (case insensitive); default: 0)",
    )
    parser.add_argument(
        "--write_report",
        action="store_true",
        help="Writes JSON file with list of files processed by category: COMPUTED, VERIFIED, ERROR",
    )
    parser.add_argument(
        "--skip_frozen_dirs",
        action="store_true",
        help="Skip frozen dirs (see --frozen_dirs)",
    )
    parser.add_argument(
        "--frozen_dirs",
        nargs="*",
        default=DEFAULT_FROZEN_DIRECTORIES,
        help=f"Name of directories that should be treated as read-only (so no file renaming); default: {' '.join(DEFAULT_FROZEN_DIRECTORIES)}",
    )
    parser.add_argument(
        "--frozen_dir_file_ext",
        nargs="*",
        default=DEFAULT_FROZEN_DIRECTORIES_TYPICAL_FILE_EXTENSIONS,
        help=f"List of file extensions typically associated with frozen directories (used for warning); default: {' '.join(DEFAULT_FROZEN_DIRECTORIES_TYPICAL_FILE_EXTENSIONS)}",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="[%(levelname)s] %(message)s",
        level=logging.DEBUG if args.debug else logging.INFO,
    )
    if args.overwrite:
        LOG.warning("WARNING: Overwriting hash in name enabled")
    if args.frozen_dir_file_ext:
        args.frozen_dir_file_ext = {
            ("" if e.startswith(".") else ".") + e.upper()
            for e in args.frozen_dir_file_ext
        }
    if args.extensions:
        args.extensions = {
            ("" if e.startswith(".") else ".") + e.upper() for e in args.extensions
        }
        problematic_extensions = list(
            filter(lambda x: x in args.frozen_dir_file_ext, args.extensions)
        )
        if problematic_extensions:
            LOG.warning(
                "You selected extensions %s. Be aware that this programs detects some folder structures as 'frozen directories' (that are associated with these extensions) and thus behaves in a special way. See help for more.",
                problematic_extensions,
            )
    else:
        LOG.warning(
            "You didn't use argument '--extensions'. Be aware that this programs detects some folder structures as 'frozen directories' (that are associated with extensions %s) and thus behaves in a special way. See help for more.",
            args.frozen_dir_file_ext,
        )
    if not isinstance(args.frozen_dirs, set):
        if isinstance(args.frozen_dirs, list):
            args.frozen_dirs = set(args.frozen_dirs)
        else:
            raise ValueError(
                f"Unexpected type for --frozen_dirs: {type(args.frozen_dirs)}"
            )
    args.min_size_int = human_parse_int(args.min_size)
    if not isinstance(args.min_size_int, int):
        raise ValueError(f"Failed to parse '--min_size {args.min_size}': not a number")
    LOG.debug("args=%s", args)

    return args


def _process_file(
    _file: Path,
    args: argparse.Namespace,
    processed_files_by_status: dict[Status, list[Path]],
) -> None:
    """Filters files against extension list and min size if given, then computes hash and puts hash in file name.
    If hash is already in filename, verifies it"""
    has_valid_extension = (
        args.extensions is None or _file.suffix.upper() in args.extensions
    )
    if not has_valid_extension:
        if LOG.isEnabledFor(logging.DEBUG):
            LOG.debug(
                "[SKIPPED] %s: extension '%s' not in %s",
                _file,
                _file.suffix.upper(),
                args.extensions,
            )
        return
    if _file.stat().st_size < args.min_size_int:
        if LOG.isEnabledFor(logging.DEBUG):
            LOG.debug(
                "[SKIPPED] %s: file of size %s lower than bound %s",
                _file,
                _file.stat().st_size,
                args.min_size,
            )
        return

    # Case: hash can't be stored in filename
    return_status = verify_file(_file, args.overwrite, args.skip_verify)
    if return_status is not Status.SKIPPED:
        processed_files_by_status[return_status].append(_file)


def process_file(
    _file: Path,
    args: argparse.Namespace,
    processed_files_by_status: dict[Status, list[Path]],
) -> None:
    """Catches errors from process_file execution"""
    try:
        _process_file(_file, args, processed_files_by_status)
    except Exception as e:
        LOG.error("%s: something went wrong\n{e}\n", _file.name)
        processed_files_by_status[Status.ERROR].append(_file)
        if args.debug:
            raise e


def process_frozen_dir(
    _dir: Path,
    args: argparse.Namespace,
    processed_files_by_status: dict[Status, list[Path]],
) -> None:
    """Process files in directory; directory or its contents may not be changed"""

    LOG.info(
        "Directory '%s' detected as a 'frozen directory' => switch to local hash database",
        _dir,
    )

    if contains_subdirectories(_dir) and not args.recursive:
        raise ValueError(
            f"Can't process directory '{_dir}' without --recursive: frozen dir with subdirectories"
        )

    local_hash_file: Path | None = None
    local_hash_file_pattern = re.compile(_dir.name + r"\.[A-F0-9]{8}\.json")
    potential_local_hash_files = list(
        x for x in _dir.parent.glob("*.json") if local_hash_file_pattern.match(x.name)
    )
    if len(potential_local_hash_files) == 1:
        local_hash_file = potential_local_hash_files[0]
        if args.skip_verify:
            LOG.info(
                "Found local hash file %s => skipping because --skip_verify",
                local_hash_file.name,
            )
            return
        LOG.info("Found local hash file %s", local_hash_file.name)
    if len(potential_local_hash_files) > 1:
        raise ValueError(
            f"Unexpectedly found multiple hash files for directory '{_dir}': {potential_local_hash_files}"
        )

    local_hashes = ChangeDetectDict.from_dict(
        json.loads(local_hash_file.read_text(encoding="utf8"))
        if local_hash_file is not None and local_hash_file.exists()
        else {}
    )

    for item in _dir.rglob("*"):
        if item.is_file():
            return_status = verify_file(
                item,
                args.overwrite,
                args.skip_verify,
                read_only_filename=True,
                local_hash_db=local_hashes,
                frozen_dir_root=_dir,
            )
            if return_status is not Status.SKIPPED:
                processed_files_by_status[return_status].append(item)

    # Save local hashes if modified (removes previous local hash file)
    if local_hashes is not None and local_hashes.was_edited:
        hash_db_json = json.dumps(local_hashes, sort_keys=True, indent=2)
        if local_hash_file is not None:
            LOG.info("Overwriting local hash file '%s'", local_hash_file)
            local_hash_file.unlink()
        local_hash_file = (
            _dir.parent / f"{_dir.name}.{string_crc32_str(hash_db_json)}.json"
        )
        LOG.info("Writing local hash file '%s'", local_hash_file)
        local_hash_file.write_text(hash_db_json, encoding="utf8")


def process_dir(
    _dir: Path,
    args: argparse.Namespace,
    processed_files_by_status: dict[Status, list[Path]],
) -> None:
    """Process files in directory; recursive search if --recursive given"""

    # For technical reasons the directory structure of DVD/BDMV disk backups shouldn't be altered
    # so modifying file names to add hash is replaced by storing hashes into a file
    if _dir.name in args.frozen_dirs:
        if args.skip_frozen_dirs:
            LOG.info("Skipping frozen dir '%s'", _dir)
        else:
            process_frozen_dir(_dir, args, processed_files_by_status)
        return

    for item in _dir.glob(pattern="*"):
        if item.is_file():
            process_file(
                item,
                args,
                processed_files_by_status,
            )
        elif item.is_dir() and args.recursive:
            process_dir(item, args, processed_files_by_status)


def main() -> None:
    """Main function"""
    # Get arguments
    args = get_args()

    # Process file(s)
    _path = Path(args.PATH).resolve()
    processed_files_by_status: dict[Status, list[Path]] = defaultdict(list)
    if not _path.exists():
        raise FileNotFoundError(f"Couldn't find a file or directory at '{_path}'")

    try:
        if _path.is_dir():
            process_dir(_path, args, processed_files_by_status)
        elif _path.is_file():
            process_file(_path, args, processed_files_by_status)
        else:
            raise ValueError(
                f"Unhandled case: Path '{_path}' exists but is neither a directory or a file"
            )
    except KeyboardInterrupt:
        print("Program interrupted")

    # Save report to file
    if args.write_report:
        json_report_file = get_available_file_path(
            CWD, time.strftime("%Y%m%d-%H%M%S"), ".json"
        )
        LOG.info("Saving execution report to %s", json_report_file.name)
        with json_report_file.open("w", encoding="utf8") as f:
            json.dump(
                {k.name: v for k, v in processed_files_by_status.items()},
                f,
                default=str,
                indent=2,
                ensure_ascii=False,
            )


if __name__ == "__main__":
    main()
