import sys

from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, 
    QGridLayout, QWidget, QListWidget, QListWidgetItem,
    QDockWidget, QFormLayout, QLineEdit, QPushButton,
    QTextEdit, QHBoxLayout, QFileDialog
)

from PyQt5.QtGui import QPixmap

from photobook.test.fillCard import AdamAPI

# from PIL import ImageQt
from PIL import Image as PilImage

import math
import os
from contextlib import contextmanager

################################################################################
@contextmanager
def waitCursorContext():
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        yield
    except:
        raise
    finally:
        QApplication.restoreOverrideCursor()

################################################################################
def pil2pixmap(im):

    if im.mode == "RGB":
        r, g, b = im.split()
        im = PilImage.merge("RGB", (b, g, r))
    elif  im.mode == "RGBA":
        r, g, b, a = im.split()
        im = PilImage.merge("RGBA", (b, g, r, a))
    elif im.mode == "L":
        im = im.convert("RGBA")
    im2 = im.convert("RGBA")
    data = im2.tobytes("raw", "RGBA")
    qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_ARGB32)
    pixmap = QtGui.QPixmap.fromImage(qim)
    return pixmap

################################################################################
class ImageReviewGui(QMainWindow):

    def __init__(self, dbPath):
        super().__init__()
        self.setWindowTitle("Image Review")
        self.resize(800,600)

        self.docked = QDockWidget("Query Form", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docked)
        self.dockedWidget = QWidget(self)
        self.docked.setWidget(self.dockedWidget)
        formLayout = QFormLayout()
        self.dockedWidget.setLayout(formLayout)
        
        self.startDate = QLineEdit("2020-07-01")
        self.endDate = QLineEdit("2020-08-01")
        self.pbQuery = QPushButton("Query")
        self.pbQuery.clicked.connect(self.querySlot)
        self.listWidget = QListWidget()
        self.listWidget.currentItemChanged.connect(self.listItemChangedSlot)

        self.pbRotateRight = QPushButton("Rotate +90")
        self.pbRotateRight.clicked.connect(self.rotateRightSlot)

        self.pbRotate180 = QPushButton("Rotate 180")
        self.pbRotate180.clicked.connect(self.flipSlot)

        self.pbRotateLeft = QPushButton("Rotate -90")
        self.pbRotateLeft.clicked.connect(self.rotateLeftSlot)
        layRotate = QHBoxLayout()
        layRotate.addWidget(self.pbRotateLeft)
        layRotate.addWidget(self.pbRotate180)
        layRotate.addWidget(self.pbRotateRight)
        self.rotateSetting = 0

        self.saveDir = QLineEdit("")
        self.pbSaveSelected = QPushButton("Save Selected")
        self.pbSaveSelected.clicked.connect(self.saveSelectedSlot)

        self.pbSaveBrowse = QPushButton("Browse...")
        self.pbSaveBrowse.clicked.connect(self.saveBrowseSlot)

        formLayout.addRow("Start Date:", self.startDate)
        formLayout.addRow("End Date:", self.endDate)
        formLayout.addRow(self.pbQuery)
        formLayout.addRow(layRotate)
        formLayout.addRow("Directory:", self.saveDir)
        formLayout.addRow(self.pbSaveBrowse)
        formLayout.addRow(self.pbSaveSelected)
        formLayout.addRow(self.listWidget)

        self.imageDisplay = QLabel()
        self.setCentralWidget(self.imageDisplay)

        self.a = AdamAPI(dbPath)

    def querySlot(self, b):
        with waitCursorContext():
            self.listWidget.clear()

            lwis = []
            for im in self.a.queryDateRange(self.startDate.text(), self.endDate.text()):
                dateStr = im.date_time.strftime("%Y/%m/%d %I:%M:%S %p [%A]")
                lwi = QListWidgetItem(dateStr)
                lwi.setCheckState(Qt.Unchecked)
                lwi.image = im
                lwis.append(lwi)
            
            lwis.sort(key=lambda x: x.image.date_time)
            for lwi in lwis:
                self.listWidget.addItem(lwi)

    def rotateRightSlot(self, b):
        self.rotateSetting += 90
        self.rotateSetting = self.rotateSetting % 360
        self.listItemChangedSlot()

    def rotateLeftSlot(self, b):
        self.rotateSetting -= 90
        self.rotateSetting = self.rotateSetting % 360
        self.listItemChangedSlot()

    def flipSlot(self, b):
        self.rotateSetting += 180
        self.rotateSetting = self.rotateSetting % 360
        self.listItemChangedSlot()

    def saveBrowseSlot(self, b):
        ret = QFileDialog.getExistingDirectory()
        if os.path.isdir(ret):
            self.saveDir.setText(ret)

    def saveSelectedSlot(self, b):
        for i in range(self.listWidget.count()):
            lwi = self.listWidget.item(i)
            if lwi.checkState() == Qt.Checked:
                print(lwi.image.path)

    def listItemChangedSlot(self, current=None, previous=None):
        with waitCursorContext():
            if current is not None:
                self.rotateSetting = 0

            current = self.listWidget.currentItem()
            if current is not None:
                w = self.imageDisplay.size().width()
                h = self.imageDisplay.size().height()
                im = current.image.getImageData(w,h, self.rotateSetting)
                self.pm = pil2pixmap(im)
                self.imageDisplay.setPixmap(self.pm)


################################################################################
if __name__ == '__main__':
    app = QApplication(sys.argv)
    irg = ImageReviewGui(sys.argv[1])
    irg.show()
    sys.exit(app.exec_())

