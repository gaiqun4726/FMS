# coding=utf-8
import pandas as pd

path1 = r"L:\Graduation Project\finger data\middleFile\2017-01-20\B4-0B-44-2F-C8-A2spectrum.csv"
path2 = r"J:\demo\2017-02-17\B4-0B-44-2F-C8-A2spectrum.csv"
path3 = r"C:\Users\DELL\Desktop\spectrum.csv"

df1 = pd.read_csv(path1, index_col=['locationID'])
df2 = pd.read_csv(path2, index_col=['locationID'])

indexList = list(df1.index)
columnList = list(df1.columns)

# 将两次的指纹库融合起来，仅供测试使用
for index in indexList:
    if index in df2.index:
        for column in columnList:
            if df1.ix[index,column] == -100 and df2.ix[index,column] != -100:
                df1.ix[index, column] = df2.ix[index,column]

df1.to_csv(path3)
