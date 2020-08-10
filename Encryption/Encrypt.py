import decimal
import math
import random
import Encryption.Key as Key
import pickle

from Encryption.FaceDetection import Detection

from PIL import Image

getIfromRGB = lambda val: int(
    (val[0] << 16) + (val[1] << 8) + val[2])  # this lamda expression converts pixel value(rgb) to int
getRGBfromI = lambda val: ((val >> 16) & 255, (val >> 8) & 255, val & 255)  # this function gives rgb value from int


class FileEncryption:
    def __init__(self, filename):
        self.filepath = "Images\\" + filename
        self.l = None
        self.x = None
        self.sigma=None
        self.xs=None
        self.n_seg=None
        self.key = Key.keyFile()

    def encrypt(self):
        obj = Detection(self.filepath)
        cordinates = obj.getFaceCordinates()
        self.key.cordinates=cordinates
        img = Image.open(self.filepath)
        pixelMap = img.load()
        allfaces = []
        ind=0
        # for cordinate in cordinates:
        #     allfaces.append(self.getFacePixels(pixelMap,cordinate))
            # print(allfaces[ind],end="\n")
            # ind=ind+1
        # for face in allfaces:
        #     ind = 0
        #     while ind <= 10:
        #         print(face[ind], end=' ')
        #         ind += 1
        #     print("\n")
        # print("break\n")
        self.confusion(cordinates, pixelMap, allfaces)
        ind=0
        # for face in allfaces:
        #     ind = 0
        #     while ind <= 10:
        #         print(face[ind], end=' ')
        #         ind += 1
        #     print("\n")
        self.diffusion(cordinates, pixelMap, allfaces)
        # print("after scramble\n")
        # for face in allfaces:
        #     ind = 0
        #     while ind <= 10:
        #         print(face[ind], end=' ')
        #         ind += 1
        #     print("\n")
        img.show()
        path = "Images/encrypted.png"
        img.save(path)
        img.close()

    def confusion(self, cordinates, pixelMap, allfaces):
        # print("confusion" ,end="\n")

        for cordinate in cordinates:
            self.getInitialValues(cordinate)
            allfaces.append(self.modifyFace(cordinate, pixelMap))

    def modifyFace(self, cordinate, pixelMap):
        x = cordinate[0]
        y = cordinate[1]
        w = cordinate[2]
        h = cordinate[3]
        pix = []
        ind = 0
        val = self.x
        for j in range(y, y + h):
            for i in range(x, x + w):
                val = (self.l) * (val) * (1 - val)
                valconf = round(val * 16777215)
                # pixelsNew[i,j]=pixelsNew[i,j]^valconf
                value = getIfromRGB(pixelMap[i, j])
                # it accepts a tuple of rgb values
                pixelMap[i, j] = getRGBfromI(value ^ valconf)
                pix.append(value^valconf)
                # ind+=1
        return pix

    def scramble(self, cordinate, pixelMap, pix):
        # print("diffusion",end="\n")

        #print("sigma =",sigma)
        #print("xs= ",xs)
        size = cordinate[2] * cordinate[3]
        spix = int(math.ceil(size / self.n_seg))
        num_seg = 0
        indx = 0
        xcurr = self.xs
        ret = pix.copy()
        while num_seg < self.n_seg:
            start = indx

            ma = min(size, start + spix) - start  # size of pix array
            pos = [ok for ok in range(ma)]

            # scrambling is done here
            i = 0
            list1 = []

            while i < ma:
                val_s = self.sigma * decimal.Decimal(math.sin(decimal.Decimal(math.pi) * xcurr))
                position = round(val_s * decimal.Decimal(len(pos) - 1))

                list1.append(pos[position])
                pos.remove(pos[position])

                xcurr = val_s
                i += 1
                indx += 1

            i = 0
            for ok in list1:
                ret[start + i] = pix[start + ok]
                i += 1
            num_seg += 1
        x = cordinate[0]
        y = cordinate[1]
        w = cordinate[2]
        h = cordinate[3]
        ind = 0
        for j in range(y, y + h):
            for i in range(x, x + w):
                value = ret[ind]
                ind += 1
                # it accepts a tuple of rgb values
                pixelMap[i, j] = getRGBfromI(value)

        return ret

    def diffusion(self, cordinates, pixelMap, allfaces):
        ind = 0
        for cordinate in cordinates:
            # self.getInitialValues(cordinate)
            allfaces[ind] = self.scramble(cordinate, pixelMap, allfaces[ind])
            ind += 1

    def getFacePixels(self, pixelMap, cordinate):
        x = cordinate[0]
        y = cordinate[1]
        w = cordinate[2]
        h = cordinate[3]
        pix = []
        for j in range(y,y+h):
            for i in range(x,x+w):
                pix.append(getIfromRGB(pixelMap[i,j]))
        return pix

    def getInitialValues(self,cordinate):
        # select a random value between a and b inclusive both
        self.l = random.randint(3560000, 4000000) / 1000000
        #print("l= ",self.l)
        self.x = random.randint(0, 1000000) / 1000000
        #print("x= ",self.x)
        size = cordinate[2] * cordinate[3]
        # no of segments into which face is divided
        self.n_seg = random.randint(10, size // 100)
        self.sigma = decimal.Decimal(random.randrange(8700000, 10000000)) / 10000000
        self.xs = decimal.Decimal(random.randrange(0, 10000000)) / 10000000
        val = [self.x,self.l,self.n_seg,self.sigma,self.xs]
        self.key.constants.append(val)

def main():
    obj = FileEncryption('image2.png')
    obj.encrypt()
    with open('key.pkl', 'wb') as output:
        pickle.dump(obj.key, output, pickle.HIGHEST_PROTOCOL)
    # with open('key.pkl', 'rb') as input:
    #     retrievedKey = pickle.load(input)
    # print(retrievedKey.cordinates,end=' ')
    # print("\n")
    # for val in retrievedKey.constants:
    #     print(val,end="\n")

main()

