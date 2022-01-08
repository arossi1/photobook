import photobook.db.Tables as Tables
from sqlalchemy import select
from sqlalchemy import exists
import sys, os, datetime, logging
import hashlib

if __name__=="__main__":

    fileHandler = logging.FileHandler("populateFileAttributes.log")
    streamHandler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        handlers = [fileHandler, streamHandler])
    logger = logging.getLogger("populateFileAttributes")

    try:
        cnt = 0
        
        Tables.Db.initialize(sys.argv[1])
        LIMIT = int(sys.argv[2])

        with Tables.Db.Session() as session:
            q = session.query(Tables.File).filter(
                            ~exists().
                            where(Tables.File.id == Tables.FileAttributes.file_id)
                            ).all()
            for fileRow in q:
                logger.debug(fileRow.path)
                with open(fileRow.path, "rb") as f:
                    hashval = hashlib.md5(f.read()).hexdigest()
                st = os.stat(fileRow.path)
                dt = datetime.datetime.fromtimestamp(st.st_mtime)
                session.add(
                    Tables.FileAttributes(fileRow, st.st_size, dt, hashval))
                cnt += 1
                
                if cnt%250==0:
                    logger.info("processed {cnt} files")
                    session.commit()

                if LIMIT>0 and cnt>=LIMIT:
                    break

            logger.info("processed {cnt} files")
            session.commit()

    except Exception as e:
        logger.critical(e, exc_info=True)
        raise e