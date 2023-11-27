import photobook.db.Tables as Tables
from photobook.core import Image

# from PIL import Image
# from IPython.display import display

from sqlalchemy import and_, func

from tqdm import tqdm

import shutil
import os

# from PIL import Image
# from pillow_heif import register_heif_opener
# register_heif_opener()



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
        return res

    def queryDateRangeRandomSizeLimit(self, startDate, endDate, desiredSizeBytes):
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
                if sz+x.FileAttributes.size > desiredSizeBytes:
                    break
                sz += x.FileAttributes.size
                res.append(Image.fromDb(x))
        return res

    def queryDateRangeRandom(self, startDate, endDate):
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



def copyImage(imagePath, destDir):
    if imagePath.lower().endswith(".heic"):
        heif_file = Image.open(imagePath)

        heif_file.save(
            os.path.join(
                destDir,
                os.path.splitext(os.path.basename(imagePath))[0] + ".jpg"
            ),
            "JPEG"
        )

    else:
        shutil.copy2(imagePath, destDir)

if __name__=="__main__":
    a = AdamAPI(r"<win db path>")

    KB = 1024
    MB = KB*KB
    GB = MB*KB

    yearStart = 2016
    yearEnd = 2023
    month = 11
    numYears = yearEnd - yearStart
    cardSizeBytes = 1*GB
    szPerYear = cardSizeBytes / numYears
    images = []
    for y in range(yearStart,yearEnd):
        images += a.queryDateRangeRandomSizeLimit(f"{y}-{month}-01", f"{y}-{month}-31", szPerYear)

    breakpoint()
    images[0].getImageData(200, 300, 90)

    # DEST_DIR = r""
    # os.makedirs(DEST_DIR, exist_ok=True)

    # # for imagePath in tqdm(images):
    # #     copyImage(imagePath, DEST_DIR)

    # for imagePath in a.queryDateRangeRandom(f"{yearStart}-{month}-01", f"{yearEnd}-{month}-31"):
    #     print(imagePath)
    #     copyImage(imagePath, DEST_DIR)
