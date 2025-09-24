# 処理時間が増えないようにあらかじめデータを保存するためのコード
import pandas as pd
import json
from move_fatigue_calculater import get_distance_and_angles, calculate_METs, get_routeCoord

# SPOT_NUM = 56

# # coordsData[i] = [lat, lon]
# # heightData[i] = [ele]
# coordsSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='座標取得')
# heightSheet = pd.read_excel('preExpData_fatigue.xlsx', sheet_name='高さの取得')

# coordsData = [coordsSheet.iloc[i,1:3].tolist() for i in range(SPOT_NUM+1)]
# heightData = [heightSheet.iloc[i,1:2].tolist() for i in range(SPOT_NUM+1)]

# route_df = pd.DataFrame(index=range(SPOT_NUM+1), columns=range(SPOT_NUM+1))
# for i in range(SPOT_NUM+1):
#     start_coord_for_call = coordsData[i]  # get_routeCoord に渡すのは lat/lon のみ
#     for j in range(SPOT_NUM+1):
#         if i == j:
#             route_df.iloc[i,j] = '[]'
#             continue
#         end_coord_for_call = coordsData[j]

#         try:
#             # 緯度経度のみでルート取得
#             route_coords = get_routeCoord(start_coord_for_call, end_coord_for_call)

#             # Excelには高度も追加して保存
#             # start: [lat, lon, ele], end: [lat, lon, ele] + 中間座標 lat/lon のみ
#             route_coords_with_ele = [
#                 [float(coord[0]), float(coord[1]), 0.0] for coord in route_coords
#             ]
#             # 始点と終点には実際の高度を付与
#             route_coords_with_ele[0][2] = float(heightData[i][0])
#             route_coords_with_ele[-1][2] = float(heightData[j][0])

#             route_df.iloc[i,j] = json.dumps(route_coords_with_ele)
#         except Exception as e:
#             print(f"Error calculating route {i}->{j}: {e}")
#             route_df.iloc[i,j] = '[]'

# # Excelに書き込み
# with pd.ExcelWriter('preExpData_fatigue.xlsx', mode='a', engine='openpyxl',
#                     if_sheet_exists='replace') as writer:
#     route_df.to_excel(writer, sheet_name='移動ルート', index=False, header=False, startrow=1, startcol=1)

# print("移動ルートの保存が完了しました。")

# 読み込む Excel ファイル
file_name = 'preExpData_fatigue.xlsx'

# スポット数（終着点含む）
SPOT_NUM = 56

# 移動ルートシートを読み込む
route_sheet = pd.read_excel(file_name, sheet_name='移動ルート', header=None, index_col=None)

# Excel 用の DataFrame を作成（ヘッダーはそのまま）
fatigue_df = pd.DataFrame(index=route_sheet.index, columns=route_sheet.columns)

# 各区間の METs 疲労度を計算
for i in range(SPOT_NUM+1):
    for j in range(SPOT_NUM+1):
        if i == j:
            fatigue_df.iloc[i,j] = 0  # 自身への移動は疲労なし
            continue

        try:
            cell_value = route_sheet.iloc[i+1, j+1]  # B2 から始まるので +1
            # 文字列でなければ空リスト扱い
            if isinstance(cell_value, str):
                route_coords = json.loads(cell_value)
            else:
                route_coords = []
            if not route_coords:  # 空リスト
                fatigue_df.iloc[i,j] = 0
                continue

            # 距離・角度データを取得
            distangle_data = get_distance_and_angles(route_coords)

            # METs 疲労を計算
            mets_fatigue = calculate_METs(distangle_data)
            fatigue_df.iloc[i,j] = mets_fatigue

        except Exception as e:
            print(f"Error calculating METs fatigue {i}->{j}: {e}")
            fatigue_df.iloc[i,j] = 0

# Excel に書き込み（B2 から）
with pd.ExcelWriter(file_name, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
    fatigue_df.to_excel(writer, sheet_name='METsを用いた移動による疲労', startrow=1, startcol=1, index=False, header=False)

print("METsによる移動疲労の保存が完了しました。")
