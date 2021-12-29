import os


if __name__=="__main__":

    import photobook.db.Tables
    dbPath = r"C:\Users\Adam Rossi\source\photobook\testdb.db"
    if os.path.isfile(dbPath):
        os.remove(dbPath)    
    photobook.db.Tables.createDatabase(dbPath)
