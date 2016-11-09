import peewee
import sys, inspect
import hashlib, random, datetime

###############################################################################
db = peewee.MySQLDatabase("photobook",
                          host="localhost",
                          port=3306,
                          user="pbuser",
                          passwd="pbpassword")

###############################################################################
def setDB(dbName, host, port, user, passwd):
    db = peewee.MySQLDatabase(dbName,
                              host=host,
                              port=port,
                              user=user,
                              passwd=passwd)

def getTables():
    tables = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if (inspect.isclass(obj) and
            issubclass(obj,peewee.Model) and
            name !="BaseModel"): tables.append(obj)
    return tables

###############################################################################
def tostr(s):
    ret = ""
    for c in s:
        if (ord(c)>127):
            ret += "?"
        else:
            try:    ret += chr(ord(c))
            except: ret += "?"
    return ret
    
def dumpTables():
    f = open("tables.txt","w")
    for table in getTables():
        f.write("*"*79 + "\n")
        f.write(str(table) + "\n")
        for row in table.select():
            f.write("-"*79 + "\n")
            for field in row.getFieldNames():
                f.write(tostr("%s: %s" % (field,getattr(row,field)) + "\n"))
    f.close()

###############################################################################
def dropTables():
    db.execute_sql("SET FOREIGN_KEY_CHECKS=0;")
    print "Dropping tables..."
    for table in getTables():
        if (table.table_exists()):
            print table
            table.drop_table()
        else:
            print "TABLE DOES NOT EXIST (%s)"%table            
    db.execute_sql("SET FOREIGN_KEY_CHECKS=1;")

def createTables():
    db.execute_sql("SET FOREIGN_KEY_CHECKS=0;")
    print "Creating tables..."
    for table in getTables():
        print table
        if (not table.table_exists()):
            table.create_table()
        else:
            print "TABLE EXISTS (%s)"%table            
    db.execute_sql("SET FOREIGN_KEY_CHECKS=1;")

def populateEnums():
    print "Populating enumerations..."

def cleanTables():
    dropTables()
    print
    createTables()
    print
    populateEnums()

###############################################################################
class BaseModel(peewee.Model):
    class Meta: database = db

    def addOmitFields(self, omitFields):
        if (not self.__dict__.has_key("omitFields")):
            self.__dict__["omitFields"] = []
        if (isinstance(omitFields, str)):
            self.__dict__["omitFields"].append(omitFields)
        else:
            self.__dict__["omitFields"] += omitFields

    def getFieldNames(self):
        if (not self.__dict__.has_key("omitFields")):
            self.__dict__["omitFields"] = []
        fns = self._meta.get_field_names()
        for ofn in self.__dict__["omitFields"]:
            if (ofn in fns): fns.remove(ofn)            
        return fns

    def getFieldsDict(self):
        vals = {}
        for field in self.getFieldNames():
            vals[field] = getattr(self,field)
        return vals
    
    @classmethod
    def getAll(cls):
        return cls.select()
    
    @classmethod
    def getId(cls, id):
        res = cls.select().where(cls.id==id)
        if (res.exists()): return res[0]
        else: raise Exception("Cannot find %s (id=%s)"%(cls,id))

#################################################################################
class SystemParameters(BaseModel):
    
    id = peewee.PrimaryKeyField()
    key = peewee.CharField()
    value = peewee.CharField()

    @staticmethod
    def existsKey(key):
        return (SystemParameters.select().where(SystemParameters.key==key).exists())
    
    @staticmethod
    def getKey(key):
        res = SystemParameters.select().where(SystemParameters.key==key)
        if (res.exists()): return res[0]
        else: raise Exception("Cannot find SystemParameters (key=%s)"%key)

    @staticmethod
    def getInteger(key): return int(SystemParameters.getKey(key).value)
    @staticmethod
    def getFloat(key): return float(SystemParameters.getKey(key).value)
    @staticmethod
    def getString(key): return SystemParameters.getKey(key).value
        
        
