import matplotlib.pyplot as plt
import numpy as np
import math
import random
import time
from fractions import Fraction


class Map:
    roads_cost = {}
    roads_point = {}
    roads_every_cost = {}
    point_connection = {}

    def point(self, point_coordinate_x, point_coordinate_y, graph_number):
        self.point_connection[str(point_coordinate_x) + str(point_coordinate_y)] = graph_number  # 座標をkeyとして点と繋がっている道を格納

    def road(self, slope, intercept, max_x, min_x, graph_number):
        if type(max_x) == list:  # 傾きがy軸に平行な時（max_x, min_xに座標が格納されている時）
            max_x = max_x[0]  # xの最大値
            min_x = min_x[0]  # xの最小値
            max_x_y = max_x[1]  # xが最大の時のyの値
            min_x_y = min_x[1]  # xが最小の時のyの値
            self.roads_point["graph" + str(graph_number)] = [[max_x, max_x_y], [min_x, min_x_y]]  # 道の端の座標を辞書型で格納
            area_x = 0
            area_y = abs(max_x_y - min_x_y)  # yの範囲
            self.cost = area_y  # costはyの範囲

        else:
            y_coordinate = slope * np.arange(min_x, max_x, max_x - min_x) + intercept  # xが最小値から最大値までの範囲（整数値）の時のyの値のlist
            max_x_y = round(slope * max_x + intercept)  # xが最大値の時のyの値
            min_x_y = round(slope * min_x + intercept)  # xが最小値の時のyの値
            self.roads_point["graph" + str(graph_number)] = [[max_x, max_x_y], [min_x, min_x_y]]  # 道の端の座標を辞書型で格納
            area_x = max_x - min_x  # 正の整数
            area_y = max_x_y - min_x_y  # 正の整数
            if slope == 0:  # グラフがx軸に平行な時
                cost = area_x

            else:
                cost = math.sqrt(area_x ** 2 + area_y ** 2)

        final_cost = round(cost)  # 正の整数
        line_number = int(final_cost / 1)  # costを1で割った数（区間の数）
        self.roads_cost["graph" + str(graph_number)] = line_number

        # 1区間ごとのx, yの値を求める
        if type(max_x) == list:  # 傾きがy軸に平行な時（max_x, min_xに座標が格納されている時
            cost_x = 0
            cost_y = Fraction(max_x[1] - min_x[1], line_number)
        elif slope == 0:  # グラフがx軸に平行な時
            cost_x = Fraction(area_x, line_number)  # 1区間ごとのxのcost
            cost_y = 0  # 1区間ごとのyのcost
        else:
            cost_x = Fraction(area_x, line_number)  # 1区間ごとのxのcost
            cost_y = Fraction(area_y, line_number)  # 1区間ごとのyのcost

        self.roads_every_cost["graph" + str(graph_number)] = [cost_x, cost_y]  # 上の二つを辞書に格納

    def decide_point(self, now_point_x, now_point_y, former_graph):  # 今のx,y座標 + 一個前の道の番号
        # 進む道をrandomで決定しその道の番号を取得
        connection_road_number = self.point_connection[str(now_point_x) + str(now_point_y)]  # str型のkeyで行くことが可能な道をlistに入れる

        if former_graph != None:  # 最初でない時、前回通った道を除く
            if type(former_graph) == list:
                former_graph = int(str(former_graph).strip("[]"))
            connection_road_number.remove(former_graph)  # connection_road_numberのlistから前回通った道を除く
            nominee_road_number = connection_road_number
            connection_road_number.append(former_graph)  # removeしたものを戻す


        else:
            nominee_road_number = connection_road_number


        if len(nominee_road_number) >= 2:  # 行くことが可能な道が二つ以上あるときrandomで道を決める
            move_road = random.choice(nominee_road_number)

        else:
            move_road = nominee_road_number

        self.decided_road = move_road

    def moving_road(self, graph_number, now_point):
        apex = self.roads_point["graph" + str(graph_number).strip("[]")]  # 道の端の座標
        every_cost = self.roads_every_cost["graph" + str(graph_number).strip("[]")]  # 通るグラフのcost
        now_point_x = now_point[0]
        now_point_y = now_point[1]
        if now_point == apex[0]:  # xが最大の時
            for i in range(self.roads_cost["graph" + str(graph_number).strip("[]")]):
                now_point_x -= every_cost[0]  # x座標にcostを引く
                now_point_y -= every_cost[1]  # y座標にcostを引く
                time.sleep(1)
                print(now_point_x, now_point_y)
        elif now_point == apex[1]:  # xが最小の時
            for i in range(int(self.roads_cost["graph" + str(graph_number).strip("[]")])):
                now_point_x += every_cost[0]  # x座標からcostを足す
                now_point_y += every_cost[1]  # y座標からcostを足す
                time.sleep(1)
                print(now_point_x, now_point_y)


        now_point = [now_point_x, now_point_y]
        self.now_point = now_point  # 最終的な位置(list)
        self.former_graph = graph_number  # この動きで進んだ道

    def plot(self, slope, intercept, max_x, min_x):
        x_graph = np.arange(min_x, max_x, max_x - min_x)
        plt.plot(x_graph, slope * x_graph + intercept)


graph_data = [[0, 1, 6, 1],
              [2, -1, 5, 1],
              [-1.25, 15.25, 9, 5],
              [1, -5, 9, 6],
              [0.5, -0.5, 19, 9],
              [0, 9, 19, 5]]
point_data = [[1, 1, [0, 1]],
              [6, 1, [0, 3]],
              [5, 9, [1, 2, 5]],
              [9, 4, [2, 3, 4]],
              [19, 9, [4, 5]]
              ]
map = Map()
for index, i in enumerate(graph_data):
    map.road(i[0], i[1], i[2], i[3], index)

for index, i in enumerate(point_data):
    map.point(i[0], i[1], i[2])

# for i in graph_data:
#     map.plot(i[0], i[1], i[2], i[3])
# plt.show()

start_point_x = 1
start_point_y = 1
map.decide_point(start_point_x, start_point_y, None)
map.moving_road(map.decided_road, [start_point_x, start_point_y])
for i in range(10):
    map.decide_point(map.now_point[0], map.now_point[1], map.former_graph)
    map.moving_road(map.decided_road, map.now_point)