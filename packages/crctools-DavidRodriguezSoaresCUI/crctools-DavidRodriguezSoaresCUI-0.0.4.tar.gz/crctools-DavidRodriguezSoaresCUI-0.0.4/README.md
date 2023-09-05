# [crctools](https://github.com/DavidRodriguezSoaresCUI/crctools) - A simple tool to check file integrity using CRC32 hash in filename

Having the hash of files in their name makes it so much easier to:
- keep track of their integrity
- deduplicate files
- probably more

This is intended to be a simple to use command-line utility to:
- add CRC32 hash into filename in a widely recognised format (suffix with 8 hex uppercase characters in square brackets)
- verify integrity of files based on hash in file name
- update hash in name

## Requirements

This project was developed for Python 3.10 and may not work on lower versions.

## Installation

From a terminal execute:

```bash
python -m pip install crctools-DavidRodriguezSoaresCUI
```

On some systems it may be necessary to specify python version as `python3`

## Usage

```bash
$> python -m crctools --help
usage: __main__.py [-h] [--skip_verify] [--overwrite] [--recursive] [--extensions [EXTENSIONS ...]]
                   [--min_size MIN_SIZE] [--write_report] [--skip_frozen_dirs]
                   [--frozen_dirs [FROZEN_DIRS ...]]
                   [--frozen_dir_file_ext [FROZEN_DIR_FILE_EXT ...]] [--debug]
                   PATH

positional arguments:
  PATH                  Can be file path or directory (all files in directory will be processed)

options:
  -h, --help            show this help message and exit
  --skip_verify         Skip verification; only process files with no hash in filename (useful to
                        resume interrupted execution)
  --overwrite           Overwrite CRC in filename when verification fails
  --recursive           (Only with PATH a directory) Enables recursive search for files to verify
  --extensions [EXTENSIONS ...]
                        Restrict files to process with extension whitelist (default: no restriction;
                        you may list extensions with leading dot separator)
  --min_size MIN_SIZE   Restrict files to ones of at least <min_size> bytes; accepts values like
                        '-4.4k', '99G' or '0.5M' (case insensitive); default: 0)
  --write_report        Writes JSON file with list of files processed by category: COMPUTED,
                        VERIFIED, ERROR
  --skip_frozen_dirs    Skip frozen dirs (see --frozen_dirs)
  --frozen_dirs [FROZEN_DIRS ...]
                        Name of directories that should be treated as read-only (so no file
                        renaming); default: VIDEO_TS BDMV
  --frozen_dir_file_ext [FROZEN_DIR_FILE_EXT ...]
                        List of file extensions typically associated with frozen directories (used
                        for warning); default: IFO BUP VOB M2TS BDMV MPLS CLPI
```

Example: Check large (>10MB) video files in directory `D:\Videos` (and subdirectories) :
```
python -m crctools "D:\Vidéos" --recursive --extensions mkv mp4 --min_size 10M
```

Note: these are all equivalent:
- `--extensions mkv mp4`
- `--extensions .mkv .mp4`
- `--extensions MKV MP4`
- `--extensions .MKV .MP4`

I typically use:
```
python -m crctools . --recursive --extension 7Z AAC AC3 APK AVI FLAC FLV ISO M2TS M4A M4V MKV MOV MP4 MPEG MPG NDS PDF RAR RMVB TS WAV WBFS WEBM WMV ZIP --min_size 20M --write_report
```




### Concept of `frozen directories`

Some directories, like DVD/BD disk backups, have a known directory structure and shouldn't be changed by adding hash into file names. Instead, all files inside are hashed, their hashes collected into a file outside the directory, and that file hashed to give a "composite" hash that represents the whole directory.