###############################################################################
class Catalog(BaseModel):
    
    id = peewee.PrimaryKeyField()
    name = peewee.TextField(null=True, default=None)
    description = peewee.TextField(null=True, default=None)
    path = peewee.TextField(null=True, default=None)
            
    @staticmethod
    def new(name, description, path):
        c = Catalog.create(name=name,
                           description=description,
                           path=path)
        c.save()
        return c

    def newPhoto(self, path, hashval):
        return Photo.new(self, path, hashval)
    

###############################################################################
class Photo(BaseModel):
    
    id = peewee.PrimaryKeyField()
    catalog = peewee.ForeignKeyField(Catalog, related_name="catalog", null=True)
    path = peewee.TextField(null=True, default=None)
    hashval = peewee.TextField(null=True, default=None)
    exists = peewee.BooleanField(default=True)
            
    @staticmethod
    def new(catalog, path, hashval):
        c = Photo.create(catalog=catalog,
                         path=path,
                         hashval=hashval)
        c.save()
        return c

###############################################################################
#class Message(BaseModel):
#    
#    id = peewee.PrimaryKeyField()
#    phone1 = peewee.ForeignKeyField(PhoneNumbers, related_name="phone1", null=True)
#    phone2 = peewee.ForeignKeyField(PhoneNumbers, related_name="phone2", null=True)
#    datetime = peewee.DateTimeField(null=True, default=None)
#    body = peewee.TextField(null=True, default=None)
#        
#    @staticmethod
#    def getAll():
#        return Message.select()
#        
#    @staticmethod
#    def new(phone1, phone2, datetime, body):
#        msg = Message.create(phone1=phone1,
#                             phone2=phone2,
#                             datetime=datetime,
#                             body=body)
#        msg.save()
#        return msg
#    
#    @staticmethod
#    def exists(phone1, phone2, body):
#        return Message.select().where( (Message.phone1==phone1) & \
#                                       (Message.phone2==phone2) & \
#                                       (Message.body==body) ).exists()
#                                       
#    @staticmethod
#    def getRange(phone1, phone2, dtStart, dtEnd):
#        if (phone1!=None and phone2!=None):
#            return Message.select().where( ((Message.phone1==phone1) | (Message.phone2==phone1)) & \
#                                           ((Message.phone1==phone2) | (Message.phone2==phone2)) & \
#                                           ((Message.datetime >= dtStart) & (Message.datetime <= dtEnd)) ).order_by(Message.datetime)
#        elif (phone1!=None or phone2!=None):
#            pn = None
#            if (phone1!=None): pn = phone1
#            if (phone2!=None): pn = phone2
#            return Message.select().where( ((Message.phone1==pn) | (Message.phone2==pn)) & \
#                                           ((Message.datetime >= dtStart) & (Message.datetime <= dtEnd)) ).order_by(Message.datetime)
#        else:
#            return Message.select().where( ((Message.datetime >= dtStart) & (Message.datetime <= dtEnd)) ).order_by(Message.datetime)
#                                       
#    def isSame(self, msg):
#        return (self.phone1==msg.phone1 and 
#                self.phone2==msg.phone2 and 
#                self.body==msg.body)
#    
#    def __str__(self):
#        return "[%s] %s -> %s | %s"%(self.datetime, self.phone1, self.phone2, self.body)
#        
#
#
##################################################################################
#class Call(BaseModel):
#    
#    id = peewee.PrimaryKeyField()
#    phonenum = peewee.ForeignKeyField(PhoneNumbers, related_name="phonenum", null=True)
#    datetime = peewee.DateTimeField(null=True, default=None)
#        
#    @staticmethod
#    def getAll():
#        return Call.select()
#        
#    @staticmethod
#    def new(phone, datetime):
#        call = Call.create(phonenum=phone, datetime=datetime)
#        call.save()
#        return call
#    
#    @staticmethod
#    def exists(callid):
#        return Call.select().where(Call.id==callid).exists()
#        
#    @staticmethod
#    def getId(callid):
#        res = Call.select().where(Call.id==callid)
#        if (res.exists()): return res[0]
#        else: raise Exception("Cannot find Call (id=%s)"%callid)
#    
#    @staticmethod
#    def getRange(phone, dtStart, dtEnd):
#        if (phone!=None):
#            return Call.select().where( (Call.phonenum==phone) & \
#                                       ((Call.datetime >= dtStart) & (Call.datetime <= dtEnd)) ).order_by(Call.datetime)
#        else:
#            return Call.select().where( ((Call.datetime >= dtStart) & (Call.datetime <= dtEnd)) ).order_by(Call.datetime)
#                  
#    def getVoiceData(self):
#        return VoiceData.select().where(VoiceData.call==self.id).order_by(VoiceData.starttime)
#        
#    def getVoiceIntensityData(self):
#        return VoiceIntensityData.select().where(VoiceIntensityData.fcall==self.id).order_by(VoiceIntensityData.starttime)        
#                                       
#    def __str__(self):
#        return "[%s] %s"%(self.datetime, self.phonenum)
#        
#
##################################################################################
#class VoiceData(BaseModel):
#    
#    id = peewee.PrimaryKeyField()
#    call = peewee.ForeignKeyField(Call, related_name="call", null=True)
#    starttime = peewee.IntegerField()
#    vocaltiming = peewee.IntegerField()
#    
#    @staticmethod
#    def new(call, starttime, vocaltiming):
#        vd = VoiceData.create(call=call,
#                              starttime=starttime,
#                              vocaltiming=vocaltiming)
#        vd.save()
#        return vd
#
#  
##################################################################################
#class VoiceIntensityData(BaseModel):
#    
#    id = peewee.PrimaryKeyField()
#    fcall = peewee.ForeignKeyField(Call, related_name="fcall", null=True)
#    starttime = peewee.IntegerField()
#    intensity = peewee.IntegerField()
#    
#    @staticmethod
#    def new(call, starttime, intensity):
#        vid = VoiceIntensityData.create(fcall=call,
#                                        starttime=starttime,
#                                        intensity=intensity)
#        vid.save()
#        return vid
#        


