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

import getData

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

# # 歩数なし
# maxList = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
# minList = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]

# # 歩数あり
# maxList = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
# minList = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]

# 疲労，観光時間追加
maxList = [1.0,1.0,1.0,1.0]
minList = [0.0,0.0,0.0,0.0]

# Excelデータの読み込みを始める行番号を指定
row = 26

# Algorithm parameters
MU = 200 #int(H + (4 - H % 4))
#交叉率
CXPB = 90 # ％表記でお願いします
#s突然変異率
MUTPB = 10 # ％表記でお願いします
##

# # Create uniform reference point
# # ここでリファレンスポイントを作成している（NOBJ:目的関数の数，P:リファレンスポイントの次元）
ref_points = tools.uniform_reference_points(NOBJ, P)

# reference points の表示
# for i in range(len(ref_points)):
#     print("ref_points[",i,"]:",ref_points[i])


# 各リファレンスポイントに関連する解の個体数を把握するための変数
num_associate_rp = []

# １つのリファレンスポイントの評価値を保存する用の変数
record_evaluate_value = []

# 各世代の親個体，交叉した個体，変異した個体の個数を格納する
# 生存率の計算が機能しているか確認する用
ind_ratio = [0,0,0]

# 生存率を格納する容器
# survive_mate_pro = []
# survive_mutate_pro = []
survive_new_ind_pro = [] # 交叉した個体と突然変異した個体を合計した生存率

data = pd.read_excel('preExpData_fatigue.xlsx')
spotData = []
tTimeData = []
stepData = []
watchData = []
metsFatigueData = []

SPOT_NUM = 56

# pandasで特定のシートを読み込む
featureSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='特徴表')
tTimeSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポット間移動時間')
stepSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポット間移動歩数')
watchTimeSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='スポットでの観光時間')
metsFatigueSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='METsを用いた移動による疲労')

for i in range(SPOT_NUM + 1):
    spotData.append(featureSheet.iloc[i+25,1:10].values)
    tTimeData.append(tTimeSheet.iloc[i,2:SPOT_NUM + 3].values)
    stepData.append(stepSheet.iloc[i,2:SPOT_NUM + 3].values)
    watchData.append(watchTimeSheet.iloc[i+25,4:5].values)
    metsFatigueData.append(metsFatigueSheet.iloc[i,1:SPOT_NUM + 2].values)


# 目的関数のweight(自然，文化，身体的疲労，精神的疲労，観光時間，移動時間)=(1.0,1.0,-1.0,-1.0,-1.0,-1.0)
# print("spotData:", spotData)
# print("len:", len(spotData))
# print("tTimeData:", tTimeData)
# print("len:", len(tTimeData))
# print("stepData:", stepData)
# print("len:", len(stepData))
# print("watchData:", watchData)
# print("len:", len(watchData))
# print("metsFatigueData:", metsFatigueData)
# print("len:", len(metsFatigueData))
## 観光スポットのデータ作成終了

# for i in range(MU * CXPB // 200):
#         # ルーレット選択で交叉する親個体を選ぶ
#         # 累積適応度を計算
#         selected_parents = []
#         for _ in range(2):  # 2人の親を選ぶ
#             r = random.uniform(0, total_fitness)
#             cumulative_fitness = 0
#             for ind in parents:
#                 cumulative_fitness += ind.fitness.values[0]
#                 if cumulative_fitness >= r:
#                     selected_parents.append(ind)
#                     break

#         # 選択した親を交叉させる
#         child1, child2 = toolbox.mate(toolbox.clone(selected_parents[0]), toolbox.clone(selected_parents[1]), gen)

#         if(debug.mate_check):
#             print("交叉する親個体A：", selected_parents[0], "交叉により生まれたchild1：", child1)
#             print("交叉する親個体B：", selected_parents[1], "交叉により生まれたchild2：", child2)
        
#         offsprings.append(child1)
#         offsprings.append(child2)

