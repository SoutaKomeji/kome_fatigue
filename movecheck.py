# 単に動作が心配なものを突っ込んでは消してを繰り返すだけの場所
from math import factorial
import numpy as np
import random
# import xlrd
import time
import getData

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

from move_fatigue_calculater import get_routeCoord, get_distance_and_angles, calculate_METs # metsを用いた疲労度計算があるファイルをimport

start_time = time.time()
# Problem definition
# PROBLEM = "dtlz2"

#目的関数の数の設定
# NOBJ = 9 #歩数あり
NOBJ = 4

K = 10
NDIM = NOBJ + K - 1
P = 2
H = factorial(NOBJ + P - 1) / (factorial(P) * factorial(NOBJ - 1))

# 制限時間
timeLimit = 60 * 4

# 各評価値の最大，最小値を測定
BOUND_LOW, BOUND_UP = [],[]



maxList = [1.0,1.0,1.0,1.0]
minList = [0.0,0.0,0.0,0.0]

data = pd.read_excel('preExpData_fatigue.xlsx')
spotData = []
tTimeData = []
stepData = []
watchData = []
coordsData = []
heightData = []
metsFatigueData = []

SPOT_NUM = 56

# pandasで特定のシートを読み込む
featureSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='特徴表')
tTimeSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポット間移動時間')
stepSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポット間移動歩数')
watchTimeSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポットでの観光時間')
coordsSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='座標取得')
heightSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='高さの取得')
metsFatigueSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='METsを用いた移動による疲労')


for i in range(SPOT_NUM + 1):
    spotData.append(featureSheet.iloc[i+25,1:10].values)
    tTimeData.append(tTimeSheet.iloc[i,2:SPOT_NUM + 3].values)
    stepData.append(stepSheet.iloc[i,2:SPOT_NUM + 3].values)
    watchData.append(watchTimeSheet.iloc[i+25,4:5].values)
    coordsData.append(coordsSheet.iloc[i,1:3].values)
    heightData.append(heightSheet.iloc[i,1:2].values)
    metsFatigueData.append(metsFatigueSheet.iloc[i,1:SPOT_NUM + 2].values)

# print(stepData)
# print(heightData)
# print(metsFatigueData)