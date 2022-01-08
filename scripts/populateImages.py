import photobook.db.Tables as Tables
from sqlalchemy import select
import sys, os
import logging

if __name__=="__main__":

    Tables.Db.initialize(sys.argv[1])
    ROOT = sys.argv[2]
    EXTENSIONS = (".jpg", ".jpeg", ".tif", ".tiff", ".png")
    cnt = 0
    LIMIT = 500

    for dirpath,dirnames,filenames in os.walk(ROOT):
        print(dirpath)
        with Tables.Db.Session() as session:
            for fn in filenames:
                if os.path.splitext(fn)[1].lower() in EXTENSIONS:
                    p = os.path.join(dirpath, fn)
                    # import pdb; pdb.set_trace()

                    # x = select(Tables.File.__table__).where(Tables.File.path == p).one()
                    x = session.execute(
                        select(Tables.File.id).
                        where(Tables.File.path==p)
                        ).all()

                    if len(x)<=0:
                        f = Tables.File(p)
                        session.add(f)
                        cnt += 1
                    # else:
                    #     print(f"already in db: {p}")
                    if cnt>LIMIT: break
                if cnt>LIMIT: break
            print(f"count: {cnt}")
            session.commit()
            if cnt>LIMIT: break
        print(f"count: {cnt}")
    print(f"count: {cnt}")
