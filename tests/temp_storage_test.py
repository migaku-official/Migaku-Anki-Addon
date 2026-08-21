import importlib.util
import os
from pathlib import Path


module_path = Path(__file__).parents[1] / "src" / "temp_storage.py"
spec = importlib.util.spec_from_file_location("temp_storage", module_path)
temp_storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(temp_storage)


assert temp_storage.tmp_path().startswith(temp_storage.temp_dir)
assert not temp_storage.tmp_path().startswith(str(module_path.parents[1]))

temp_path = temp_storage.tmp_path("nested", "audio.m4a")
assert os.path.dirname(temp_path) == os.path.join(temp_storage.temp_dir, "nested")

temp_storage.cleanup()
assert not os.path.exists(temp_storage.temp_dir)

print("✓ temporary media storage is outside the add-on installation directory")
