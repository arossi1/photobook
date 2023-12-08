import photobook.db.Tables as Tables

class Paths:
    def __init__(self):
        self.__windowsRootPath = None
        self.__linuxRootPath = None
        self.__populated = False

    def __populate(self):
        if not self.__populated:
            self.__populated = True
            with Tables.Db.Session() as s:
                x = s.query(Tables.RootPath)[0]
                self.__windowsRootPath = x.windows
                self.__linuxRootPath = x.linux

    @property
    def windows(self):
        self.__populate()
        return self.__windowsRootPath

    @property
    def linux(self):
        self.__populate()
        return self.__linuxRootPath

rootPaths = Paths()
