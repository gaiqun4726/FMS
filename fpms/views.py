# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse
import os

from modules.preprocessor import InitialFDGenerator
from modules.loader import InitialFDLoader
from modules.generator import Generator


# Create your views here.
def generateInitialFD(request):
    initialFDGenerator = InitialFDGenerator()
    initialFDGenerator.mergeFiles()
    initialFDGenerator.generateFD()
    return HttpResponse("finished")


def getInitialFD(request):
    initialFD = InitialFDLoader.getInitialFD()
    print initialFD
    return HttpResponse("done")


def home(request):
    print 'hello world'
    return render(request, 'fpms/home.html')


def test(request):
    path = r'J:\G11_origin_data'
    dirList = []
    for parent, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            dirList.append(dirname)
    dirList.sort()
    for dirname in dirList:
        generator = Generator('test', dirname)
        generator.start()
        generator.join()
    return HttpResponse('done')
