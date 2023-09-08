


import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))




import gui



def launch(modelClass, modelCfgPath=None):
    gui.App(modelClass, modelCfgPath)