# 交叉
def mate(inds1, inds2, gen):

    # コースを分割する場所を決定
    ind1 = copy.deepcopy(inds1)
    ind2 = copy.deepcopy(inds2)

    if len(ind1[0]) <= 2 or len(ind2[0]) <= 2:
        return ind1, ind2

    child1= []
    child2= []

    breakP1 = random.randint(1,len(ind1[0])-1)
    breakP2 = random.randint(1,len(ind2[0])-1)

    ind1Front = ind1[0][0:breakP1]
    ind1Behind = ind1[0][breakP1:len(ind1[0])]
    ind2Front = ind2[0][0:breakP2]
    ind2Behind = ind2[0][breakP2:len(ind2[0])]

    # 重複があった場合に，ランダムに削除する(course1用)
    t = [x for x in set(ind1Front + ind2Behind) if (ind1Front + ind2Behind).count(x) > 1]
    if SPOT_NUM in t:
        t.remove(SPOT_NUM)
    for i in t:
        loot = random.randint(0,1)

        if(loot == 0):
            ind1Front.remove(i)
        else:
            ind2Behind.remove(i)
    
    # 重複があった場合に，ランダムに削除する(course2用)
    t = [x for x in set(ind2Front + ind1Behind) if (ind2Front + ind1Behind).count(x) > 1]
    if SPOT_NUM in t:
        t.remove(SPOT_NUM)
    # if(t):
    for i in t:
        loot = random.randint(0,1)
        if(loot == 0):
            ind2Front.remove(i)
        else:
            ind1Behind.remove(i)
    
    course1 = ind1Front + ind2Behind
    course2 = ind2Front + ind1Behind

    child1.append(course1)
    child2.append(course2)

    #　トータルの観光時間と移動のみの時間，制限時間との差分を算出する
    totaltime = 0
    walktime = 0
    steps = 0

    # 身体的疲労度(mets移動)
    metsFatigue = 0

    for j in range(len(course1) - 1):
        totaltime += tTimeData[course1[j]][course1[j+1]] + watchData[course1[j]]
        walktime += int(tTimeData[course1[j]][course1[j+1]])
        steps += int(stepData[course1[j]][course1[j+1]])
        metsFatigue += metsFatigueData[course1[j]][course1[j+1]]

    if totaltime[0] < timeLimit + int(timeLimit/10) and totaltime[0] > timeLimit - (int(timeLimit/10))*2:
        child1.append(totaltime[0])
        child1.append(walktime)
        child1.append(metsFatigue)
        child1.append(gen + 1)

        childA = copy.deepcopy(child1)
    else:
        childA = [[0],0,0,0,0]

    totaltime = 0
    walktime = 0
    steps = 0

    metsFatigue = 0

    for j in range(len(course2) - 1):
        totaltime += tTimeData[course2[j]][course2[j+1]] + watchData[course2[j]]
        walktime += int(tTimeData[course2[j]][course2[j+1]])
        steps += stepData[course2[j]][course2[j+1]]
        metsFatigue += metsFatigueData[course2[j]][course2[j+1]]

    if totaltime[0] < timeLimit + int(timeLimit/10) and totaltime[0] > timeLimit - (int(timeLimit/10))*2:
        child2.append(totaltime[0])
        child2.append(walktime)
        child2.append(metsFatigue)
        child2.append(gen + 1)

        childB = copy.deepcopy(child2)
    else:
        childB = [[0],0,0,0,0]

        # childA = copy.deepcopy(child1)
        # childB = copy.deepcopy(child2)

    return type(ind1)(childA), type(ind1)(childB)



# 突然変異
def mutate(ind,gen): # [[61, 43, 42, 20] 560

    loot = 0
    if(len(ind[0]) > 3):
        loot = random.randint(0,1)  
    
    # 増加変異
    if(loot == 0):
        # 既にコース内に含まれている観光スポットを削除し，
        # 削除した中から追加するスポットを選択
        t = set(ind[0])^set(range(SPOT_NUM))
        print("t:",t)
        t.discard(SPOT_NUM)
        addSpot = random.choice(list(t))
        # 観光スポットを追加する場所を選択
        if len(ind[0]) > 1:
            addPoint = random.randint(1,len(ind[0]) - 1)
        else:
            addPoint = 1
        ind[0].insert(addPoint,addSpot)
        # print("増加変異")

    # 減少変異
    elif(loot == 1):
        t = set(ind[0])^set([SPOT_NUM]) 
        removeSpot = random.choice(list(t))
        ind[0].remove(removeSpot)
        # print("減少変異")
    
    time = 0
    totaltime = 0
    walktime = 0
    steps = 0

    metsFatigue = 0

    for j in range(len(ind[0]) - 1):
        totaltime += tTimeData[ind[0][j]][ind[0][j+1]] + watchData[ind[0][j]]
        walktime += int(tTimeData[ind[0][j]][ind[0][j+1]])
        steps += stepData[ind[0][j]][ind[0][j+1]]

        metsFatigue += metsFatigueData[ind[0][j]][ind[0][j+1]]
    # print("steps : ",steps)

    if totaltime[0] < timeLimit + int(timeLimit/10) and totaltime[0] > timeLimit - (int(timeLimit/10))*2:
        ind[1] = totaltime[0]
        ind[2] = walktime
        ind[3] = metsFatigue
        ind[4] = gen + 1
        return ind
    else:
        ind = [[0],0,0,0,0]
        return ind

    # ind[1] = totaltime[0]
    # ind[2] = walktime
    # ind[3] = gen + 1
    
    # return ind
