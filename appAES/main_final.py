#from pyexpat.errors import messages
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import numpy as np
import random
import imageio
import cv2
import matplotlib.pyplot as plt
from skimage.morphology import convex_hull_image, erosion
from skimage.morphology import square
import skimage
import math
import os
import random
from unidecode import unidecode
import sys


def getTerminationBifurcation(img, mask):
    img = img == 255
    (rows, cols) = img.shape
    minutiaeTerm = np.zeros(img.shape)
    minutiaeBif = np.zeros(img.shape)
    
    for i in range(1,rows-1):
        for j in range(1,cols-1):
            if(img[i][j] == 1):
                block = img[i-1:i+2,j-1:j+2]
                block_val = np.sum(block)
                if(block_val == 2):
                    minutiaeTerm[i,j] = 1
                elif(block_val == 4):
                    minutiaeBif[i,j] = 1
    
    mask = convex_hull_image(mask>0)
    mask = erosion(mask, square(5))         
    minutiaeTerm = np.uint8(mask)*minutiaeTerm
    return(minutiaeTerm, minutiaeBif)


def genID():
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ID = random.choice(characters)
    ID += random.choice(characters)
    ID += str(random.randint(100,999))
    ID += str(random.randint(10,99))
    return ID

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'App'
    
    def initUIOpen(self):
        self.setWindowTitle(self.title)
        filename = self.openFileNameDialog()
        #self.show()
        return filename

    def initUISave(self):
        self.setWindowTitle(self.title)
        filename = self.saveFileDialog()
        return filename
    
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"OpenFile", "","All Files (*);;Text Files (*.txt)", options=options)
        return fileName
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        return fileName
    



class MinutiaeFeature(object):
    def __init__(self, locX, locY, Orientation, Type):
        self.locX = locX
        self.locY = locY
        self.Orientation = Orientation
        self.Type = Type

def computeAngle(block, minutiaeType):
    angle = 0
    (blkRows, blkCols) = np.shape(block)
    CenterX, CenterY = (blkRows-1)/2, (blkCols-1)/2
    if(minutiaeType.lower() == 'termination'):
        sumVal = 0
        for i in range(blkRows):
            for j in range(blkCols):
                if((i == 0 or i == blkRows-1 or j == 0 or j == blkCols-1) and block[i][j] != 0):
                    angle = -math.degrees(math.atan2(i-CenterY, j-CenterX))
                    sumVal += 1
                    if(sumVal > 1):
                        angle = float('nan')
        return(angle)
    elif(minutiaeType.lower() == 'bifurcation'):
        (blkRows, blkCols) = np.shape(block)
        CenterX, CenterY = (blkRows - 1) / 2, (blkCols - 1) / 2
        angle = []
        sumVal = 0
        for i in range(blkRows):
            for j in range(blkCols):
                if ((i == 0 or i == blkRows - 1 or j == 0 or j == blkCols - 1) and block[i][j] != 0):
                    angle.append(-math.degrees(math.atan2(i - CenterY, j - CenterX)))
                    sumVal += 1
        if(sumVal != 3):
            angle = float('nan')
        return(angle)
    


def extractMinutiaeFeatures(skel, minutiaeTerm, minutiaeBif):
    FeaturesTerm = []

    minutiaeTerm = skimage.measure.label(minutiaeTerm, connectivity=2)
    RP = skimage.measure.regionprops(minutiaeTerm)
    
    WindowSize = 2          
    FeaturesTerm = []
    for i in RP:
        (row, col) = np.int16(np.round(i['Centroid']))
        block = skel[row-WindowSize:row+WindowSize+1, col-WindowSize:col+WindowSize+1]
        angle = computeAngle(block, 'Termination')
        FeaturesTerm.append(MinutiaeFeature(row, col, angle, 'Termination'))

    FeaturesBif = []
    minutiaeBif = skimage.measure.label(minutiaeBif, connectivity=2)
    RP = skimage.measure.regionprops(minutiaeBif)
    WindowSize = 1 
    for i in RP:
        (row, col) = np.int16(np.round(i['Centroid']))
        block = skel[row-WindowSize:row+WindowSize+1, col-WindowSize:col+WindowSize+1]
        angle = computeAngle(block, 'Bifurcation')
        FeaturesBif.append(MinutiaeFeature(row, col, angle, 'Bifurcation'))
    return(FeaturesTerm, FeaturesBif)




