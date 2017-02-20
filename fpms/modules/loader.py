# coding=utf-8

# from fpms.models import InitialFD
from xml.dom.minidom import parse
import xml.dom.minidom
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# 从xml文件加载资源文件类
class ResLoader(object):
    __DOMTree = xml.dom.minidom.parse(os.path.join(BASE_DIR, "static/configs/resources.xml"))
    __collection = __DOMTree.documentElement

    @staticmethod
    def getRootPath():
        return ResLoader.__collection.getElementsByTagName("rootpath")[0].childNodes[0].data

    @staticmethod
    def getOriginDataPath():
        return ResLoader.__collection.getElementsByTagName("origindatapath")[0].childNodes[0].data

    @staticmethod
    def getMiddleFilePath():
        return ResLoader.__collection.getElementsByTagName("middlefilepath")[0].childNodes[0].data

    @staticmethod
    def getLocInfoPath():
        return ResLoader.__collection.getElementsByTagName("locinfopath")[0].childNodes[0].data

    @staticmethod
    def getMergeFilePath():
        return ResLoader.__collection.getElementsByTagName("mergefilepath")[0].childNodes[0].data


# 从数据库加载初始指纹库类
# class InitialFDLoader(object):
#     def getInitialFD():
#         objects = InitialFD.objects.all()
#         fd_dict = {}
#         for item in objects:
#             locationID = item.locationID
#             apMAC = item.apMAC
#             rssi = item.rssi
#             channel = item.channel
#             level1 = fd_dict.get(locationID, {})
#             level1[apMAC] = {'rssi': rssi, 'channel': channel}
#         return fd_dict

# 部分更新指纹库和回归系数表始终在变化，所以不能使用静态方法从数据库中读取数据

# 从数据库加载部分更新指纹库类
# class PartialFDLoader(object):
#     def getPartialFD():
#         fd_dict = {}
#         return fd_dict


# 从数据库加载回归系数表类
# class ParameterLoader(object):
#     def getParameter():
#         pass


# 从csv文件中加载指纹库
class SpectrumLoader(object):
    path = r"L:\Graduation Project\finger data\middleFile\2017-01-20\B4-0B-44-2F-C8-A2spectrum.csv"

    # 从指纹库的csv文件加载指纹库字典
    def loadSpectrum(self):
        df = pd.read_csv(self.path, index_col='locationID')
        global spectrumDict
        for key1 in df.index:
            sr = df.ix[key1]
            lv2val = {}
            for key2 in sr.index:
                lv2val[key2] = [sr[key2], ]
            spectrumDict[key1] = lv2val

        print 'load spectrum finished'
