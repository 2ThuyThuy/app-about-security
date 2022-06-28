from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import random
import cv2
import sys
import pickle
import numpy as np
import docx

def genKey():
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ID = random.choice(characters)
    for i in range(9):
        ID += random.choice(characters)
    for i in range(2):
        ID += str(random.randint(100,999))
        #print(ID)
    return ID


def to_bin(data):
    """Convert `data` to binary format as string"""
    if isinstance(data, str):
        return ''.join([ format(ord(i), "08b") for i in data ])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [ format(i, "08b") for i in data ]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")

def encode(image_name, secret_data):
    image = cv2.imread(image_name)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8
    print("[*] Maximum bytes to encode:", n_bytes)
    if len(secret_data) > n_bytes:
        raise ValueError("[!] Insufficient bytes, need bigger image or less data.")
    print("[*] Encoding data...")
    secret_data += "====="
    data_index = 0
    binary_secret_data = to_bin(secret_data)
    data_len = len(binary_secret_data)
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel)
            # modify the least significant bit only if there is still data to store
            if data_index < data_len:
                # least significant red pixel bit
                pixel[0] = int(r[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            if data_index < data_len:
                # least significant green pixel bit
                pixel[1] = int(g[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            if data_index < data_len:
                # least significant blue pixel bit
                pixel[2] = int(b[:-1] + binary_secret_data[data_index], 2)
                data_index += 1
            # if data is encoded, just break out of the loop
            if data_index >= data_len:
                break
    return image


def decode(image_name):
    print("[+] Decoding...")
    # read the image
    image = cv2.imread(image_name)
    
    binary_data = ""
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel)
            binary_data += r[-1]
            binary_data += g[-1]
            binary_data += b[-1]
    # split by 8-bits
    all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
    # convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "=====":
            break
    return decoded_data[:-5]

def getText(filename):
        doc = docx.Document(filename)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)

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
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.png)", options=options)
        return fileName


class Ui_AppAES(object):
    def setupUi(self, AppAES):

        self.PATH = os.getcwd()
        self.PATH += '\data_app'
        if not os.path.exists(self.PATH):
            os.mkdir(self.PATH)

        self.link_ImgEncode = ''
        self.link_ImgDecode = ''

        AppAES.setObjectName("AppAES")
        AppAES.resize(1260, 957)
        self.centralwidget = QtWidgets.QWidget(AppAES)
        self.centralwidget.setObjectName("centralwidget")
        self.imgEncoder = QtWidgets.QLabel(self.centralwidget)
        self.imgEncoder.setGeometry(QtCore.QRect(80, 90, 360, 360))
        self.imgEncoder.setText("")
        self.imgEncoder.setPixmap(QtGui.QPixmap("data_app/imageEncode-01.png"))
        self.imgEncoder.setObjectName("imgEncoder")
        self.imgEncoder.setScaledContents(True)
        self.imgDecode = QtWidgets.QLabel(self.centralwidget)
        self.imgDecode.setGeometry(QtCore.QRect(850, 90, 360, 360))
        self.imgDecode.setText("")
        self.imgDecode.setPixmap(QtGui.QPixmap("data_app/imageDecode-01.png"))
        self.imgDecode.setScaledContents(True)
        self.imgDecode.setObjectName("imgDecode")
        self.label_header = QtWidgets.QLabel(self.centralwidget)
        self.label_header.setGeometry(QtCore.QRect(480, 10, 551, 71))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.label_header.setFont(font)
        self.label_header.setObjectName("label_header")
        self.btnSelectImg = QtWidgets.QPushButton(self.centralwidget)
        self.btnSelectImg.setGeometry(QtCore.QRect(80, 480, 141, 71))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.btnSelectImg.setFont(font)
        self.btnSelectImg.setObjectName("btnSelectImg")
        self.btnSaveImg = QtWidgets.QPushButton(self.centralwidget)
        self.btnSaveImg.setGeometry(QtCore.QRect(1070, 480, 141, 71))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.btnSaveImg.setFont(font)
        self.btnSaveImg.setObjectName("btnSaveImg")
        self.btnEncode = QtWidgets.QPushButton(self.centralwidget)
        self.btnEncode.setGeometry(QtCore.QRect(300, 480, 141, 71))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.btnEncode.setFont(font)
        self.btnEncode.setObjectName("btnEncode")
        self.btnDecode = QtWidgets.QPushButton(self.centralwidget)
        self.btnDecode.setGeometry(QtCore.QRect(850, 480, 141, 71))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.btnDecode.setFont(font)
        self.btnDecode.setObjectName("btnDecode")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(520, 250, 231, 61))
        self.textEdit.setObjectName("textEdit")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(530, 190, 181, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.btnRandom = QtWidgets.QPushButton(self.centralwidget)
        self.btnRandom.setGeometry(QtCore.QRect(560, 330, 141, 81))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.btnRandom.setFont(font)
        self.btnRandom.setObjectName("btnRandom")
        self.txtEncode = QtWidgets.QTextEdit(self.centralwidget)
        self.txtEncode.setGeometry(QtCore.QRect(80, 670, 361, 221))
        self.txtEncode.setObjectName("txtEncode")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(80, 580, 361, 81))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.btnOpenFile = QtWidgets.QPushButton(self.centralwidget)
        self.btnOpenFile.setGeometry(QtCore.QRect(450, 670, 191, 81))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.btnOpenFile.setFont(font)
        self.btnOpenFile.setObjectName("btnOpenFile")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(850, 580, 321, 71))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.txtDecode = QtWidgets.QTextEdit(self.centralwidget)
        self.txtDecode.setGeometry(QtCore.QRect(850, 670, 361, 221))
        self.txtDecode.setObjectName("txtDecode")
        self.btnSelectImgDecode = QtWidgets.QPushButton(self.centralwidget)
        self.btnSelectImgDecode.setGeometry(QtCore.QRect(700, 90, 141, 71))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.btnSelectImgDecode.setFont(font)
        self.btnSelectImgDecode.setObjectName("btnSelectImgDecode")

        AppAES.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(AppAES)
        self.statusbar.setObjectName("statusbar")
        AppAES.setStatusBar(self.statusbar)

        self.retranslateUi(AppAES)
        QtCore.QMetaObject.connectSlotsByName(AppAES)

        # all event 
        self.btnEncode.clicked.connect(self.Click_Encode)
        self.btnDecode.clicked.connect(self.Click_Decode)
        self.btnRandom.clicked.connect(self.Click_Random)
        self.btnSelectImg.clicked.connect(self.Click_SelectImgEncode)
        self.btnSelectImgDecode.clicked.connect(self.Click_SelectImgDecode)
        self.btnOpenFile.clicked.connect(self.Click_OpenFile)
        self.btnSaveImg.clicked.connect(self.Click_SaveImg)

    def retranslateUi(self, AppAES):
        _translate = QtCore.QCoreApplication.translate
        AppAES.setWindowTitle(_translate("AppAES", "Giấu tin trong ảnh"))
        self.label_header.setText(_translate("AppAES", "GIẤU TIN TRONG ẢNH"))
        self.btnSelectImg.setText(_translate("AppAES", "Chọn ảnh"))
        self.btnSaveImg.setText(_translate("AppAES", "Lưu ảnh"))
        self.btnEncode.setText(_translate("AppAES", "Mã Hóa"))
        self.btnDecode.setText(_translate("AppAES", "Giải mã"))
        self.label.setText(_translate("AppAES", "<html><head/><body><p><span style=\" font-size:10pt;\">Khóa</span></p></body></html>"))
        self.btnRandom.setText(_translate("AppAES", "Tạo khóa "))
        self.label_2.setText(_translate("AppAES", "Nội dung giấu tin"))
        self.btnOpenFile.setText(_translate("AppAES", "Chọn từ file"))
        self.label_3.setText(_translate("AppAES", "Nội dung giải mã"))
        self.btnSelectImgDecode.setText(_translate("AppAES", "Chọn ảnh giải mã"))

   
    


    # test

    

    def openFileEncrypt(self):
        linkFile = App().initUIOpen()
        if not linkFile == '':
            f = open(linkFile,"r",encoding="utf-8")
            self.in_encrypt.setText(f.read())
            f.close()
    
    def messenger(self,x):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        
        msg.setInformativeText(x)
        msg.setWindowTitle("Thông báo")
        msg.exec_()


    ## all function click
    def Click_Encode(self):

        if self.textEdit.toPlainText() == '':
            self.messenger('Không được để trống khóa')
            return
        
        if len(self.textEdit.toPlainText()) != 16 :
            self.messenger('khóa phải đủ 16 ký tự')
            return
        if self.txtEncode.toPlainText() == '':
            self.messenger('Không được để nội dung thông tin mã hóa trống')
            return
        
        if self.link_ImgEncode == '':
            self.messenger('Phải chọn ảnh để giấu thông tin')
            return

        textEncode = self.txtEncode.toPlainText()
        lst_textEncode = [ord(i) for i in textEncode]

        key =  self.textEdit.toPlainText()
        num_key = str(random.randint(100,999))

        while key + num_key in  os.listdir(self.PATH):
            num_key = str(random.randint(100,999))

        key = key + num_key # real key
        path_folder = self.PATH + '\\' + key
        os.mkdir(path_folder)

        with open(path_folder + '\\data.txt', 'wb') as f:
            pickle.dump(lst_textEncode, f)
        
        encoded_image = encode(image_name=self.link_ImgEncode, secret_data=key)
        cv2.imwrite(path_folder+'\\encoded_image.png', encoded_image)
        self.link_ImgDecode = path_folder+'\\encoded_image.png'
        self.imgDecode.setPixmap(QtGui.QPixmap(self.link_ImgDecode))
        self.messenger("Giấu tin thành công")



    def Click_Decode(self):
        if self.textEdit.toPlainText() == '':
            self.messenger('Không được để trống khóa')
            return
        
        if self.link_ImgDecode == '':
            self.messenger('Phải chọn ảnh để mã hóa')
            return
        key = self.textEdit.toPlainText()
        decoded_data = decode(self.link_ImgDecode)

        if decoded_data[:-3] != key :
            self.messenger('Khóa không chính xác')
            return

        path_folder = self.PATH + '\\' + decoded_data
    
        with open(path_folder + '\\data.txt', 'rb') as f:
            my_list = pickle.load(f)

        ac = ''
        for i in my_list:
            ac += chr(i)
        self.txtDecode.setText(ac)
        self.messenger("Giải mã thành công")
    


    def Click_Random(self):
        txtRand = genKey()
        self.textEdit.setText(txtRand)

    def Click_SelectImgEncode(self):
        linkFile = App().initUIOpen()
        if not linkFile == '':
            #img = cv2.read(linkFile)
            #img = cv2.resize(img, (360,360))
            self.imgEncoder.setPixmap(QtGui.QPixmap(linkFile))
            self.link_ImgEncode = linkFile

    def Click_SelectImgDecode(self):
        linkFile = App().initUIOpen()
        if not linkFile == '':
            #img = cv2.read(linkFile)
            #img = cv2.resize(img, (360,360))
            self.link_ImgDecode = linkFile
            self.imgDecode.setPixmap(QtGui.QPixmap(linkFile))

    def Click_OpenFile(self):
        linkFile = App().initUIOpen()
        if not linkFile == '':
            if linkFile[-4:] == 'docx':
                text = getText(linkFile)
                self.txtEncode.setText(text)
            else:
                f = open(linkFile,"r",encoding="utf-8")
                #readFile = f.read()
                self.txtEncode.setText(f.read())
                f.close()
    
    def Click_SaveImg(self):
        
        if self.link_ImgDecode == '':
            self.messenger('Chưa có ảnh để lưu')
            return

        img = cv2.imread(self.link_ImgDecode)
        linkFile = App().saveFileDialog()
        print(linkFile)
        if not linkFile == '':
            if '.' not in linkFile:
                linkFile +='.png'
            cv2.imwrite(linkFile,img=img)
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    AppAES = QtWidgets.QMainWindow()
    ui = Ui_AppAES()
    ui.setupUi(AppAES)
    AppAES.show()
    sys.exit(app.exec_())