class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        self.PATH = os.getcwd()
        self.PATH +='\data'
        if not os.path.exists(self.PATH):
            os.mkdir(self.PATH)


        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1299, 855)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(-10, 0, 1271, 821))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")
        self.tabKiemTraVanTay = QtWidgets.QWidget()
        self.tabKiemTraVanTay.setObjectName("tabKiemTraVanTay")
        self.txtID = QtWidgets.QPlainTextEdit(self.tabKiemTraVanTay)
        self.txtID.setGeometry(QtCore.QRect(580, 90, 451, 79))
        self.txtID.setObjectName("txtID")
        self.label = QtWidgets.QLabel(self.tabKiemTraVanTay)
        self.label.setGeometry(QtCore.QRect(160, 90, 221, 71))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.tabKiemTraVanTay)
        self.label_2.setGeometry(QtCore.QRect(160, 230, 291, 71))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.tabKiemTraVanTay)
        self.label_3.setGeometry(QtCore.QRect(160, 410, 261, 71))
        self.label_3.setObjectName("label_3")
        self.txtName = QtWidgets.QPlainTextEdit(self.tabKiemTraVanTay)
        self.txtName.setGeometry(QtCore.QRect(580, 220, 451, 91))
        self.txtName.setObjectName("txtName")
        self.txtLinkFinger = QtWidgets.QPlainTextEdit(self.tabKiemTraVanTay)
        self.txtLinkFinger.setGeometry(QtCore.QRect(580, 400, 451, 101))
        self.txtLinkFinger.setObjectName("txtLinkFinger")
        self.btnLinkAnh = QtWidgets.QPushButton(self.tabKiemTraVanTay)
        self.btnLinkAnh.setGeometry(QtCore.QRect(1100, 420, 151, 81))
        self.btnLinkAnh.setObjectName("btnLinkAnh")
        self.btnKiemTra = QtWidgets.QPushButton(self.tabKiemTraVanTay)
        self.btnKiemTra.setGeometry(QtCore.QRect(860, 580, 161, 91))
        self.btnKiemTra.setObjectName("btnKiemTra")
        self.tabWidget.addTab(self.tabKiemTraVanTay, "")
        self.btnClear = QtWidgets.QPushButton(self.tabKiemTraVanTay)
        self.btnClear.setGeometry(QtCore.QRect(360, 580, 161, 91))
        self.btnClear.setObjectName("btnClear")

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_5 = QtWidgets.QLabel(self.tab_2)
        self.label_5.setGeometry(QtCore.QRect(110, 30, 301, 91))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.tab_2)
        self.label_6.setGeometry(QtCore.QRect(110, 220, 201, 61))
        self.label_6.setObjectName("label_6")
        self.txtAddLinkFinger = QtWidgets.QPlainTextEdit(self.tab_2)
        self.txtAddLinkFinger.setGeometry(QtCore.QRect(500, 210, 401, 101))
        self.txtAddLinkFinger.setObjectName("txtAddLinkFinger")
        self.txtAddName = QtWidgets.QPlainTextEdit(self.tab_2)
        self.txtAddName.setGeometry(QtCore.QRect(500, 30, 401, 101))
        self.txtAddName.setObjectName("txtAddName")
        self.btnAddLinkFinger = QtWidgets.QPushButton(self.tab_2)
        self.btnAddLinkFinger.setGeometry(QtCore.QRect(950, 210, 141, 81))
        self.btnAddLinkFinger.setObjectName("btnAddLinkFinger")
        self.btnAddNew = QtWidgets.QPushButton(self.tab_2)
        self.btnAddNew.setGeometry(QtCore.QRect(730, 360, 171, 71))
        self.btnAddNew.setObjectName("btnAddNew")
        self.txtInfor = QtWidgets.QTextBrowser(self.tab_2)
        self.txtInfor.setGeometry(QtCore.QRect(500, 460, 621, 261))
        self.txtInfor.setObjectName("txtInfor")
        self.label_7 = QtWidgets.QLabel(self.tab_2)
        self.label_7.setGeometry(QtCore.QRect(140, 540, 201, 61))
        self.label_7.setObjectName("label_7")
        self.btnAddClear = QtWidgets.QPushButton(self.tab_2)
        self.btnAddClear.setGeometry(QtCore.QRect(1040, 30, 151, 71))
        self.btnAddClear.setObjectName("btnAddClear")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        #something
        self.btnLinkAnh.clicked.connect(self.openLink)
        self.btnAddLinkFinger.clicked.connect(self.openAddLink)
        self.btnAddNew.clicked.connect(self.addNewPerson)
        self.btnClear.clicked.connect(self.checkClear)
        self.btnAddClear.clicked.connect(self.addClear)
        self.btnKiemTra.clicked.connect(self.checkPerson)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "ID:"))
        self.label_2.setText(_translate("MainWindow", "Tên người dùng:"))
        self.label_3.setText(_translate("MainWindow", "Ảnh vân tay: "))
        self.btnLinkAnh.setText(_translate("MainWindow", "Chọn"))
        self.btnKiemTra.setText(_translate("MainWindow", "Kiểm tra"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabKiemTraVanTay), _translate("MainWindow", "Kiểm tra"))
        self.btnClear.setText(_translate("MainWindow", "Xóa"))
        self.label_5.setText(_translate("MainWindow", "Tên người dùng mới:"))
        self.label_6.setText(_translate("MainWindow", "Ảnh vân tay: "))
        self.btnAddLinkFinger.setText(_translate("MainWindow", "Chọn"))
        self.btnAddNew.setText(_translate("MainWindow", "Thêm mới"))
        self.label_7.setText(_translate("MainWindow", "Thông tin"))
        self.btnAddClear.setText(_translate("MainWindow", "Xóa"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Thêm Mới"))
    
    def openLink(self):
        linkFile = App().initUIOpen()
        if not linkFile == '':
            self.txtLinkFinger.setPlainText(linkFile)

    def openAddLink(self):
        linkFile = App().initUIOpen()
        if not linkFile == '':
            self.txtAddLinkFinger.setPlainText(linkFile)

    def checkClear(self):
        self.txtID.setPlainText('')
        self.txtLinkFinger.setPlainText('')
        self.txtName.setPlainText('')

    def addClear(self):
        self.txtAddName.setPlainText('')
        self.txtAddLinkFinger.setPlainText('')
        self.txtInfor.setPlainText('')

    def messenger(self,x):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setInformativeText("Không được để trống {}".format(x))
        msg.setWindowTitle("Thông báo")
        msg.exec_()
    
    def checkMessenger(self,x):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        if x == 'ID':
            msg.setInformativeText("không có ID này")
        elif x == 'Name':
            msg.setInformativeText("Tên người dùng sai")
        elif x == 'false':
             msg.setInformativeText("Vân Tay không chính xác")
        else :
             msg.setInformativeText("Thành công !!!")
        msg.setWindowTitle("Thông báo")
        msg.exec_()

    def addNewPerson(self):
        if self.txtAddName.toPlainText() == '' :
            self.messenger('Tên')
            return
        if self.txtAddLinkFinger.toPlainText() == '':
            self.messenger('link ảnh')
            return
        
        personName = self.txtAddName.toPlainText()
        personName = unidecode(personName).upper()
        personID = genID()
        while personID in os.listdir(self.PATH):
            personID = genID

        Pathfinger = self.txtAddLinkFinger.toPlainText()
        PATHID = self.PATH + '\\' + personID
        os.mkdir(PATHID)
        f=open(PATHID+'\\name.txt','w')
        f.write(personName)
        f.close()

        img1 = imageio.imread(Pathfinger)
        THRESHOLD1= img1.mean()
        img = cv2.imread(Pathfinger,0) 
        img = np.array(img > THRESHOLD1).astype(int)
        skel = skimage.morphology.skeletonize(img)
        skel = np.uint8(skel)*255
        mask = img*255

        (minutiaeTerm, minutiaeBif) = getTerminationBifurcation(skel, mask)
        FeaturesTerm, FeaturesBif = extractMinutiaeFeatures(skel, minutiaeTerm, minutiaeBif)
        
        BifLabel = skimage.measure.label(minutiaeBif, connectivity=1)
        TermLabel = skimage.measure.label(minutiaeTerm, connectivity=1)

        #BifLabel = BifLabel.astype(int)
        #TermLabel = TermLabel.astype(int)
        #print(BifLabel)
        np.savetxt(PATHID+'\\BifLabel.txt',BifLabel)
        np.savetxt(PATHID+'\\TermLabel.txt',TermLabel)

        self.txtInfor.setPlainText('ID: '+personID+'\nHọ và tên: '+personName)

    def checkPerson(self):
        if self.txtID.toPlainText() == '':
            self.messenger('ID')
            return
        if self.txtName.toPlainText() == '':
            self.messenger('Họ và Tên')
            return
        if self.txtLinkFinger.toPlainText() == '':
            self.messenger('')
            return

        ID = self.txtID.toPlainText()
        name = self.txtName.toPlainText()
        pathFinger = self.txtLinkFinger.toPlainText()
        pathPerson = self.PATH+'\\'+ID
        if ID not in os.listdir(self.PATH):
            self.checkMessenger('ID')
            return
        
        name = unidecode(name).upper()

        f = open(pathPerson+'\\name.txt','r')
        checkName = f.read()
        f.close

        if not checkName == name:
            self.checkMessenger('Name')
            return
        

        img1 = imageio.imread(pathFinger)
        THRESHOLD1= img1.mean()
        img = cv2.imread(pathFinger,0) 
        img = np.array(img > THRESHOLD1).astype(int)
        skel = skimage.morphology.skeletonize(img)
        skel = np.uint8(skel)*255
        mask = img*255
        (minutiaeTerm, minutiaeBif) = getTerminationBifurcation(skel, mask)
        FeaturesTerm, FeaturesBif = extractMinutiaeFeatures(skel, minutiaeTerm, minutiaeBif)
        BifLabel = skimage.measure.label(minutiaeBif, connectivity=1)
        TermLabel = skimage.measure.label(minutiaeTerm, connectivity=1)

        matrixBif = np.loadtxt(pathPerson+'\\BifLabel.txt')
        matrixTerm = np.loadtxt(pathPerson+'\\TermLabel.txt')


        checkBif = matrixBif == BifLabel
        checkTerm = matrixTerm == TermLabel
        #print(np.linalg.matrix_rank(matrixBif),np.linalg.matrix_rank(BifLabel),np.linalg.matrix_rank(matrixTerm),np.linalg.matrix_rank(TermLabel))

        if checkBif.all() and checkTerm.all():
            self.checkMessenger('win')
        else:
            self.checkMessenger('false')
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
