from .RootPath import rootPaths
from PIL import Image as PilImage
from pillow_heif import register_heif_opener
register_heif_opener()

import platform


ROTATE_MAP = {
    90 : PilImage.Transpose.ROTATE_270,
    180 : PilImage.Transpose.ROTATE_180,
    270 : PilImage.Transpose.ROTATE_90,
}


class Image:

    def __init__(
        self,
        path,
        size,
        modified_date_time,
        width,
        height,
        bands,
        date_time):

        self.__path = path
        self.size = size
        self.modified_date_time = modified_date_time
        self.width = width
        self.height = height
        self.bands = bands
        self.date_time = date_time

    def __repr__(self):
        return \
        f"path: {self.path}\n"
        f"size: {self.size}\n"
        f"modified_date_time: {self.modified_date_time}\n"
        f"width: {self.width}\n"
        f"height: {self.height}\n"
        f"bands: {self.bands}\n"
        f"date_time: {self.date_time}\n"

    @staticmethod
    def fromDb(im):
        return Image(
            im.FileAttributes.file.path,
            im.FileAttributes.size,
            im.FileAttributes.modified_date_time,
            im.ImageAttributes.width,
            im.ImageAttributes.height,
            im.ImageAttributes.bands,
            im.ImageAttributes.date_time
        )

    @property
    def path(self):
        if platform.system()=="Windows":
            return self.__path.replace(rootPaths.linux, rootPaths.windows).replace("/", "\\")
        else:
            return self.__path

    def getImageData(self, width=None, height=None, rotate=None):
        im = PilImage.open(self.path)

        if rotate is not None and rotate != 0:
            if rotate not in ROTATE_MAP:
                raise Exception(f"Unsupported rotation: {rotate}")

            im = im.transpose(ROTATE_MAP[rotate])

        dsWidth = dsHeight = None
        if width is not None:
            dsWidth = im.size[0] / width
        else:
            dsHeight = 1
            width = self.width

        if height is not None:
            dsHeight = im.size[1] / height
        else:
            dsHeight = 1
            height = self.height
        
        ds = max(dsHeight, dsWidth)
        if ds!=1:
            im = im.resize(
                (
                    int(im.size[0]//ds),
                    int(im.size[1]//ds)
                ),
                PilImage.Resampling.LANCZOS
            )

        return im


