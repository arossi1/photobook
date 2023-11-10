import photobook.db.Tables as Tables
from .Image import Image
import datetime

from sqlalchemy import func

class Images:
    
    @staticmethod
    def getRandom():

        with Tables.Db.Session() as session:

            # f = session.query(Tables.File).join(Tables.FileAttributes).filter(
            #     Tables.FileAttributes.modified_date_time.between(
            #         datetime.datetime(2021, 1, 1),
            #         datetime.datetime(2022, 12, 5)))

            # f = session.query(Tables.File).join(Tables.FileAttributes).filter(
            #     Tables.File.path.contains(".heic"))

            # f = session.query(Tables.File).\
            #     filter(Tables.FileAttributes.modified_date_time >= datetime.date(2020, 1, 1)).\
            #     filter(Tables.FileAttributes.modified_date_time <= datetime.date(2021, 1, 1))


            f = session.query(Tables.File).join(Tables.FileAttributes, Tables.ImageAttributes).filter(
                Tables.ImageAttributes.date_time.between(
                    datetime.datetime(2022, 1, 1),
                    datetime.datetime(2022, 12, 5)))           


            # import pdb; pdb.set_trace()
            print(f"Results: {f.count()}\n")
            for x in f.limit(5): #slice(1,10):
                print(x.path)
                print(x.image_attributes)
                print()

            # q = session.query(Tables.File).filter(
            #     Tables.FileAttributes.modified_date_time.between(
            #         datetime.date(2020, 1, 1),
            #         datetime.date(2021, 1, 1))).all()

            # for fileRow in q:
            #     print(fileRow)