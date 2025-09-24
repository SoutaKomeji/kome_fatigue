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
NOBJ = 5

K = 10
NDIM = NOBJ + K - 1
P = 2
H = factorial(NOBJ + P - 1) / (factorial(P) * factorial(NOBJ - 1))

# 制限時間
timeLimit = 60 * 4

# 各評価値の最大，最小値を測定
BOUND_LOW, BOUND_UP = [],[]


# 現在の目的関数(自然，歴史，身体的疲労，精神的疲労，移動による疲労)
maxList = [1.0,1.0,1.0,1.0,1.0]
minList = [0.0,0.0,0.0,0.0,1.0]

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

# Excelデータの読み込みを始める行番号を指定
row = 26

# Algorithm parameters
MU = 200 #int(H + (4 - H % 4))
CXPB = 90 # ％表記でお願いします
MUTPB = 10 # ％表記でお願いします
##

# 各リファレンスポイントに関連する解の個体数を把握するための変数
num_associate_rp = []

# １つのリファレンスポイントの評価値を保存する用の変数
record_evaluate_value = []

# 各世代の親個体，交叉した個体，変異した個体の個数を格納する
# 生存率の計算が機能しているか確認する用
ind_ratio = [0,0,0]


# 観光コース内のコースを回る順番を作成
# singleCourseDataでは初期解（１回目の観光ルート）を作成する
def singleCourseData(spotData, tTimeData, stepData, watchData, metsFatigueData, minSpotNum, maxSpotNum):

    # 生成された観光ルートが制限時間を超えている場合は再生成する
    route_flag = False

    nobj = len(spotData[0])
    while route_flag == False:
        spotNum = random.randint(minSpotNum, maxSpotNum)

        route = []
        # 出発地点の追加(函館駅を指定)
        route.append(56)

        # 全スポットから重複なしでランダムにスポットを選択する
        # range(x) は 0 から x-1 までの値を指す
        route.extend(random.sample(range(SPOT_NUM), k=spotNum))
        
        # 終着地点の追加(函館駅を指定)
        route.append(56)

        # トータルの観光時間と移動のみの時間，制限時間との差分を算出する
        totaltime = 0
        walktime = 0

        # metsによる疲労データをいれるもの
        metsFatigue = 0

        for j in range(len(route) - 1):
            totaltime += tTimeData[route[j]][route[j+1]] + watchData[route[j]]
            walktime += int(tTimeData[route[j]][route[j+1]])
            metsFatigue += metsFatigueData[route[j]][route[j+1]]

        if totaltime <= timeLimit + int(timeLimit/10) and totaltime >= timeLimit - (int(timeLimit/10)*2):
            route_flag = True

        # print("metsFatigue:", metsFatigue)
            

    routeData = []
    routeData.append(route)
    routeData.append(totaltime[0])
    routeData.append(walktime)
    routeData.append(metsFatigue)

    routeData.append(1) #　ここにはできた世代が入力される


    return routeData
    # routeDataの中身は以下の通り
    # routeData = [[出発地点, 観光地1, 観光地2, ..., 観光地n, 終着地点], トータルの観光時間, トータルの移動時間, metsを用いた移動による身体的疲労度, 0]

# コース評価用の関数
# ここでは5段階評価しているものだけを扱う

