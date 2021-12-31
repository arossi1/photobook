import os, sys


if __name__=="__main__":

    import photobook.db.Tables as Tables
    dbPath = sys.argv[1]
    windowsPath = sys.argv[2]
    linuxPath = sys.argv[3]

    if os.path.isfile(dbPath):
        os.remove(dbPath)

    Tables.createDatabase(dbPath)

    with Tables.Db.Session() as session:
        rp = Tables.RootPath(windowsPath, linuxPath)
        session.add(rp)
        session.commit()
