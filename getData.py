from math import factorial
import numpy as np
import random
# import xlrd
import time

# import matplotlib.pyplot as plt
import numpy
# import pymop.factory
import copy
import pandas as pd

from deap import algorithms
from deap import base
from deap.benchmarks.tools import igd
from deap import creator
from deap import tools

start_time = time.time()
# pandasでread_excel
data = pd.read_excel('preExpData_fatigue.xlsx')
spotData = []
tTimeData = []
stepData = []
watchTime = []

SPOT_NUM = 56

# pandasで特定のシートを読み込む
featureSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='特徴表')
tTimeSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポット間移動時間')
stepSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポット間移動歩数')
watchTimeSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポットでの観光時間')

for i in range(SPOT_NUM + 1):
    spotData.append(featureSheet.iloc[i+25,1:10].values)
    tTimeData.append(tTimeSheet.iloc[i,2:SPOT_NUM + 3].values)
    stepData.append(stepSheet.iloc[i,2:SPOT_NUM + 3].values)
    watchTime.append(watchTimeSheet.iloc[i+25,4:5].values)

# def getData():
#     spotData = []
#     tTimeData = []
#     stepData = []
#     watchTime = []

#     SPOT_NUM = 56

#     # pandasで特定のシートを読み込む
#     featureSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='特徴表')
#     tTimeSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポット間移動時間')
#     stepSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポット間移動歩数')
#     watchTimeSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポットでの観光時間')

#     for i in range(SPOT_NUM + 1):
#         spotData.append(featureSheet.iloc[i+25,1:10].values)
#         tTimeData.append(tTimeSheet.iloc[i,2:SPOT_NUM + 3].values)
#         stepData.append(stepSheet.iloc[i,2:SPOT_NUM + 3].values)
#         watchTime.append(watchTimeSheet.iloc[i+25,4:5].values)


#     return spotData, tTimeData, stepData, watchTime

