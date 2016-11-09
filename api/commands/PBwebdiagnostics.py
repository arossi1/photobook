from PBcommandbase import PBcommandbase
#from URwebauth import URwebauth

class URwebdiagnostics(PBcommandbase):
    def __init__(self, session):
        self.__session = session

    @staticmethod
    def requiredParameters():
        return ["session"]

    def process(self):
        pass
#        if (not URwebauth.validate(self.__session)): return
            
#        print URwebauth.TEMPLATE() % tuple([self.__session]*4)
