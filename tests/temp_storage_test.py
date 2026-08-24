import importlib.util
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier


module_path = Path(__file__).parents[1] / "src" / "temp_storage.py"
spec = importlib.util.spec_from_file_location("temp_storage", module_path)
temp_storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(temp_storage)


assert temp_storage.tmp_path().startswith(temp_storage.temp_dir)
assert not temp_storage.tmp_path().startswith(str(module_path.parents[1]))

temp_path = temp_storage.tmp_path("nested", "audio.m4a")
assert os.path.dirname(temp_path) == os.path.join(temp_storage.temp_dir, "nested")

barrier = Barrier(2)


def use_same_named_file(contents):
    with temp_storage.temporary_workspace() as workspace:
        path = os.path.join(workspace, "audio.m4a")
        with open(path, "wb") as file:
            file.write(contents)
        barrier.wait()
        with open(path, "rb") as file:
            assert file.read() == contents
        return workspace, path


with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [
        executor.submit(use_same_named_file, contents)
        for contents in (b"first", b"second")
    ]
    workspaces_and_paths = [future.result() for future in futures]

workspaces = [workspace for workspace, _ in workspaces_and_paths]
paths = [path for _, path in workspaces_and_paths]
assert workspaces[0] != workspaces[1]
assert paths[0] != paths[1]
assert all(not os.path.exists(workspace) for workspace in workspaces)

temp_storage.cleanup()
assert not os.path.exists(temp_storage.temp_dir)

recreated_legacy_path = temp_storage.tmp_path("audio.m4a")
assert os.path.isdir(temp_storage.temp_dir)
assert os.path.dirname(recreated_legacy_path) == temp_storage.temp_dir

temp_storage.cleanup()
assert not os.path.exists(temp_storage.temp_dir)

with temp_storage.temporary_workspace() as recreated_workspace:
    assert os.path.isdir(recreated_workspace)

assert not os.path.exists(recreated_workspace)

temp_storage.cleanup()
assert not os.path.exists(temp_storage.temp_dir)

print("✓ temporary media storage is outside the add-on installation directory")
