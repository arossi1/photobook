import photobook.db.Tables as Tables
from sqlalchemy import select
import sys, os
import logging

if __name__=="__main__":

    fileHandler = logging.FileHandler("populateImages.log")
    streamHandler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        handlers = [fileHandler]) #, streamHandler])
    logger = logging.getLogger("populateImages")

    def shouldBreak(cnt, limit):
        if limit<1: return False
        return cnt>limit

    try:
        Tables.Db.initialize(sys.argv[1])
        ROOT = sys.argv[2]
        LIMIT = int(sys.argv[3])
        checkExist = int(sys.argv[4]) == 1

        EXTENSIONS = (".jpg", ".jpeg", ".tif", ".tiff", ".png", ".heic")
        cnt = 0

        for dirpath,dirnames,filenames in os.walk(ROOT):
            logger.info(f"processing directory: {dirpath}")
            dircnt = 0
            with Tables.Db.Session() as session:
                for fn in filenames:
                    if os.path.splitext(fn)[1].lower() in EXTENSIONS:
                        p = os.path.join(dirpath, fn)

                        addP = True
                        if checkExist:
                            # x = select(Tables.File.__table__).where(Tables.File.path == p).one()
                            x = session.execute(
                                select(Tables.File.id).
                                where(Tables.File.path==p)
                                ).all()

                            if len(x)>0:
                                addP = False
                                logger.info(f"already in db: {p}")

                        if addP:
                            f = Tables.File(p)
                            session.add(f)
                            cnt += 1
                            dircnt += 1

                        if shouldBreak(cnt, LIMIT): break
                    if shouldBreak(cnt, LIMIT): break
                session.commit()
                if shouldBreak(cnt, LIMIT): break
            logger.info(f"processed {dircnt} images in {dirpath} | {cnt} total")

    except Exception as e:
        logger.critical(e, exc_info=True)
        raise e
