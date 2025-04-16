import os
from pathlib import Path
from typing import List


class DirectoryNotFound(Exception):
    def __init__(self, message):
        self.message = message


def find_file(filename: str, skip: str | None = None) -> Path:
    """Function to find find file

    Finds paths to a file with a certain filename.
    You can also skip certain directories with 'skip'

    Args:
        filename: Name of the file to find
        skip: Name of the directory to skip

    Returns:
        Path to the file

    Raises:
        FileNotFoundError: Raised if the file can not be found
    """
    basedir = Path(__file__)

    if skip is not None:
        for parent in basedir.parents:
            if not parent.match(skip):
                current = parent.rglob(filename)
                for path in current:
                    if path.exists():
                        return path
    else:
        for parent in basedir.parents:
            current = parent.rglob(filename)
            for path in current:
                if path.exists():
                    return path

    raise FileNotFoundError(f"Can not find file '{filename}'")


def find_dir(dirname: str) -> Path:
    basedir = Path(__file__)
    subpath = "data"

    for parent in basedir.parents:
        current = parent / subpath
        if current.exists():
            datadir = current
            break
    target = datadir / dirname
    if not target.exists():
        os.makedirs(target)
    return target


def find_retrieval(name: str) -> Path:
    """Function to find retrieval

    Args:
        name: Name of the retrieval

    Returns:
        Path to the retrieval

    Raises:
        FileNotFoundError: Raise if file can not be found
    """
    filep = Path(__file__)
    subpath = "data/simulation"

    for parent in filep.parents:
        current = parent / subpath / name
        if current.exists():
            return current
    raise FileNotFoundError(f"Can not find file: {name}")


def find_files() -> tuple[List[Path], List[Path]]:
    """Find paths to measurement and ycalc data

    Returns:
        List of file paths

    Raises:
        FileNotFoundError: Raise if measurement and/or simulation
        data cannot be found
    """
    measdir = find_dir(dirname="measurements/240104")
    simdir = find_dir(dirname="simulation")

    meas = [path for path in measdir.rglob("Data*")]
    sims = [path for path in simdir.rglob("YCALC_*")]

    if len(meas) == 0 or len(sims) == 0:
        raise FileNotFoundError(
            "Can not find paths to measurement\
                                 and/or simulations"
        )
    else:
        return meas, sims


def imgs_path() -> Path:
    """Function to find imgs directory

    Returns:
        Pat to imgs directory

    Raises:
        DirectoryNotFound: Raise if directory cannor be found
    """
    root = Path(__file__)
    datadir = "data"

    for parent in root.parents:
        current = parent / datadir

        if current.exists():
            imgsdir = current / "imgs"
            if not imgsdir.exists():
                os.makedirs(imgsdir)
            return imgsdir
    raise DirectoryNotFound("Cannot locate data directory")
