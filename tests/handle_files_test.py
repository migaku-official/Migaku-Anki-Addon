import importlib.util
import os
import sys
import tempfile
import types
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Lock


root = Path(__file__).parents[1]
temp_storage_path = root / "src" / "temp_storage.py"
temp_storage_spec = importlib.util.spec_from_file_location(
    "handle_files_test_temp_storage", temp_storage_path
)
temp_storage = importlib.util.module_from_spec(temp_storage_spec)
temp_storage_spec.loader.exec_module(temp_storage)


class FakeFFmpeg:
    def __init__(self):
        self.barrier = Barrier(2)
        self.lock = Lock()
        self.inputs = []
        self.outputs = []

    def call(self, *args):
        source = args[args.index("-i") + 1]
        output = args[-1]
        with self.lock:
            self.inputs.append(source)
            self.outputs.append(output)
        self.barrier.wait(timeout=5)
        with open(source, "rb") as source_file:
            data = source_file.read()
        with open(output, "wb") as output_file:
            output_file.write(data)
        return 0


with tempfile.TemporaryDirectory(prefix="migaku-media-test-") as media_dir:
    fake_ffmpeg = FakeFFmpeg()
    fake_aqt = types.ModuleType("aqt")
    fake_aqt.mw = types.SimpleNamespace(
        migaku_connection=types.SimpleNamespace(ffmpeg=fake_ffmpeg)
    )

    fake_config = types.ModuleType("handle_files_test_addon.config")
    fake_config.get = lambda key, default=None: {
        "convert_audio_mp3": True,
        "normalize_audio": False,
    }.get(key, default)

    fake_util = types.ModuleType("handle_files_test_addon.util")
    fake_util.col_media_path = lambda filename: os.path.join(media_dir, filename)
    fake_util.publish_file_atomically = temp_storage.publish_file_atomically
    fake_util.temporary_workspace = temp_storage.temporary_workspace
    fake_util.tmp_path = temp_storage.tmp_path

    fake_pydub = types.ModuleType("pydub")
    fake_pydub.AudioSegment = object

    fake_package = types.ModuleType("handle_files_test_addon")
    fake_package.__path__ = []
    fake_connection_package = types.ModuleType("handle_files_test_addon.migaku_connection")
    fake_connection_package.__path__ = []

    sys.modules["aqt"] = fake_aqt
    sys.modules["pydub"] = fake_pydub
    sys.modules["handle_files_test_addon"] = fake_package
    sys.modules["handle_files_test_addon.config"] = fake_config
    sys.modules["handle_files_test_addon.util"] = fake_util
    sys.modules["handle_files_test_addon.migaku_connection"] = fake_connection_package

    handle_files_path = root / "src" / "migaku_connection" / "handle_files.py"
    handle_files_spec = importlib.util.spec_from_file_location(
        "handle_files_test_addon.migaku_connection.handle_files", handle_files_path
    )
    handle_files = importlib.util.module_from_spec(handle_files_spec)
    handle_files_spec.loader.exec_module(handle_files)

    with temp_storage.temporary_workspace() as workspace:
        contained_path = handle_files.move_file_to_tmp_dir(
            b"contained", "/tmp/escaped.wav", workspace
        )
        assert os.path.dirname(contained_path) == workspace
        assert os.path.basename(contained_path) == "escaped.wav"

    contents = (b"first audio", b"second audio")
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(handle_files.handle_audio_file, data, "shared.wav", "wav")
            for data in contents
        ]
        filenames = [future.result() for future in futures]

    assert filenames == ["shared.mp3", "shared.mp3"]
    assert len(set(fake_ffmpeg.inputs)) == 2
    assert len(set(fake_ffmpeg.outputs)) == 2
    assert all(os.path.dirname(path) != media_dir for path in fake_ffmpeg.outputs)
    assert all(not os.path.exists(os.path.dirname(path)) for path in fake_ffmpeg.outputs)

    with open(os.path.join(media_dir, "shared.mp3"), "rb") as media_file:
        assert media_file.read() in contents

temp_storage.cleanup()

print("✓ concurrent audio conversions publish complete isolated media")
