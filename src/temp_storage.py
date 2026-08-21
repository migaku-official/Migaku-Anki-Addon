import atexit
import os
import shutil
import tempfile


temp_dir = tempfile.mkdtemp(prefix="migaku-anki-addon-")


def tmp_path(*path_parts):
    return os.path.join(temp_dir, *path_parts)


def cleanup():
    shutil.rmtree(temp_dir, ignore_errors=True)


atexit.register(cleanup)
