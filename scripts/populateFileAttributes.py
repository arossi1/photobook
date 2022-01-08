import photobook.db.Tables as Tables
from sqlalchemy import select
from sqlalchemy import exists
import sys, os, datetime
import hashlib

if __name__=="__main__":

    cnt = 0
    LIMIT = 5

    Tables.Db.initialize(sys.argv[1])
    with Tables.Db.Session() as session:
        q = session.query(Tables.File).filter(
                          ~exists().
                          where(Tables.File.id == Tables.FileAttributes.file_id)
                          ).all()
        for fileRow in q:
            print(fileRow.path)
            with open(fileRow.path, "rb") as f:
                hashval = hashlib.md5(f.read()).hexdigest()
            st = os.stat(fileRow.path)
            dt = datetime.datetime.fromtimestamp(st.st_mtime)
            session.add(
                Tables.FileAttributes(fileRow, st.st_size, dt, hashval))
            cnt += 1
            if cnt>=LIMIT: break
        print(f"count: {cnt}")
        session.commit()
