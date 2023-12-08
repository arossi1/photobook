import photobook.db.Tables as Tables
from photobook.core import Image

# from PIL import Image
# from IPython.display import display

from sqlalchemy import and_, func

from tqdm import tqdm

import shutil
import os
import sys
import datetime

from PIL import Image as PILImage
from pillow_heif import register_heif_opener
register_heif_opener()



class AdamAPI:
    def __init__(self, dbPath:str):
        Tables.Db.initialize(dbPath)

    def queryDateRange(self, startDate, endDate):
        res = []
        with Tables.Db.Session() as s:
            for x in s.query(
                Tables.FileAttributes,
                Tables.ImageAttributes).join(
                    Tables.ImageAttributes,
                    Tables.ImageAttributes.file_id == Tables.FileAttributes.file_id
                ).filter(
                    and_(
                        func.date(Tables.ImageAttributes.date_time) >= startDate,
                        func.date(Tables.ImageAttributes.date_time) <= endDate,
                )
            ):
                res.append(Image.fromDb(x))
        return res
    
    def queryMultipleDateRangeSameMonth(self, yearStart, yearEnd, month):
        res = []
        for d in range(yearStart,yearEnd+1):
            res += self.queryDateRange(
                f"{d}-{month}-01",
                f"{d}-{month}-31"
            )
        return 
    
    @staticmethod
    def inTimeWindow(timestamps, newTimestamp, minuteWindow):
        minWin = datetime.timedelta(minutes=minuteWindow)
        return any(
            (ts - minWin) < newTimestamp < (ts + minWin)
            for ts in timestamps
        )

    def queryDateRangeRandomSizeLimit(
        self,
        startDate, 
        endDate, 
        desiredSizeBytes,
        timestamps=None,
        minuteWindow=5):

        if timestamps is None:
            timestamps = []
        res = []
        sz = 0
        with Tables.Db.Session() as s:
            for x in s.query(
                    Tables.FileAttributes,
                    Tables.ImageAttributes
                ).join(
                    Tables.ImageAttributes,
                    Tables.ImageAttributes.file_id == Tables.FileAttributes.file_id
                ).filter(
                    and_(
                        func.date(Tables.ImageAttributes.date_time) >= startDate,
                        func.date(Tables.ImageAttributes.date_time) <= endDate,
                    )
                ).order_by(
                    func.random()
            ):
            # for x in s.query(
            #     Tables.FileAttributes
            #     ).join(
            #         Tables.ImageAttributes,
            #         Tables.ImageAttributes.file_id == Tables.FileAttributes.file_id
            #     ).filter(
            #         func.date(Tables.FileAttributes.modified_date_time) >= startDate
            #     ):
                image = Image.fromDb(x)

                if not AdamAPI.inTimeWindow(timestamps, image.date_time, 5):
                    timestamps.append(image.date_time)
                    if sz+x.FileAttributes.size > desiredSizeBytes:
                        break
                    sz += x.FileAttributes.size
                    res.append(image)
        return res

    def queryDateRangeRandom(
        self,
        startDate,
        endDate,
        timestamps=None,
        minuteWindow=5):
        
        with Tables.Db.Session() as s:
            for x in s.query(
                    Tables.FileAttributes,
                    Tables.ImageAttributes
                ).join(
                    Tables.ImageAttributes,
                    Tables.ImageAttributes.file_id == Tables.FileAttributes.file_id
                ).filter(
                    and_(
                        func.date(Tables.ImageAttributes.date_time) >= startDate,
                        func.date(Tables.ImageAttributes.date_time) <= endDate,
                    )
                ).order_by(
                    func.random()
            ):
                yield Image.fromDb(x)



def copyImage(im : Image, destDir : str):
    if im.path.lower().endswith(".heic"):
        heif_file = PILImage.open(im.path)

        heif_file.save(
            os.path.join(
                destDir,
                os.path.splitext(os.path.basename(im.path))[0] + ".jpg"
            ),
            "JPEG"
        )

    else:
        shutil.copy2(im.path, destDir)

if __name__=="__main__":
    a = AdamAPI(sys.argv[1])
    DEST_DIR = sys.argv[2]
    dryRun = False

    KB = 1024
    MB = KB*KB
    GB = MB*KB

    yearStart = 2016
    yearEnd = 2023
    month = 12
    WINDOW_MIN = 5

    if not dryRun:
        if os.path.exists(DEST_DIR):
            print(f"Deleting existing images: {DEST_DIR}")
            shutil.rmtree(DEST_DIR)
        os.makedirs(DEST_DIR)

    print("Copying images...")
    numYears = yearEnd - yearStart
    cardSizeBytes = 1*GB
    szPerYear = cardSizeBytes / numYears
    images = []
    timestamps = []
    for y in range(yearStart,yearEnd):
        images += a.queryDateRangeRandomSizeLimit(
            f"{y}-{month}-01", f"{y}-{month}-31", szPerYear, timestamps, WINDOW_MIN)

    for image in tqdm(images):
        if dryRun:
            print(image.path)
        else:
            copyImage(image, DEST_DIR)

    for image in a.queryDateRangeRandom(
        f"{yearEnd}-{month}-01", f"{yearEnd}-{month}-31", timestamps, WINDOW_MIN):
        print(image.path)
        if not dryRun:
            copyImage(image, DEST_DIR)
