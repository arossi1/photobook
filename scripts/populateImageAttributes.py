import photobook.db.Tables as Tables
from sqlalchemy import select
from sqlalchemy import exists
import sys, datetime
import hashlib
from PIL import Image
import numpy as np

from PIL.ExifTags import TAGS

def getExifData(imagePath):
    ed = {}
    with Image.open(imagePath) as im:
        exifdata = im.getexif()
        for tag_id in exifdata:
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            if isinstance(data, bytes):
                data = data.decode()
            ed[tag] = data
    return ed

def getImageAttributes(imagePath):
    with Image.open(imagePath) as im:
        a = np.asarray(im)
        return (im.width, im.height, len(im.getbands()), 
                hashlib.md5(a.data.tobytes()).hexdigest())

if __name__=="__main__":

    cnt = 0
    LIMIT = 10

    Tables.Db.initialize(sys.argv[1])
    with Tables.Db.Session() as session:
        q = session.query(Tables.File).filter(
                          ~exists().
                          where(Tables.File.id == Tables.ImageAttributes.file_id)
                          ).all()
        for fileRow in q:
            print(fileRow.path)

            exifData = getExifData(fileRow.path)
            dtTaken = None
            if "DateTime" in exifData:
                dtTaken = datetime.datetime.strptime(exifData["DateTime"], "%Y:%m:%d %H:%M:%S")

            session.add(
                Tables.ImageAttributes(
                    fileRow,
                    *getImageAttributes(fileRow.path),
                    dtTaken))
            cnt += 1
            if cnt>=LIMIT: break
        print(f"count: {cnt}")
        session.commit()
