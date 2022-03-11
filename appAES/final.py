import numpy as np
import glob
import random
import imageio
import PIL, cv2
import pandas as pd
import matplotlib.pyplot as plt
from skimage.morphology import convex_hull_image, erosion
from skimage.morphology import square
import matplotlib.image as mpimg
import skimage
import math
from scipy.ndimage.filters import convolve
from PIL import Image,ImageFilter
from skimage.feature import hessian_matrix, hessian_matrix_eigvals
import os
import random
from unidecode import unidecode
import sys
np.set_printoptions(threshold=sys.maxsize) # in hết giá trị của mảng trong python


#FeaturesTerm, FeaturesBif

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


class MinutiaeFeature(object):
    def __init__(self, locX, locY, Orientation, Type):
        self.locX = locX;
        self.locY = locY;
        self.Orientation = Orientation;
        self.Type = Type;

def computeAngle(block, minutiaeType):
    angle = 0
    (blkRows, blkCols) = np.shape(block);
    CenterX, CenterY = (blkRows-1)/2, (blkCols-1)/2
    if(minutiaeType.lower() == 'termination'):
        sumVal = 0;
        for i in range(blkRows):
            for j in range(blkCols):
                if((i == 0 or i == blkRows-1 or j == 0 or j == blkCols-1) and block[i][j] != 0):
                    angle = -math.degrees(math.atan2(i-CenterY, j-CenterX))
                    sumVal += 1
                    if(sumVal > 1):
                        angle = float('nan');
        return(angle)
    elif(minutiaeType.lower() == 'bifurcation'):
        (blkRows, blkCols) = np.shape(block);
        CenterX, CenterY = (blkRows - 1) / 2, (blkCols - 1) / 2
        angle = []
        sumVal = 0;
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

    minutiaeTerm = skimage.measure.label(minutiaeTerm, connectivity=2);
    RP = skimage.measure.regionprops(minutiaeTerm)
    
    WindowSize = 2          
    FeaturesTerm = []
    for i in RP:
        (row, col) = np.int16(np.round(i['Centroid']))
        block = skel[row-WindowSize:row+WindowSize+1, col-WindowSize:col+WindowSize+1]
        angle = computeAngle(block, 'Termination')
        FeaturesTerm.append(MinutiaeFeature(row, col, angle, 'Termination'))

    FeaturesBif = []
    minutiaeBif = skimage.measure.label(minutiaeBif, connectivity=2);
    RP = skimage.measure.regionprops(minutiaeBif)
    WindowSize = 1 
    for i in RP:
        (row, col) = np.int16(np.round(i['Centroid']))
        block = skel[row-WindowSize:row+WindowSize+1, col-WindowSize:col+WindowSize+1]
        angle = computeAngle(block, 'Bifurcation')
        FeaturesBif.append(MinutiaeFeature(row, col, angle, 'Bifurcation'))
    return(FeaturesTerm, FeaturesBif)



def genID():
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ID = random.choice(characters)
    ID += random.choice(characters)
    ID += str(random.randint(100,999))
    ID += str(random.randint(10,99))
    return ID

def addNewFinger(PATH):
    personName = input('Name: ')
    personName = unidecode(personName).upper()
    personID = genID()
    while personID in os.listdir(PATH):
        personID = genID()
    
    PATHfinger = input('Link ảnh: ')

    PATHID = PATH + '\\' + personID
    os.mkdir(PATHID)
    f=open(PATHID+'\\name.txt', 'w')
    f.write(personName)
    f.close()

    img1 = imageio.imread(PATHfinger)
    THRESHOLD1= img1.mean()

    img = cv2.imread(PATHfinger,0)
    img = np.array(img > THRESHOLD1).astype(int)
    skel = skimage.morphology.skeletonize(img)
    skel = np.uint8(skel)*25
    mask = img*255

    (minutiaeTerm, minutiaeBif) = getTerminationBifurcation(skel, mask)
    FeaturesTerm, FeaturesBif = extractMinutiaeFeatures(skel, minutiaeTerm, minutiaeBif)
    BifLabel = skimage.measure.label(minutiaeBif, connectivity=1)
    TermLabel = skimage.measure.label(minutiaeTerm, connectivity=1)

    BifLabel = BifLabel.astype(int)
    TermLabel = TermLabel.astype(int)
    #print(BifLabel)
    np.savetxt(PATHID+'\\BifLabel.txt',BifLabel)
    np.savetxt(PATHID+'\\TermLabel.txt',TermLabel)

PATH = os.getcwd()
PATH += '\data'
if not os.path.exists(PATH) :
    os.mkdir(PATH)

addNewFinger(PATH=PATH)
#đầu vào ở dây
#img_name = '102__M_Left_ring_finger.bmp'  # đường dẫn file ảnh
#name = str(input('Nhập tên: '))


'''
img1 = imageio.imread(img_name)
THRESHOLD1= img1.mean()

img = cv2.imread(img_name,0);
img = np.array(img > THRESHOLD1).astype(int)
skel = skimage.morphology.skeletonize(img)
skel = np.uint8(skel)*255;
mask = img*255;

(minutiaeTerm, minutiaeBif) = getTerminationBifurcation(skel, mask);
FeaturesTerm, FeaturesBif = extractMinutiaeFeatures(skel, minutiaeTerm, minutiaeBif)
BifLabel = skimage.measure.label(minutiaeBif, connectivity=1);
TermLabel = skimage.measure.label(minutiaeTerm, connectivity=1);


BifLabel = BifLabel.astype(int)
#print(BifLabel)
np.savetxt('test.txt',BifLabel)



matrix = np.loadtxt('test.txt').astype(int)
#print(matrix)
print(BifLabel.shape)
print(matrix.shape)
res = matrix == BifLabel
print(res.all())
#ShowResults(skel, TermLabel, BifLabel)
'''