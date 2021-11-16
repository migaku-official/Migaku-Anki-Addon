from os.path import join, exists
import os
import subprocess
from .migaku_http_handler import MigakuHTTPHandler


class AudioCondenser(MigakuHTTPHandler):

    def get(self):
        self.finish("ImportHandler")

    def ffmpegExists(self):
        if exists(self.ffmpeg):
            return True
        return False

    def removeTempFiles(self):
        tmpdir = self.tempDirectory
        filelist = [f for f in os.listdir(tmpdir)]
        for f in filelist:
            path = os.path.join(tmpdir, f)
            try:
                os.remove(path)
            except:
                innerDirFiles = [df for df in os.listdir(path)]
                for df in innerDirFiles:
                    innerPath = os.path.join(path, df)
                    os.remove(innerPath)
                os.rmdir(path)

    def condenseAudioUsingFFMPEG(self, filename, timestamp, config):
        print("FFMPEG REACHED")
        wavDir = join(self.tempDirectory, timestamp)
        if exists(wavDir):
            config = self.getConfig()
            mp3dir = config.get('condensed-audio-dir', False)
            wavs = [f for f in os.listdir(wavDir)]
            wavs.sort()
            wavListFilePath = join(wavDir, "list.txt")
            wavListFile = open(wavListFilePath, "w+")
            print(filename)
            filename = self.cleanFilename(filename + "\n") + "-condensed.mp3"
            mp3path = join(mp3dir, filename)
            print(wavs)
            for wav in wavs:
                wavListFile.write("file '{}'\n".format(join(wavDir, wav)))
            wavListFile.close()
            subprocess.call([self.ffmpeg, '-y', '-f', 'concat', '-safe',
                            '0', '-i', wavListFilePath, '-write_xing', '0', mp3path])
            self.removeTempFiles()
            if not config.get('disable-condensed-audio-messages', False):
                self.alert("A Condensed Audio File has been generated.\n\n The file: " +
                           filename + "\nhas been created in dir: " + mp3dir)

    def cleanFilename(self, filename):
        return re.sub(r"[\n:'\":/\|?*><!]", "", filename).strip()

    def post(self):
        if self.checkVersion():
            config = self.getConfig()
            timestamp = self.get_body_argument("timestamp", default=0)
            finished = self.get_body_argument("finished", default=False)
            if finished:
                filename = self.get_body_argument("filename", default=False)
                if not filename:
                    filename = str(timestamp)
                self.condenseAudioUsingFFMPEG(filename, timestamp, config)
                self.removeCondensedAudioInProgressMessage()
                return
            else:
                mp3dir = config.get('condensed-audio-dir', False)
                if not mp3dir:
                    self.alert("You must specify a Condensed Audio Save Location.\n\nYou can do this by:\n1. Navigating to Migaku->Dictionary Settings in Anki's menu bar.\n2. Clicking \"Choose Directory\" for the \"Condensed Audio Save Location\"  in the bottom right of the settings window.")
                    self.removeCondensedAudioInProgressMessage()
                    self.finish("Save location not set.")
                elif self.ffmpegExists():
                    self.handleAudioFileInRequestAndReturnFilename(
                        self.copyFileToCondensedAudioDir, timestamp)
                    print("File saved in temp dir")
                    self.addCondensedAudioInProgressMessage()
                    self.finish("Exporting Condensed Audio")
                else:
                    self.alert("The FFMPEG media encoder must be installed in order to export condensedAudio.\n\nIn order to install FFMPEG please enable MP3 Conversion in the Dictionary Settings window and click \"Apply\".\nFFMPEG will then be downloaded and installed automatically.")
                    self.removeCondensedAudioInProgressMessage()
                    self.finish("FFMPEG not installed.")
                return
        self.finish("Invalid Request")

    def handleAudioFileInRequestAndReturnFilename(self, copyFileFunction, timestamp):
        if "audio" in self.request.files:
            audioFile = self.request.files['audio'][0]
            audioFileName = audioFile["filename"]
            copyFileFunction(audioFile, audioFileName, timestamp)
            return audioFileName
        else:
            return False

    def copyFileToCondensedAudioDir(self, file, filename, timestamp):
        directoryPath = join(self.tempDirectory, timestamp)
        if not exists(directoryPath):
            os.mkdir(directoryPath)
        filePath = join(directoryPath, filename)
        fh = open(filePath, 'wb')
        fh.write(file['body'])
