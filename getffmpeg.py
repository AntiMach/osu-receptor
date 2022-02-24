import io
import sys
import tarfile
import zipfile
import requests
import subprocess
import traceback
from abc import ABC, abstractmethod


class Archive(ABC):
    @abstractmethod
    def __init__(self, data: io.BytesIO) -> None:
        return NotImplemented

    @abstractmethod
    def list(self) -> list:
        return NotImplemented

    @abstractmethod
    def get_filename(self, info):
        return NotImplemented

    @abstractmethod
    def set_filename(self, info, new):
        return NotImplemented

    @abstractmethod
    def extract(self, info):
        return NotImplemented


class ZipArchive(Archive):
    def __init__(self, data) -> None:
        self.archive = zipfile.ZipFile(data, "r")

    def list(self):
        return self.archive.infolist()

    def get_filename(self, info: zipfile.ZipInfo):
        return info.filename

    def set_filename(self, info: zipfile.ZipInfo, new: str):
        info.filename = new

    def extract(self, info: zipfile.ZipInfo):
        self.archive.extract(info, ".")


class TarArchive(Archive):
    def __init__(self, data) -> None:
        self.archive = tarfile.open(fileobj=data, mode="r")

    def list(self):
        return self.archive.getmembers()

    def get_filename(self, info: tarfile.TarInfo):
        return info.name

    def set_filename(self, info: tarfile.TarInfo, new: str):
        info.name = new

    def extract(self, info: tarfile.TarInfo):
        self.archive.extract(info, ".")


class Platform:
    FFMPEG = "ffmpeg"

    FFMPEG_SRC = NotImplemented
    FFMPEG_FILES = NotImplemented

    ARCHIVE_CLS = Archive

    @classmethod
    def download(cls, url, name) -> io.BytesIO:
        res = requests.get(url, stream=True)
        
        max_size = int(res.headers.get("Content-Length", -1))
        read_size = 0
        data = io.BytesIO()

        for chunk in res.iter_content(1024*1024):
            read_size += len(chunk)
            data.write(chunk)

            if max_size > 0:
                prog = f"{int(read_size/max_size*100)}%"
            else:
                prog = f"{int(read_size)} bytes"

            sys.stdout.write(f"\rDownloading {name}... {prog}")

        sys.stdout.write("\n")

        data.seek(0, io.SEEK_SET)
        return data

    @classmethod
    def get_ffmpeg(cls):
        data = cls.download(cls.FFMPEG_SRC, cls.FFMPEG)

        print(f"Extracting {cls.FFMPEG}...")

        archive = cls.ARCHIVE_CLS(data)

        for info in archive.list():
            *_, name = archive.get_filename(info).split("/")

            if name not in cls.FFMPEG_FILES:
                continue
            
            archive.set_filename(info, name)
            archive.extract(info)

    @classmethod
    def install(cls, force = False):
        try:
            if force: raise FileNotFoundError()

            subprocess.run([cls.FFMPEG, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            cls.get_ffmpeg()


class Windows(Platform):
    FFMPEG_SRC = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    FFMPEG_FILES = "ffmpeg.exe",

    ARCHIVE_CLS = ZipArchive


class Linux(Platform):
    FFMPEG_SRC = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
    FFMPEG_FILES = "ffmpeg",

    ARCHIVE_CLS = TarArchive


def main():
    if sys.platform in ["win32", "cygwin"]:
        Windows.install(False)
    elif sys.platform in ["linux"]:
        Linux.install(False)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        input("Press enter to exit")