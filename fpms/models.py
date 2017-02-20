# coding=utf-8
from __future__ import unicode_literals

from django.db import models


# Create your models here.
# 初始指纹库
class InitialFD(models.Model):
    locationID = models.CharField(max_length=20)
    apMAC = models.CharField(max_length=20)
    rssi = models.IntegerField(default=-100)
    channel = models.IntegerField(default=0)


# 更新指纹库
class UpdateFD(models.Model):
    locationID = models.CharField(max_length=20)
    apMAC = models.CharField(max_length=20)
    rssi = models.IntegerField(default=-100)
    channel = models.IntegerField(default=0)


# 部分更新指纹库
class PartialFD(models.Model):
    locationID = models.CharField(max_length=20)
    apMAC = models.CharField(max_length=20)
    rssi = models.IntegerField(default=-100)
    channel = models.IntegerField(default=0)
    usability = models.BooleanField(default=False)
    historyDataPath = models.CharField(max_length=100)


# 设备间信号强度回归系数数据库
class RegParameters(models.Model):
    # 测量MU
    surveyMU = models.CharField(max_length=20)
    # 普通MU
    commonMU = models.CharField(max_length=20)
    # 斜率
    a = models.FloatField(default=0)
    # 截矩
    b = models.FloatField(default=0)
    # 权重
    parameterUsability = models.BooleanField(default=False)
    # 训练数据集所在路径
    trainSetPath = models.CharField(max_length=100)
