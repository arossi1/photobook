# -*- coding: utf-8 -*-

import os
import hashlib
import logging

import sqlalchemy



from sqlalchemy.orm import sessionmaker

# from base import Session #, Base


# Model = declarative_base(name='Model')
# Model.query = db_session.query_property()



FORMAT = '[%(asctime)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
# log = logging.getLogger("test")


#Tables:
# path: windows, linux
# image: id, rel_path, size 
# image_metadata: full_hash, image_hash
#

#Agents (populate db tables):
# primary: populates image table by simply scanning filesystem, uses paths in Path table
# times: file time, image metadata timestamp
# hashes: file, image_only
# modify detection: file moved, deleted, modified, etc - need to update tables
#                   can probably just check that files in table exist, if not, just delete row and any links
# people id: use machine learning to find faces, identify, populate table of people to image
#

#Apps (end user CLI apps, GUIs, scripts, webapps):
# duplicates: based on hash, time, size, etc.
# searching: variety of criteria: name, dates, other metadata
#




if __name__=="__main__":   

    if True:
        Session = sessionmaker(engine)
        with Session() as session:

            p1 = Path(r"\\zeus\pictures", "/raid/pictures")
            session.add(p1)
            session.commit()

    Session = sessionmaker(engine)
    with Session() as session:
        for x in session.query(Path).all():
            print(x)

    

    ROOT = r"\\zeus\pictures\Jamie's Photos\iPhone\Pics Backup 2015.07.21\DCIM"
    EXTENSIONS = (".jpg", ".jpeg", ".tif")
    cnt = 0
    for dirpath,dirnames,filenames in os.walk(ROOT):    
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in EXTENSIONS:
                p = os.path.join(dirpath, fn)
                Image.add(p)
                cnt +=1

                if cnt>10: break
            if cnt>10: break
        if cnt>10: break


    # with open(p,"rb") as f:
    #     hashval = hashlib.md5(f.read()).hexdigest()
    # print(f"{fn}: {hashval}")
    # #cat.newPhoto(os.path.relpath(p, ROOT), hashval)

