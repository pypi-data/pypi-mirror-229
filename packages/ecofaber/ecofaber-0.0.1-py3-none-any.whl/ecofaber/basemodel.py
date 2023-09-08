


import utils



# ---------- Register Model Classes

modelElements = {}

def register(c):
    modelElements[c.__name__] = c
    return c





# ---------- Model Element

class ModelElement:
    def __init__(self, data):
        self._obj = self.__class__.__name__
        if data:
            self.loadData(data)
        else:
            self.loadRandom()

    def loadData(self, data):
        for prop in data.keys():
            setattr(self, prop, makeObjStruct(data[prop]))

    def loadRandom(self):
        pass

    def getData(self):
        return makeDataStruct(self.__dict__)

    def save(self, filePath):
        utils.saveJson(self.getData(), filePath)




def makeObject(data):
    objName = data['_obj']
    objClass = modelElements[objName]
    return objClass(data)


def makeObjStruct(d):
    if type(d) == dict:
        if '_obj' in d.keys():
            return makeObject(d)
        else:
            return {key:makeObjStruct(d[key]) for key in d}
    elif type(d) == list:
        return [makeObjStruct(elem) for elem in d]
    else:
        return d


def makeDataStruct(d):
    if isinstance(d, ModelElement):
        return d.getData()
    elif type(d) == dict:
        return {key:makeDataStruct(d[key]) for key in d}
    elif type(d) == list:
        return [makeDataStruct(elem) for elem in d]
    else:
        return d


