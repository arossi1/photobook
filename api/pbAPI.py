import os
import cgi
import json
import string, decimal, datetime, imp, glob, sys, traceback
import pbdb, Types, Log
        
#################################################################################
class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        elif (isinstance(o, datetime.datetime)):
            return str(o)
        elif (isinstance(o, pbdb.BaseModel)):
            return o.getFieldsDict()
        else:
            return json.JSONEncoder.default(self, o)

class pbResponse:

    def __init__(self, data):
        self.__data = data
        
    def success(self):
        return self.__data["result"]["success"]
        
    def comment(self):
        return self.__data["result"]["comment"]

    def serialize(self):
        pb = {"pb":self.__data}
        return json.dumps(pb, sort_keys=True, indent=2, cls=CustomEncoder)


    
#################################################################################
class PBcommand:

    def __init__(self, form):
        self.__form = form


    @staticmethod
    def __getCommandMap():        
        MODULE_PATH = os.path.split(os.path.abspath(__file__))[0]
        sys.path.append(MODULE_PATH)
        sys.path.append(os.path.join(MODULE_PATH, "commands"))
        sys.path.append(os.path.join(MODULE_PATH, "services"))        
        import PBcommandbase
        cm = {}
        for f in glob.glob(os.path.join(MODULE_PATH, "commands", "*.py")):
            modName = os.path.splitext(os.path.split(f)[1])[0]
            mod = imp.load_source(modName, f)
            for className in dir(mod):
                try:
                    co = getattr(mod, className)
                    if (issubclass(co, PBcommandbase.PBcommandbase) and
                        co!=PBcommandbase.PBcommandbase):
#                        if (cm.has_key(className[2:])):
#                            raise Types.pbException(
#                                "developer error, duplicate command class: " + className[2:])
                        
                        if (not cm.has_key(className[2:])):
                            cm[className[2:]]=co
                        
                except Types.pbException: raise
                except: pass
        return cm

    def process(self):
        try:
            dPB = {}
            dPB["result"] = {"success":True, "comment":""}
            
            if (not self.__form.has_key("command")):
                raise Types.pbException("command not specified")

            # get dynamically discovered command map
            commandMap = PBcommand.__getCommandMap()

            # check for command handler class
            if (not commandMap.has_key(self.__form["command"])):
                raise Types.pbException("unknown command: " + self.__form["command"])

            # validate existance of all required constructor parameters
            missingParamters = []
            constructorParameters = []

            if (commandMap[self.__form["command"]].requiredParameters()):
                for p in commandMap[self.__form["command"]].requiredParameters():
                    if (not self.__form.has_key(p)): missingParamters.append(p)
                    else: constructorParameters.append(self.__form[p])            
                if (len(missingParamters)>0):
                    raise Types.pbException("missing parameters for %s command: %s" % \
                                            (self.__form["command"], string.join(missingParamters, ", ")))

            commandHandler = commandMap[self.__form["command"]](*constructorParameters)
            commandHandler.setFormData(self.__form)

            
            commandParameters = {"commandName":self.__form["command"]}
            if (commandMap[self.__form["command"]].requiredParameters()):
                for p in commandMap[self.__form["command"]].requiredParameters():
                    commandParameters[p] = self.__form[p]
            dPB["command"] = commandParameters               
        
            commandRes = commandHandler.process()
            if (commandRes):
                for k in commandRes.keys():
                    dPB[k] = commandRes[k]
                    
#        except Types.pbException,pbe:
#            dPB["result"]["success"] = False
#            dPB["result"]["comment"] = str(pbe)
        except Exception,e:
            dPB["result"]["success"] = False
            dPB["result"]["comment"] = str(e)
            
        return pbResponse(dPB)


#################################################################################
if __name__=="__main__":

    try:
        form = cgi.FieldStorage()

        d = {}
        for k in form.keys():
            d[k] = form[k].value
            
        if (not d.has_key("command")):
            d["command"] = "webdiagnostics"
        
        
        if (d["command"].startswith("web")):
            print "Content-type: text/html\n"
            cmd = PBcommand(d)
            response = cmd.process()
            if (not response.success()):
                raise Exception(response.comment())
        else:
            cmd = PBcommand(d)
            response = cmd.process()
            print "Content-type: application/json"
            print
            print response.serialize()
            if (not response.success()):
                Log.logError(response.serialize())

        
    except Types.pbException, e:
        print str(traceback.format_exc())
        Log.logError(str(traceback.format_exc()))

    except Exception, e:
        print str(traceback.format_exc())
        Log.logError(str(traceback.format_exc()))



