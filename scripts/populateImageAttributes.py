import photobook.db.Tables as Tables
from sqlalchemy import select
from sqlalchemy import exists

from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np

# import pyheif
from pillow_heif import register_heif_opener
register_heif_opener()


import sys, datetime, logging
import hashlib

from tqdm import tqdm

logger = logging.getLogger("populateImageAttributes")

def parseExifData(exifdata):    
    ed = {}
    for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        try:
            if isinstance(data, bytes):
                data = data.decode()
            ed[tag] = data
        except:
            pass
    return ed


def getImageAttributes(imagePath):

    # https://github.com/carsales/pyheif
    if False: #imagePath.lower().endswith(".heic"):
        heif_file = pyheif.read(imagePath)

        ret = [heif_file.size[0], heif_file.size[1], len(heif_file.mode), None]

        mdTypes = dict((md["type"].lower(),md["data"]) for md in heif_file.metadata)
        if "exif" not in mdTypes:
            logger.info(f"Exif metadata not found for: {imagePath}")
            
        exifData = Image.Exif()
        exifData.load(mdTypes["exif"])

        # im = Image.frombytes(
        #     heif_file.mode,
        #     heif_file.size,
        #     heif_file.data,
        #     "raw",
        #     heif_file.mode,
        #     heif_file.stride)

        # a = np.asarray(im)
    
    else:
        with Image.open(imagePath) as im:      
            ret = [im.size[0], im.size[1], len(im.mode), None]
            exifData = im.getexif()
            # a = np.asarray(im)
    
    exifData = parseExifData(exifData)

    dtTaken = None
    if "DateTime" in exifData:
        dtTaken = datetime.datetime.strptime(exifData["DateTime"], "%Y:%m:%d %H:%M:%S")
    ret.append(dtTaken)

    return ret

    # return (a.shape[1], a.shape[0], a.shape[2], 
    #         hashlib.md5(a.data.tobytes()).hexdigest())


if __name__=="__main__":

    fileHandler = logging.FileHandler("populateImageAttributes.log")
    streamHandler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        handlers = [fileHandler, streamHandler])

    try:
        Tables.Db.initialize(sys.argv[1])
        LIMIT = int(sys.argv[2])

        with Tables.Db.Session() as session:
            q = session.query(Tables.File).filter(
                            ~exists().
                            where(Tables.File.id == Tables.ImageAttributes.file_id)
                            ).all()
            for cnt,fileRow in enumerate(tqdm(q)):
                try:
                    ia = getImageAttributes(fileRow.path)
                    session.add(Tables.ImageAttributes(fileRow, *ia))
                except Exception as e:
                    logging.exception(f"Failed getting image attributes for: {fileRow.path}", e)

                if LIMIT>0 and cnt>=LIMIT: break
                
                if cnt%1000==0:
                    session.commit()

            session.commit()

    except Exception as e:
        logger.critical(e, exc_info=True)
        logger.critical(fileRow.path)
        raise e