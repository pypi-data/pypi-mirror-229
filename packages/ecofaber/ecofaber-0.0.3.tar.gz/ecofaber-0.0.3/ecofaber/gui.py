

import sys
import yaml
import pathlib


from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


import rendering
import utils



class SelectElem(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__("Selection")
        self.parent = parent

        self.elem = None

        self.initUi()

    def initUi(self):
        font = QtGui.QFont("Monospace", 10)

        self.label = QtWidgets.QLabel('None')
        self.label.setFont(font)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.label)

        self.setLayout(vbox)

    def setText(self):
        if self.elem:
            data = self.elem.getData()
            txt = yaml.dump(data, sort_keys=True)
            txt = txt[:-1]
            self.label.setText(txt)
        else:
            self.label.setText('None')

    def setElem(self, elem):
        self.elem = elem

    def update(self):
        self.setText()


class SpeedCtrl(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super().__init__("Speed")
        self.parent = parent

        self.initTimer()
        self.initUi()

    def initTimer(self):
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.parent.update)
        self.timer.start()

    def initUi(self):
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.valueChanged.connect(self.setSpeed)

        self.label = QtWidgets.QLabel('')

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(slider)
        vbox.addWidget(self.label)

        self.setLayout(vbox)

        slider.setValue(10)

    def setSpeed(self, val):
        speed = int(((val)/8)**2)
        self.label.setText(f'{speed}/s')

        if speed == 0:
            self.timer.stop()
        else:
            intervalMs = int(1000/speed)
            self.timer.setInterval(intervalMs)
            self.timer.start()


class ToolBar(QtWidgets.QToolBar):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        self.act = {}

        self.addAct('Load', 'load.png', self.load)
        self.addAct('Save', 'save.png', self.parent.save)
        self.addSeparator()
        self.addAct('View', 'view.png', self.parent.resetView)
        self.addSeparator()
        self.addAct('Reset', 'reset.png', self.parent.reset)
        self.addAct('Next', 'next.png', self.parent.update_)
        self.addAct('Play', 'play.png', self.play)
        self.addSeparator()
        self.addAct('Close', 'close.png', self.parent.closeEvent)

    def getIconPath(self, icon):
        return pathlib.Path(__file__).parent / f"icons/{icon}"

    def setIcon(self, act, icon):
        icon = QtGui.QIcon(str(self.getIconPath(icon)))
        self.act[act].setIcon(icon)

    def addAct(self, name, icon, conn):
        icon = QtGui.QIcon(str(self.getIconPath(icon)))
        act = QtWidgets.QAction(icon, name, self)
        act.triggered.connect(conn)
        self.act[name] = act
        self.addAction(act)

    def load(self):
        self.parent.load()
        if self.parent.model:
            self.act['Save'].setEnabled(True)

    def play(self):
        if self.parent.state == 'pause':
            self.parent.state = 'play'
            self.setIcon('Play', 'pause.png')
        else:
            self.parent.state = 'pause'
            self.setIcon('Play', 'play.png')



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, modelClass, filePath=None):
        super().__init__()

        self.modelClass = modelClass
        self.filePath = filePath
        self.model = modelClass({})
        self.state = 'pause'

        self.resize(800, 500)
        self.setWindowTitle('Ecofaber')

        self.glWidget = rendering.GLWidget(self)
        self.initGUI()
        self.show()

        if self.filePath:
            self.load(self.filePath)

    def initCtrl(self):
        self.speedCtrl = SpeedCtrl(self)
        self.selectElem = SelectElem(self)

        ctrlLayout = QtWidgets.QVBoxLayout()
        ctrlLayout.addWidget(self.speedCtrl)
        ctrlLayout.addWidget(self.selectElem)
        ctrlLayout.addStretch()

        self.ctrlWidget = QtWidgets.QWidget()
        self.ctrlWidget.setLayout(ctrlLayout)

    def initGUI(self):
        self.initCtrl()

        self.toolBar = ToolBar(self)
        self.addToolBar(self.toolBar)

        guiLayout = QtWidgets.QHBoxLayout()
        guiLayout.addWidget(self.glWidget)
        guiLayout.addWidget(self.ctrlWidget)

        guiLayout.setStretch(0, 4)
        guiLayout.setStretch(1, 1)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(guiLayout)
        self.setCentralWidget(centralWidget)

    def resetView(self):
        self.glWidget.resetView()
        self.updateView()

    def reset(self):
        if self.filePath:
            data = utils.loadJson(self.filePath)
        else:
            data = {}
        self.model = self.modelClass(data)
        self.selectElem.setElem(None)
        self.updateView()

    def load(self, filePath=None):
        if filePath == None:
            dFun = QtWidgets.QFileDialog.getOpenFileName
            filePath, _ = dFun(self, 'Open project', '.', 'Json (*.json)')

        if filePath:
            self.filePath = filePath
            self.reset()
            self.resetView()

    def save(self):
        dFun = QtWidgets.QFileDialog.getSaveFileName
        filePath, _ = dFun(self, 'Save project', '.', 'Json (*.json)')

        if filePath:
            if filePath[-5:] != '.json':
                filePath += '.json'
            self.model.save(filePath)

    def updateView(self):
        self.glWidget.updateGL()
        self.selectElem.update()

    def update_(self):
        if self.model:
            self.model.update()
            self.updateView()

    def update(self):
        if self.state == 'play':
            self.update_()

    def closeEvent(self, event):
        sys.exit()

    def setSelectElem(self, elem):
        self.selectElem.setElem(elem)
        self.updateView()




class App(QtWidgets.QApplication):
    def __init__(self, modelClass, modelCfgPath=None):
        super().__init__([])

        self.win = MainWindow(modelClass, modelCfgPath)

        sys.exit(self.exec_())


