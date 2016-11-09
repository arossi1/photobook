import pbdb
import hashlib


def createSystemParameters():
    # session timeout = 15min
    pbdb.SystemParameters.create(key="sessiontimeoutseconds",
                                 value=str(60*15))


def createUsers():
    pbdb.User.create(email="arossi1@gmail.com",
                     password=hashlib.md5("uor60^)").hexdigest(),
                     firstname="Adam", lastname="Rossi")


def initDB():
    pbdb.cleanTables()

if __name__=="__main__":
    initDB()
    print "Creating system parameters"; createSystemParameters()
    print "Creating users"; createUsers()

