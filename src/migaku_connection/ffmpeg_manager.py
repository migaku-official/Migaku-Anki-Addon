import os
import subprocess
import requests
import zipfile

import aqt
from anki.utils import isLin, isMac, isWin

from .. import util
from .. import config


class FFmpegManager(aqt.qt.QObject):

    DOWNLOAD_URI = 'http://dicts.migaku.io/ffmpeg/'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ffmpeg_path = None

        if isWin:
            executable_name = 'ffmpeg.exe'
        else:
            executable_name = 'ffmpeg'
        self.local_ffmpeg_path = util.user_path(executable_name)

        self.make_avaialble()


    def is_available(self):
        return not self.ffmpeg_path is None

    
    def call(self, *args, **kwargs):
        assert self.is_available()
        return subprocess.call([self.ffmpeg_path, *args], **kwargs)


    def make_avaialble(self):
        # Attempy path set in config
        if self.check_set_ffmpeg_path(config.get('ffmpeg')):
            return

        # Attempt global installation
        if self.check_set_ffmpeg_path('ffmpeg'):
            return
        
        # Attempt local installation
        if self.check_set_ffmpeg_path(self.local_ffmpeg_path):
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

        aqt.mw.progress.start(label='Downloading FFmpeg', max=100)

        download_thread = DownloadThread(self._download, self.parent())
        download_thread.finished.connect(self.finished_download)
        download_thread.start()
       

    def finished_download(self):
        aqt.mw.progress.finish()

        if not self.check_set_ffmpeg_path(self.local_ffmpeg_path):
            util.show_critical(
                'Downloading FFmpeg failed.\n\n'
                'It is required for converting media files during card creation.\n\n'
                'Please make sure that you are connected to the internet and restart Anki.\n\n'
                'FFmpeg only has to be downloaded once.')

    def _download(self):
        # download ffmpeg zip
        def fmt_kb(n):
            return F'{n//1000}kB'

        download_path = util.tmp_path('ffmpeg-download')
        try:
            with open(download_path, 'wb') as f:
                with requests.get(self.os_download_uri(), stream=True) as r:
                    total = int(r.headers['Content-Length'])
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pos = f.tell()

                            label = F'Downloading FFmpeg\n({fmt_kb(pos)}/{fmt_kb(total)})'

                            aqt.mw.taskman.run_on_main(
                                lambda: aqt.mw.progress.update(value=pos, max=total, label=label)
                            )
        except requests.HTTPError:
            return

        # extract ffmpeg executable from downloaded zip into user_data
        aqt.mw.taskman.run_on_main(
            lambda: aqt.mw.progress.update(value=0, max=0, label='Extracting FFmpeg')
        )

        with zipfile.ZipFile(download_path) as zf:
            zf.extractall(util.user_path())

        # make ffmpeg executable
        if not isWin:
            try:
                os.chmod(self.local_ffmpeg_path, 0o755)
            except OSError:
                pass


    def os_download_uri(self):
        if isLin:
            return self.DOWNLOAD_URI + 'linux'
        if isMac:
            return self.DOWNLOAD_URI + 'macos'
        if isWin:
            return self.DOWNLOAD_URI + 'windows'
        raise NotImplementedError('OS not supported')


    def check_set_ffmpeg_path(self, path):
        if not path:
            return False
        try:
            subprocess.call([path, '-version'])
            self.ffmpeg_path = path
            return True
        except OSError:
            return False
