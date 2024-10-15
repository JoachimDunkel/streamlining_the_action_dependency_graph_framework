from datetime import datetime
from pathlib import Path
from typing import Union


def get_all_files_in_directory(directory: Union[str, Path], file_extension=""):
    directory = Path(directory)
    glob_pattern = '**/*'
    if file_extension != "" and "." not in file_extension:
        file_extension = f".{file_extension}"
    files = list(directory.glob(glob_pattern + file_extension))
    files = [f for f in files if f.is_file()]
    return sorted(files)


def append_timestamp_to_filename(file_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = file_path.stem
    suffix = file_path.suffix
    new_file_name = f"{stem}_{timestamp}{suffix}"
    return file_path.with_name(new_file_name)