###############################################################################
class Session(BaseModel):
    
    id = peewee.PrimaryKeyField()
    key = peewee.CharField()
    timestamp = peewee.DateTimeField()
    ipaddy = peewee.CharField(null=True)
    

    @staticmethod
    def getKey(key):
        res = Session.select().where(Session.key==key)
        if (res.exists()): return res[0]
        else: raise Exception("Cannot find Session (key=%s)"%key)

    @staticmethod
    def existsKey(key):
        return (Session.select().where(Session.key==key).exists())

    @staticmethod
    def new(key):
        m = hashlib.md5(key)
        while (True):
            m.update(str(random.random()))
            if (not Session.existsKey(m.hexdigest())):
                break
        return Session.create(key=m.hexdigest(),
                              timestamp=datetime.datetime.now())
    
    @staticmethod
    def getUser(key):
        s = Session.getKey(key)
        res = User.select().where(User.session==s.id)
        if (res.exists()): return res[0]
        raise Exception("Cannot find user for session (key=%s)"%key)         

    def updateTime(self):
        self.timestamp = datetime.datetime.now()
        self.save()
        
    def updateAddy(self, addy):
        self.ipaddy = addy
        self.save()

    def expire(self):
        self.timestamp = datetime.datetime(1900,1,1)
        self.save()

    def isActive(self):
        diff = datetime.datetime.now() - self.timestamp
        return (diff < datetime.timedelta(seconds=SystemParameters.getInteger("sessiontimeoutseconds")))

    def getFieldsDict(self):
        vals = BaseModel.getFieldsDict(self)
        vals["active"] = self.isActive()
        return vals        
        
        
###############################################################################
class User(BaseModel):
    
    id = peewee.PrimaryKeyField()
    email = peewee.CharField()
    password = peewee.CharField()
    firstname = peewee.CharField()
    lastname = peewee.CharField()
    session = peewee.ForeignKeyField(Session, related_name="usersession", null=True)

    @staticmethod
    def getEmail(email):
        res = User.select().where(User.email==email)
        if (res.exists()): return res[0]
        else: raise Exception("Cannot find User (email=%s)"%email)

    @staticmethod
    def existsEmail(email):
        return ((User.select().where(User.email==email)).exists())
    
    
###############################################################################    
if __name__=="__main__":

    if ("-dump" in sys.argv):
        dumpTables()

