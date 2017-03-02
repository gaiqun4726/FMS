# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse

from modules.preprocessor import InitialFDGenerator
from modules.loader import InitialFDLoader


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
