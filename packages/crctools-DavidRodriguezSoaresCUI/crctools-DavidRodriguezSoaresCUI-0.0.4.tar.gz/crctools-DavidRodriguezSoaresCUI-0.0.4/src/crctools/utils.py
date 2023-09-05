"""Supporting methods and classes for __main__"""

import enum
import logging
import re
import zlib
from pathlib import Path
from time import time

BLOCK_SIZE = 2**16
CRC_IN_FILENAME_PATTERN = re.compile(r"(\[[A-F0-9]{8}\])", re.IGNORECASE)
LOG = logging.getLogger(__file__)
SI_SUFFIX = {"K": 1_000, "M": 1_000_000, "G": 1_000_000_000}


class ChangeDetectDict(dict):
    """Normal dict but has the ability to detect if it was edited since initialization.
    Should be initialised from method from_dict"""

    EDIT_DETECT_FIELD: str = "__edit_detect__"

    def __setitem__(self, __key, __value) -> None:
        """Records that dict was edited"""
        setattr(self, ChangeDetectDict.EDIT_DETECT_FIELD, True)
        super().__setitem__(__key, __value)

    def __delitem__(self, __key) -> None:
        """Records that dict was edited"""
        setattr(self, ChangeDetectDict.EDIT_DETECT_FIELD, True)
        super().__delitem__(__key)

    @property
    def was_edited(self) -> bool:
        """Returns true if dict was edited"""
        return getattr(self, ChangeDetectDict.EDIT_DETECT_FIELD, False)

    @staticmethod
    def from_dict(d: dict) -> "ChangeDetectDict":
        """Creates instance of ChangeDetectDict from dict"""
        instance = ChangeDetectDict(d)
        setattr(instance, ChangeDetectDict.EDIT_DETECT_FIELD, False)
        return instance


class Status(enum.Enum):
    """Represents the different status a file processed can have"""

    SKIPPED = enum.auto()
    VERIFIED = enum.auto()
    COMPUTED = enum.auto()
    ERROR = enum.auto()


def human_parse_int(s: str) -> int | str:
    """Decodes values such as:
    - 12.5k => 12500
    - -44G => -44000000
    """
    if len(s) < 1:
        return s
    if len(s) > 1 and (suffix := s[-1].upper()) in SI_SUFFIX:
        # try:
        #     base_value = int(s[:-1])
        #     return base_value * SI_SUFFIX[suffix]
        # except ValueError:
        try:
            base_value = float(s[:-1])
            return int(base_value * SI_SUFFIX[suffix])
        except ValueError:
            return s
    try:
        return int(s)
    except ValueError:
        return s


def contains_subdirectories(_dir: Path) -> bool:
    """Checks whether a directory contains subdirectories"""
    return any([x.is_dir() for x in _dir.glob("*")])


def get_available_file_path(directory: Path, filename: str, suffix: str) -> Path:
    """Returns available file path, adds ' (<idx>)' suffix to filename as needed"""
    i = 0
    while True:
        p: Path = directory / (
            filename + suffix if i == 0 else f"{filename} ({i}){suffix}"
        )
        if not p.exists():
            return p
        i += 1


def file_crc32(_file: Path) -> int:
    """Returns _file's digest
    code based on maxschlepzig's answer
      https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    """
    b = bytearray(BLOCK_SIZE)
    mv = memoryview(b)
    digest: int = 0
    with _file.open("rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            digest = zlib.crc32(mv[:n], digest)  # data, value
    return digest


def crc32_digest_to_normalized_string(digest: int) -> str:
    """Returns CRC32 digest as a 8-character uppercase hexadecimal value representation"""
    return hex(digest)[2:].rjust(8, "0").upper()


def file_crc32_str(_file: Path) -> str:
    """Returns the file's CRC32 digest as a 8-character uppercase hexadecimal value representation"""
    return crc32_digest_to_normalized_string(file_crc32(_file))


def string_crc32_str(s: str) -> str:
    """Returns the string's CRC32 digest as a 8-character uppercase hexadecimal value representation"""
    return crc32_digest_to_normalized_string(zlib.crc32(s.encode()))


def filename_extract_crc(filename: str) -> tuple[str | None, str]:
    """Returns (<crc_if_found:str|None>, <filename_without_crc:str>)"""
    match = re.search(CRC_IN_FILENAME_PATTERN, filename)
    if not match:
        return None, filename
    a, b = match.span()
    return match.group(1)[1:-1], filename[:a] + filename[b:]


def verify_file(
    _file: Path,
    overwrite_digest: bool = False,
    skip_verify: bool = False,
    read_only_filename: bool = False,
    local_hash_db: dict[str, str] | None = None,
    frozen_dir_root: Path | None = None,
) -> Status:
    """Compute file's digest, then either checks integrity if file has digest in name
    or adds digest to name.

    Note: CRC in filename must be 8-character hexadecimal in square brackets (case insensitive)

    Integrity verification: Displays a warning message on mismatch of computed
    digest and the one found in name.

    `overwrite_digest`: If True, overwrite digest in name in cases of failed
    integrity verification.
    """
    expected_digest, stem_without_digest = filename_extract_crc(_file.stem)
    local_hash_db_key = None
    if expected_digest is not None and skip_verify:
        LOG.debug("[SKIPPED] %s: already has hash in file name", _file)
        return Status.SKIPPED
    if (
        expected_digest is None
        and read_only_filename is True
        and local_hash_db is not None
    ):
        local_hash_db_key = _file.relative_to(frozen_dir_root).as_posix()  # type: ignore[arg-type]
        expected_digest = local_hash_db.get(local_hash_db_key)

    file_size_MB = _file.stat().st_size / 1_000_000
    start_t = time()
    digest = file_crc32_str(_file)
    try:
        performance_MBps = f"[{file_size_MB / (time() - start_t):0.1f} MB/s]"
    except ZeroDivisionError:
        performance_MBps = "[TOO_FAST MB/s]"
    rename_target = False
    return_status = None
    if expected_digest is None:
        # Case : no digest in filename => add it
        LOG.info("[COMPUTED] %s %s: CRC is %s", _file.name, performance_MBps, digest)
        return_status = Status.COMPUTED
        rename_target = True
    elif digest == expected_digest.upper():
        # Case : digest in filename AND digests match => verification ok, no renaming to do
        LOG.info("[VERIFIED] %s %s", _file.name, performance_MBps)
        return_status = Status.VERIFIED
    else:
        # Case : digest in filename AND digests don't match => verification failed, renaming to do conditionally
        LOG.info(
            "[ERROR] %s %s: expected %s, computed %s",
            _file.name,
            performance_MBps,
            expected_digest.upper(),
            digest,
        )
        return_status = Status.ERROR
        rename_target = overwrite_digest

    if rename_target:
        if read_only_filename:
            # store digest in local db
            local_hash_db[local_hash_db_key] = digest  # type: ignore[index]
        else:
            # rename file
            new_name = get_available_file_path(
                _file.parent,
                stem_without_digest
                + ("" if stem_without_digest.endswith("]") else " ")
                + ("" if expected_digest is None else f"[!{expected_digest}]")
                + f"[{digest}]",
                _file.suffix,
            )
            LOG.info("[RENAMING] '%s' -> '%s'", _file.name, new_name.name)
            _file.rename(new_name)

    return return_status
