import os
from pathlib import Path
import subprocess
import requests
import zipfile
import appdirs
from threading import Lock

import aqt
from anki.utils import is_lin, is_mac, is_win

from .. import util
from .. import config


# Migaku addition to prevent window flashing
class subp:
    if hasattr(subprocess, "STARTUPINFO"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        @classmethod
        def call(cls, *args, **kwargs):
            return subprocess.check_call(*args, **kwargs, startupinfo=cls.startupinfo)

    else:

        @classmethod
        def call(cls, *args, **kwargs):
            return subprocess.check_call(*args, **kwargs)


class ProgramManager(aqt.qt.QObject):
    BASE_DOWNLOAD_URI = "https://migaku-public-data.migaku.com/"
    lock = Lock()
    total_progress_dict = {}
    progress_dict = {}

    def __init__(self, program_name: str, parent=None):
        super().__init__(parent)

        self.program_path = None
        self.program_name = program_name
        self.download_uri = self.BASE_DOWNLOAD_URI + program_name + "/"

        self.program_executable_name = f"{program_name}.exe" if is_win else program_name

        self.local_program_path = util.user_path(self.program_executable_name)

        self.migaku_shared_path = appdirs.user_data_dir("MigakuShared", "Migaku")
        self.shared_user_program_name = os.path.join(
            self.migaku_shared_path, self.program_executable_name
        )

        self.make_available()

    def is_available(self):
        return self.program_path is not None

    def call(self, *args, **kwargs):
        assert self.is_available()
        return subp.call([self.program_path, *args], **kwargs)

    def make_available(self):
        # Attempt global installation
        if self.check_set_program_path(self.program_executable_name):
            return

        # Attempt local installation
        if self.check_set_program_path(self.local_program_path):
            return

        if self.check_set_program_path(self.shared_user_program_name):
            return

        # Install ffmpeg
        self.start_download()

    def start_download(self):
        class DownloadThread(aqt.qt.QThread):
            def __init__(self, target=None, parent=None):
                super().__init__(parent)
                self.target = target

            def run(self):
                self.target()

        aqt.mw.progress.start(label=f"Downloading ffmpeg and ffprobe", max=100)

        self.program_path = self.migaku_shared_path + "/" + self.program_executable_name
        print(self.program_path)
        download_thread = DownloadThread(self._download, self.parent())
        download_thread.finished.connect(self.finished_download)
        download_thread.start()

    def finished_download(self):
        aqt.mw.progress.finish()

        if not self.check_set_program_path(self.shared_user_program_name):
            util.show_critical(
                f"Downloading {self.program_name} failed.\n\n"
                "It is required for converting media files during card creation.\n\n"
                "Please make sure that you are connected to the internet and restart Anki.\n\n"
                f"{self.program_name} only has to be downloaded once."
            )

    def _download(self):
        # download ffmpeg zip
        def fmt_mb(n):
            return f"{n//1000000}MB"

        download_path = util.tmp_path(f"{self.program_name}-download")
        try:
            with open(download_path, "wb") as f:
                with requests.get(self.os_download_uri(), stream=True) as r:
                    total = int(r.headers["Content-Length"])
                    overall_total = 0
                    print(f"Downloading {fmt_mb(total)} for {self.program_name}")
                    with self.lock:
                        self.total_progress_dict[self.program_name] = total
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pos = f.tell()
                            with self.lock:
                                for program_name in self.total_progress_dict:
                                    if program_name != self.program_name:
                                        overall_total = (
                                            total
                                            + self.total_progress_dict[program_name]
                                        )
                                self.progress_dict[self.program_name] = pos
                                for key in self.progress_dict:
                                    if key != self.program_name:
                                        pos += self.progress_dict[key]

                            label = f"Downloading ffmpeg and ffprobe\n({fmt_mb(pos)}/{fmt_mb(overall_total)})"

                            aqt.mw.taskman.run_on_main(
                                lambda: aqt.mw.progress.update(
                                    value=pos, max=overall_total, label=label
                                )
                            )
        except requests.HTTPError:
            return

        # extract ffmpeg executable from downloaded zip into user_data
        aqt.mw.taskman.run_on_main(
            lambda: aqt.mw.progress.update(
                value=0, max=0, label=f"Extracting {self.program_name}"
            )
        )

        with zipfile.ZipFile(download_path) as zf:
            zf.extractall(self.migaku_shared_path)

        # make program executable
        if not is_win:
            try:
                os.chmod(self.shared_user_program_name, 0o755)
            except OSError:
                pass

    def os_download_uri(self):  # sourcery skip: use-fstring-for-concatenation
        if is_lin:
            return self.download_uri + "linux.zip"
        if is_mac:
            return self.download_uri + "macos.zip"
        if is_win:
            return self.download_uri + "windows.zip"
        raise NotImplementedError("OS not supported")

    def check_set_program_path(self, path):
        if not path:
            return False
        try:
            subp.call([path, "-version"])
            self.program_path = path
            return True
        except OSError:
            return False
