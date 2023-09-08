

import json


def loadJson(fileName):
    with open(fileName) as f:
        return json.loads(f.read())


def saveJson(data, fileName):
    with open(fileName, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)
