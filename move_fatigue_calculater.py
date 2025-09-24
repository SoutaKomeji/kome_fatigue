import requests
import folium
import pandas as pd
from pyproj import Transformer
import elevation_service as elevation_service
import os
from openpyxl import load_workbook
from math import atan2, degrees

list1 = [41.773214, 140.726230]  # 函館駅
list2 = [41.765184, 140.709044]  # 旧函館区公会堂
# list3 = [41.772429, 140.753695]  # 啄木小公園
list3 = [41.791436, 140.736526]  # 亀田八幡宮
list4 = [41.770125, 140.712786] # 緑の島
list5 = [41.766896, 140.716813]  # 金森赤レンガ倉庫
# point_list =[
#     [41.773214, 140.726230],  # 函館駅
#     [41.765184, 140.709044],  # 旧函館区公会堂
#     [41.770125, 140.712786]   # 緑の島    
# ]
 
def get_routeCoord(list1, list2):
#     """
#     2つの地点の緯度経度を受け取り、OSRM APIを使ってルートの座標を取得する。
#     """  
    # OSRM APIを使ってルートの座標を取得(Docker)
    query_url = "http://172.28.148.142:5000/route/v1/driving/{},{};{},{}?steps=true".format(list1[1], list1[0], list2[1], list2[0]) 
    response = requests.get(query_url)
    result = response.json()

    # 高度を取るために必要なやつ(elevation_service.pyで定義)
    tif_path = f"{os.path.dirname(os.path.abspath(__file__))}/tool/tif_merged/merged_all.tif"
    elevation_service_ins = elevation_service.ElevationService(tif_path)

    route = result["routes"][0]
    legs = route["legs"][0]["steps"]
    list_locations = []

    for point in legs:
        for it in point["intersections"]:
            list_locations.append(it["location"][::-1])
    
    # 先頭に出発地、末尾に到着地を追加
    list_locations.insert(0, list1)  # 先頭にlist1
    list_locations.append(list2)     # 最後にlist2

    # 各地点の標高を取得して3次元リストに
    list_locations_with_elevation = []
    for lat, lon in list_locations:
        elevation = elevation_service_ins.get_elevation(lat, lon)
        list_locations_with_elevation.append([lat, lon, elevation])


    return list_locations_with_elevation

# print(get_routeCoord(list1, list2))


# def get_routeCoord(list_points):
#     """
#     複数の地点の緯度経度を受け取り、OSRM APIを使ってルートの座標を取得する。
#     """
#     all_routes_with_elevation = [] # 返す全区間のリスト

#     # 高度を取るために必要なやつ(elevation_service.pyで定義)
#     tif_path = f"{os.path.dirname(os.path.abspath(__file__))}/tool/tif_merged/merged_all.tif"
#     elevation_service_ins = elevation_service.ElevationService(tif_path)

#     # 各区間ごとに処理
#     for i in range(len(list_points)-1):
#         start = list_points[i]
#         end = list_points[i+1]

#         # OSRM APIを使ってルートの座標を取得(Docker)
#         query_url = "http://172.28.148.142:5000/route/v1/driving/{},{};{},{}?steps=true".format(start[1], start[0], end[1], end[0])
#         response = requests.get(query_url)
#         result = response.json()

#         route = result["routes"][0]
#         legs = route["legs"][0]["steps"]
#         list_locations = []

#         for point in legs:
#             for it in point["intersections"]:
#                 list_locations.append(it["location"][::-1])
        
#         # 先頭に出発地、末尾に到着地を追加
#         list_locations.insert(0, start)  # 先頭にstart
#         list_locations.append(end)     # 最後にend

#         # 各地点の標高を取得して3次元リストに
#         list_locations_with_elevation = []
#         for lat, lon in list_locations:
#             elevation = elevation_service_ins.get_elevation(lat, lon)
#             list_locations_with_elevation.append([lat, lon, elevation])

#         all_routes_with_elevation.append(list_locations_with_elevation)

#     return all_routes_with_elevation

# print(get_routeCoord(point_list))
# print(get_routeCoord(list1, list3))
# print(get_routeCoord(list1, list4))

def get_distance_and_angles(list_locations):
    """
    ルートの座標リストを受け取り、各地点間の距離と角度を計算する。
    """

    distances = []
    angles = []
    result = []
    
    distance_sum = 0

    for i in range(len(list_locations) - 1):
        lat1, lon1, ele1 = list_locations[i]
        lat2, lon2, ele2 = list_locations[i + 1]

        # 緯度経度から距離を計算
        transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
        x1, y1 = transformer.transform(lon1, lat1)
        x2, y2 = transformer.transform(lon2, lat2)

        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        elevation_diff = ele2 - ele1
        angle = degrees(atan2(elevation_diff, distance))

        result.append([distance, angle])
        distance_sum += distance
    
    # print(distance_sum)
    return result

# data = get_distance_and_angles(get_routeCoord(list1, list2))
# data = get_distance_and_angles(get_routeCoord(list1, list3))
# data = get_distance_and_angles(get_routeCoord(list1, list4))
data = get_distance_and_angles(get_routeCoord(list2, list5))
# print(data)

def calculate_METs(distangle_data):

    # """
    # ルートの距離角度を受け取り、METsを計算する。
    # """
    mets_sum = 0

    for i in range (len(distangle_data)):
        distance, angle = distangle_data[i]
        if angle < 0:
            angle = 0
        mets_fatigue = (3 + (0.24*angle)) * distance
        mets_sum += mets_fatigue
    
    return mets_sum

# print(calculate_METs(data)) # list1: 8949.129336230555  list4: 8642.511003601241



# def get_routeCoord(list1, list2):
#     """
#     2つの地点の緯度経度を受け取り、OSRM APIを使ってルートの座標を取得する。
#     """

#     query_url = "http://172.28.148.142:5000/route/v1/driving/{},{};{},{}?steps=true".format(list1[0], list1[1], list2[0], list2[1])
#     response = requests.get(query_url)
#     result = response.json()

#     route = result["routes"][0]
#     legs = route["legs"][0]["steps"]
#     list_locations = []

#     for point in legs:
#         for it in point["intersections"]:
#             list_locations.append(it["location"][::-1])

#     # 中間地点を計算
#     loc_mid = [
#         (list1[0] + list2[0]) / 2,
#         (list1[1] + list2[1]) / 2
#     ]

#     folium_map = folium.Map(location=loc_mid[::-1], zoom_start=14)
#     folium.Marker(location=list1[::-1], icon=folium.Icon(color='red')).add_to(folium_map)
#     folium.Marker(location=list2[::-1]).add_to(folium_map)
#     line = folium.vector_layers.PolyLine(locations=list_locations, color='black', weight=10)
#     line.add_to(folium_map)

#     # # 各交差点にピン（番号付き）
#     # for idx, loc in enumerate(list_locations):
#     #     folium.Marker(
#     #         location=loc,
#     #         icon=folium.Icon(color='blue', icon='info-sign'),
#     #         tooltip=f'交差点 {idx}'
#     #     ).add_to(folium_map)

#     #     # 番号ラベル（必要ならコメントアウトも可）
#     #     folium.map.Marker(
#     #         location=loc,
#     #         icon=folium.DivIcon(html=f'<div style="font-size: 10pt; color: black;">{idx}</div>')
#     #     ).add_to(folium_map)

#     #print(list_locations)
#     folium_map.save("map_sample.html")
#     return list_locations

# get_routeCoord(list1, list2)
