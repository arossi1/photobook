# -*- coding: utf-8 -*-
"""
Created on Wed Nov 09 15:46:18 2016

@author: Adam Rossi
"""

import db
import os
import hashlib


ROOT = r"P:\Jamie's Photos\iPhone\Pics Backup 2015.07.21\DCIM"
EXTENSIONS = (".jpg", ".jpeg", ".tif")


cat = db.pbdb.Catalog.new("Test Catalog", "testing 123", ROOT)

for dirpath,dirnames,filenames in os.walk(ROOT):    
    for fn in filenames:
        if (os.path.splitext(fn)[1].lower() in EXTENSIONS):
            print fn
            p = os.path.join(dirpath, fn)
            
            with open(p,"rb") as f:
                hashval = hashlib.md5(f.read()).hexdigest()
            
            cat.newPhoto(os.path.relpath(p, ROOT), hashval)
