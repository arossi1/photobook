# -*- coding: utf-8 -*-

import os
import hashlib
import logging

import sqlalchemy





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

    # if True:
    #     Session = sessionmaker(engine)
    #     with Session() as session:

    #         p1 = Path(r"\\zeus\pictures", "/raid/pictures")
    #         session.add(p1)
    #         session.commit()

    # Session = sessionmaker(engine)
    # with Session() as session:
    #     for x in session.query(Path).all():
    #         print(x)


import random
while True:

    o1 = random.randint(0,100)
    o2 = random.randint(0,100)
    op = random.choice(("+", "-"))
    q = f"{o1} {op} {o2}"
    ans = eval(q)

    sol = int(input(f"what is {q} = "))

    if sol == ans:
        print("You are correct!\n")
    else:
        print(f"Incorrect!  {q} = {ans}\n")
    


    # with open(p,"rb") as f:
    #     hashval = hashlib.md5(f.read()).hexdigest()
    # print(f"{fn}: {hashval}")
    # #cat.newPhoto(os.path.relpath(p, ROOT), hashval)

