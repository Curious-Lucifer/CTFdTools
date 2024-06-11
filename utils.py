import os, os.path
import re
import sys
import zipfile
from contextlib import contextmanager


@contextmanager
def change_path(target_path: str):
    origin_path = os.getcwd()
    try:
        os.chdir(target_path)
        yield
    finally:
        os.chdir(origin_path)


def check_canonical(s: str):
    return re.match(r'^[a-z0-9-]+$', s) is not None


def compress2zip(path_list: list[str], output_path: str):
    archive_files = {}
    
    for path in path_list:
        if os.path.isfile(path):
            archive_files[path2archivepath(path, output_path)] = path

        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_files[path2archivepath(file_path, output_path)] = file_path

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for archivepath, path in archive_files.items():
            zipf.write(path, archivepath)


def path2archivepath(path: str, output_path: str):
    archive_dirname = os.path.normpath(output_path).split(os.sep)[-1].removesuffix('.zip')
    parts = os.path.normpath(path).split(os.sep)
    parts[0] = archive_dirname
    return os.path.join(*parts)


def info(*args):
    print('[\033[94m*\033[0m]', *args)


def success(*args):
    print('[\033[92m+\033[0m]', *args)


def error(*args):
    print('[\033[91mX\033[0m]', *args, file=sys.stderr)

