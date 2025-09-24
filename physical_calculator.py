# METs関連の計算をする
# 傾斜が1度増加するごとにMETsが0.24増加する(千住（紀要），長尾ら)
# 最終的に用いたいのは身体活動量：METs×時間(h)

# 移動ルートのデータ（高低差含む）を配列で受け取る (例：[[緯度，経度，高度], [緯度，経度，高度]，[緯度，経度，高度]])
# 受け取ったものを区切られた範囲で計算する

# 緯度，経度，高度から傾斜角度(°)を計算する
# 移動距離も計算する
# 一般的な歩行速度からかかる時間を計算する

import math  # 数学関数を使用するためのライブラリ
import numpy as np  # 数値計算を行うためのライブラリ
from geographiclib.geodesic import Geodesic # 緯度経度から距離を計算するためのライブラリ


sample_data = [[35.689533, 139.691733, 10],[35.669533, 139.661733, 300],[35.675533, 139.624733, 500]]  # 東京の例]


def calculate_METs(data): # dataは[[緯度，経度，高度], [緯度，経度，高度]，[緯度，経度，高度]]の形式

    for i in range(len(data) - 1):
        lat1, lon1, alt1 = data[i]
        lat2, lon2, alt2 = data[i + 1]

        # 緯度経度から距離を計算
        distance = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)['s12']
        # 高度差を計算
        height_diff = alt2 - alt1

        # ラジアンで角度計算
        angle_rad = math.atan(height_diff / distance)
        # 度数法に変換
        angle_deg = math.degrees(angle_rad)
        
        print("角度:", angle_deg, "°")
        print("距離:", distance, "m")
    # 緯度，経度，高度から
    return 0

calculate_METs(sample_data)