def evaluate(spotData, tTimeData, stepData, watchData, coordsData, heightData, metsFatigueData, inds):#参照しているのは単独の個体

    '''
    indに入っているもの
    ind[0]:訪れる観光スポットの番号のリスト
    ind[1]:トータルの時間
    ind[2]:移動飲みの時間
    ind[3]:metsを用いた移動による身体的疲労
    '''

    #休憩できているかどうか確認するフラグ
    phy_rest_flag = False
    men_rest_flag = False

    before_phy_fatigue = 0
    before_men_fatigue = 0

    timeLimit = 60 * 4

    nature = 0
    culture = 0
    phy_fatigue = 0
    men_fatigue = 0
    mets_fatigue = 0

    totaltime = 0
    walktime = 0
    subtime_score = 0
    walk_score = 0

    spare_minute = 0 # 理想時間よりも短い時間で回れた場合の分数
    additional_score = 0 # 分数をスコアに変換するための変数
    sub_limit_time = 0 # 制限時間との差分（分）を格納する変数
    sub_limit_penalty = 0 # 制限時間との差分をペナルティに変換するための変数

    ind = toolbox.clone(inds)

    for j in ind[0][1:-1]:
        nature += spotData[j][0] * spotData[j][8] #自然
        culture += spotData[j][2] * spotData[j][8] #文化

        before_phy_fatigue = phy_fatigue
        phy_fatigue += spotData[j][6] * spotData[j][8] #身体的疲労　小さい方が良い
        if phy_fatigue < 0:
            phy_fatigue = 0
        if before_phy_fatigue > 0 and spotData[j][6] < 0:
            phy_rest_flag = True
        
        before_men_fatigue = men_fatigue
        men_fatigue += spotData[j][7] * spotData[j][8] #精神的疲労　小さい方が良い
        if men_fatigue < 0:
            men_fatigue = 0
        if before_men_fatigue > 0 and spotData[j][7] < 0:
            men_rest_flag = True
    
    phy_fatigue += ind[2]
    
    # 出発地点と終着地点を省略
    totaltime = ind[1]
    walktime = ind[2]



    # METs * 距離に基づく身体的疲労度の計算及び追加
    spot_sequence = ind[0]

    for i in range(len(spot_sequence) - 1):
        start_idx = spot_sequence[i]
        end_idx = spot_sequence[i+1]
        mets_fatigue += metsFatigueData[start_idx][end_idx]

    # for i in range(len(spot_sequence) - 1):
    #     start_idx = spot_sequence[i]
    #     end_idx = spot_sequence[i + 1]

    #     # スポットの座標と高さを取得
    #     start_coord = [coordsData[start_idx][0], coordsData[start_idx][1]]
    #     end_coord = [coordsData[end_idx][0], coordsData[end_idx][1]]

    #     # ルート座標を取得
    #     route_coords = get_routeCoord(start_coord, end_coord)

    #     # 各地点間の距離と角度を計算
    #     distangle_data = get_distance_and_angles(route_coords)

    #     # METsによる身体的疲労度を計算
    #     mets_fatigue = calculate_METs(distangle_data)
    #     mets_fatigue_total += mets_fatigue

    #     # print(mets_fatigue_total)
    

    # 移動時間に関する制約(最小化)
    # important_information.txtの滞在時間参照

    # 理想の移動時間を求める
    if totaltime < 50:
        walk_score = 100 # 50分未満の場合は500点（短すぎるから（調整必要））
        ideal_walktime = 0 # 雑に決めてる　改善の余地あり
    else:
        ideal_walktime = int((40 * (totaltime - 45))/ 120) + 45

    walk_score = walktime - ideal_walktime # 移動時間と理想の移動時間の差分をスコアとする

    # 制限時間との制約
    # トータル観光時間と制限時間の差分を求める
    sub_limit_time = totaltime - timeLimit
    if sub_limit_time < 0:
        if sub_limit_time < (-1)*int(timeLimit/10):
            sub_limit_penalty = (-1)*sub_limit_time - int(timeLimit/10)
    else:
        sub_limit_penalty = sub_limit_time #　制限時間を超えている分だけペナルティ

    
    # 理想時間との差分をスコアに反映させる
    # walk_scoreが－⇒移動時間が理想よりも短いとき
    if walk_score < -10:
        spare_minute = (-1)*walk_score # 正の値に変換
        additional_score = int(spare_minute / 20) 
        # 最大化したいものには＋，最小化したいものには－をつける
        nature += additional_score 
        culture += additional_score
        phy_fatigue -= additional_score
        men_fatigue -= additional_score

        if phy_fatigue < 0:
            phy_fatigue = 0
        if men_fatigue < 0:
            men_fatigue = 0
        walk_score = 0

    elif walk_score > 0:
        spare_minute = walk_score
        # 最大化したいものにはー，最小化したいものには＋をつける
        additional_score = int(spare_minute / 5) # 0.2ずつ
        nature -= additional_score * 50
        culture -= additional_score * 50
        phy_fatigue += additional_score * 30
        men_fatigue += additional_score * 30

        if nature < 0:
            nature = 0
        if culture < 0:
            culture = 0
    
    # 制限時間とのペナルティをスコアに反映させる
    #　最大化したいものにはー，最小化したいものには＋をつける
    nature -= int(nature * sub_limit_penalty/10) 
    if nature < 0:
        nature = 0  
    
    culture -= int(culture * sub_limit_penalty/10)
    if culture < 0:
        culture = 0
    phy_fatigue += sub_limit_penalty * 30
    men_fatigue += sub_limit_penalty * 30

    if nature < 0:
        nature = 0
    if culture < 0:
        culture = 0   

    # print("time (ind[1]): ",time)
    # スポットの数
    num = len(ind[0]) - 2
    # print("walk_score: ", walk_score)
    # print("subtime_score: ", subtime_score)


    return nature, culture, phy_fatigue, men_fatigue, mets_fatigue


toolbox = base.Toolbox()