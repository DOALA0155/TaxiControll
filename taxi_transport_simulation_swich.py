import numpy as np
import math
import random
import time
from fractions import Fraction
import sys
import os
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.font as font
import RPi.GPIO as GPIO
GPIO.setmode(GIPO.BCM)
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

class Map:
    roads_cost = {}
    roads_point = {}
    roads_every_cost = {}
    point_connection = {}
    all_points = []
    all_apex = []

    edges = []

    def point(self, point_coordinate_x, point_coordinate_y, graph_number):
        self.point_connection[str(point_coordinate_x) + str(point_coordinate_y)] = graph_number  # 座標をkeyとして点と繋がっている道を格納

    def road(self, slope, intercept, max_x, min_x, graph_number):
        if type(max_x) == list:  # 傾きがy軸に平行な時（max_x, min_xに座標が格納されている時）
            max_x = max_x[0]  # xの最大値
            min_x = min_x[0]  # xの最小値
            max_x_y = max_x[1]  # xが最大の時のyの値
            min_x_y = min_x[1]  # xが最小の時のyの値
            if [max_x, max_x_y] not in self.all_apex:
                self.all_apex.append([max_x, max_x_y])
            if [min_x, min_x_y] not in self.all_apex:
                self.all_apex.append([min_x, min_x_y])
            self.roads_point["graph" + str(graph_number)] = [[max_x, max_x_y], [min_x, min_x_y]]  # 道の端の座標を辞書型で格納
            area_x = 0
            area_y = abs(max_x_y - min_x_y)  # yの範囲
            cost = area_y  # costはyの範囲


        else:
            y_coordinate = slope * np.arange(min_x, max_x, max_x - min_x) + intercept  # xが最小値から最大値までの範囲（整数値）の時のyの値のlist
            max_x_y = round(slope * max_x + intercept)  # xが最大値の時のyの値
            min_x_y = round(slope * min_x + intercept)  # xが最小値の時のyの値
            if [max_x, max_x_y] not in self.all_apex:
                self.all_apex.append([max_x, max_x_y])
            if [min_x, min_x_y] not in self.all_apex:
                self.all_apex.append([min_x, min_x_y])
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

        x = min_x
        y = min_x_y
        start_point = [[x, y], graph_number]
        points = []
        points.append(start_point)
        if start_point[0] not in self.all_points:
            self.all_points.append(start_point)


        # graph_numberをkeyとしてpoints（list）に格納
        for i in range(line_number):
            x += cost_x
            y += cost_y
            point = [[x, y], graph_number]
            points.append(point)
            self.all_points.append(point)
        x = []
        y = []
        for graph_points in self.all_points:
            graph_point = graph_points[0]
            x.append(graph_point[0])
            y.append(graph_point[1])

            plt.scatter(x, y, s=50, c="green")


        for i in range(line_number):
            edge = [points[i][0], points[i + 1][0]]
            plt.plot([points[i][0][0], points[i + 1][0][0]], [points[i][0][1], points[i + 1][0][1]], "-k")
            self.edges.append(edge)

    def decide_point(self, now_point_x, now_point_y, former_graph):  # 今のx,y座標 + 一個前の道の番号
        # 進む道をrandomで決定しその道の番号を取得
        print("ランダムで走行中です", now_point_x, now_point_y)
        connection_road = self.point_connection[str(now_point_x) + str(now_point_y)]  # str型のkeyで行くことが可能な道をlistに入れる
        connection_road_numbers = [connection_road]
        connection_road_number = connection_road_numbers[0]
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

        self.now_point = [now_point_x, now_point_y]
        self.decided_road = move_road

    def moving_road(self, graph_number, now_point, x, y):
        apex = self.roads_point["graph" + str(graph_number).strip("[]")]  # 道の端の座標
        every_cost = self.roads_every_cost["graph" + str(graph_number).strip("[]")]  # 通るグラフのcost
        now_point_x = now_point[0]
        now_point_y = now_point[1]
        if now_point == apex[0]:  # xが最大の時
            apex_passed = False
            for i in range(self.roads_cost["graph" + str(graph_number).strip("[]")]):
                # plt.scatter(x[self.all_points.index([now_point_x, now_point_y])], y[self.all_points.index([now_point_x, now_point_y], c="blue")])
                # plt.pause(.01)
                # plt.scatter(x[self.all_points.index([now_point_x, now_point_y])], y[self.all_points.index([now_point_x, now_point_y], c="red")])
                # plt.pause(.01)
                if apex_passed:
                    break
                now_point_x -= every_cost[0]  # x座標にcostを引く
                now_point_y -= every_cost[1]  # y座標にcostを引く
                time.sleep(1)
                print("ランダムで走行中です", now_point_x, now_point_y)
                
                if GPIO.input(14) == GPIO.HIGH:  # 20分の１の確率で客が乗車
                    price = 410  # priceを初期化
                    # self.all_pointsをall_pointに入れ直す
                    all_point = []
                    for point in self.all_points:
                        all_point.append(point[0])


                    all_point.remove([now_point_x, now_point_y])  # 全てのpointから客を乗せた場所を除く
                    for edge in self.edges:
                        if [now_point_x, now_point_y] in edge:
                            edge_index = edge.index([now_point_x, now_point_y])
                            if edge_index == 0:
                                print("removeされました")
                                all_point.remove(edge[1])
                            else:
                                print("removeされました")
                                all_point.remove(edge[0])
                    goal_point = random.choice(all_point)   # 目的地をrandomで選ぶ


                    passed = self.transport([now_point_x, now_point_y], goal_point)  # startを今のpointにしてgoalを上で選んだものにし最短距離を求める

                    passed.pop(0)  # 経路から最初のNoneを取り除く

                    for pass_point in passed:
                        if apex_passed:
                            break
                        time.sleep(1)
                        price += 60
                        print("お客さんを目的地まで運びます", pass_point[0], pass_point[1])
                        print("この地点までの料金は" + str(price) + "円です")



                        if pass_point == passed[-2]:  # 目的地の一つ前のpoint
                            passed_point = pass_point

                        elif pass_point == passed[-1]:  # 目的地に着いたとき
                            print("最終的な料金は" + str(price) + "円です")

                            while True:  # 道の端に来るまでループし続ける
                                if pass_point in self.all_apex:  # 今のpointが道も端に来たとき
                                    apex_passed = True


                                    for points in self.all_points:

                                        if passed[-2] == points[0]:
                                            graph_number = points[1]

                                            self.now_point = pass_point  # 最終的な位置(list)
                                            self.former_graph = graph_number  # この動きで進んだ道
                                    break

                                else:
                                    for edge in self.edges:  # 全ての辺
                                        if pass_point in edge:  # 今のpointを含む辺を探す
                                            if passed_point in edge:  # 一つ前に通った道を含む辺だったとき
                                                continue
                                            else:
                                                if edge.index(pass_point) == 0:
                                                    time.sleep(1)
                                                    pass_point = edge[1]
                                                    print("端に向かっています", pass_point[0], pass_point[1])
                                                    passed_point = edge[0]
                                                    break
                                                else:
                                                    time.sleep(1)
                                                    pass_point = edge[0]
                                                    print("端に向かっています", pass_point[0], pass_point[1])
                                                    passed_point = edge[1]
                                                    break

                else:
                    now_point = [now_point_x, now_point_y]
                    self.now_point = now_point  # 最終的な位置(list)
                    self.former_graph = graph_number  # この動きで進んだ道

        elif now_point == apex[1]:  # xが最小の時
            apex_passed = False
            for i in range(self.roads_cost["graph" + str(graph_number).strip("[]")]):
                if apex_passed:
                    break
                now_point_x += every_cost[0]  # x座標にcostを引く
                now_point_y += every_cost[1]  # y座標にcostを引く
                time.sleep(1)
                print("ランダムで走行中です", now_point_x, now_point_y)
                if GPIO.input(14) == GPIO.HIGH:  # 20分の１の確率で客が乗車
                    price = 410  # priceを初期化
                    # self.all_pointsをall_pointに入れ直す
                    all_point = []
                    for point in self.all_points:
                        all_point.append(point[0])

                    all_point.remove([now_point_x, now_point_y])  # 全てのpointから客を乗せた場所を除く
                    for edge in self.edges:
                        if [now_point_x, now_point_y] in edge:
                            edge_index = edge.index([now_point_x, now_point_y])
                            if edge_index == 0:
                                print("removeされました")
                                all_point.remove(edge[1])
                            else:
                                print("removeされました")
                                all_point.remove(edge[0])
                    goal_point = random.choice(all_point)  # 目的地をrandomで選ぶ

                    passed = self.transport([now_point_x, now_point_y],
                                            goal_point)  # startを今のpointにしてgoalを上で選んだものにし最短距離を求める

                    passed.pop(0)  # 経路から最初のNoneを取り除く

                    for pass_point in passed:
                        if apex_passed:
                            break
                        time.sleep(1)
                        price += 60
                        print("お客さんを目的地まで運びます", pass_point[0], pass_point[1])
                        print("この地点までの料金は" + str(price) + "円です")

                        if pass_point == passed[-2]:  # 目的地の一つ前のpoint
                            passed_point = pass_point

                        elif pass_point == passed[-1]:  # 目的地に着いたとき
                            print("最終的な料金は" + str(price) + "円です")
                            while True:  # 道の端に来るまでループし続ける
                                if pass_point in self.all_apex:  # 今のpointが道も端に来たとき
                                    apex_passed = True


                                    for points in self.all_points:
                                        if passed[-2] == points[0]:
                                            graph_number = points[1]

                                            self.now_point = pass_point  # 最終的な位置(list)
                                            self.former_graph = graph_number  # この動きで進んだ道
                                    break

                                else:
                                    for edge in self.edges:  # 全ての辺
                                        if pass_point in edge:  # 今のpointを含む辺を探す
                                            if passed_point in edge:  # 一つ前に通った道を含む辺だったとき
                                                continue
                                            else:
                                                if edge.index(pass_point) == 0:
                                                    time.sleep(1)
                                                    pass_point = edge[1]
                                                    print("端に向かっています", pass_point[0], pass_point[1])
                                                    passed_point = edge[0]
                                                    break
                                                else:
                                                    time.sleep(1)
                                                    pass_point = edge[0]
                                                    print("端に向かっています", pass_point[0], pass_point[1])
                                                    passed_point = edge[1]
                                                    break
                else:
                    now_point = [now_point_x, now_point_y]
                    self.now_point = now_point  # 最終的な位置(list)
                    self.former_graph = graph_number  # この動きで進んだ道


    def transport(self, start_point, goal_point):  # ベルマンフォード法で目的地までの最短距離を求める
        points = self.all_points
        transport_points = []

        # self.all_pointsをtransport_pointsに入れ直す
        for transport_point in points:
            transport_points.append(transport_point[0])

        transport_points.remove(start_point)  # 全てのpointからstart地点を除いたもの
        point_cost = {}  # 全てのpointへのcostを初期化するshokikasuru
        point_cost[str(start_point[0]), str(start_point[1])] = [0, [[None]]]  # start地点のcostは0

        # 全ての点のcostを無限にする
        for i in transport_points:
            point_cost[str(i[0]), str(i[1])] = [float("inf"), [[None]]]  # Noneは今まで通ってきた点（pass_point）

        all_cost = 0
        # costの合計をだす
        for i in range(len(graph_data)):
            line_number = self.roads_cost["graph" + str(i)]
            all_cost += line_number

        founded_points = [[start_point, None]]  # costが求まっているところのlist（costと今まで通った点）

        # ループを辺の数だけ繰り返す
        for i in range(len(self.edges)):
            temporary_founded_points = []
            #  それぞれの求まっているpointに処理
            for founded in founded_points:
                founded_point = founded[0]  # founded_pointはcostが求まっているpoint

                #  全ての辺に処理
                for edge_point in self.edges:
                    #  求まっているpointとつながっているedgeを出す
                    if founded_point in edge_point:  # 求まっている点を含む辺を探す


                        if founded[1] in edge_point:  # 前回通ったpointへのedgeの時は処理しない
                            continue
                        founded_index = edge_point.index(founded_point)  # 求まっている点のindexを取得


                        # [0] < [1]
                        if founded_index == 0:  # 求まっている点のindexが0ならば
                            point_not_found = edge_point[1]  # 求まっていない方のpointをpoint_not_foundとする
                            cost_not_found = point_cost[str(point_not_found[0]), str(point_not_found[1])]  # 更新するpointのcost

                            founded_cost = point_cost[str(founded_point[0]), str(founded_point[1])]  # 求まっているpointの反対側のcostに求まっているpoint＋１をする
                            new_cost = founded_cost[0]  # この計算で求められたcost
                            new_cost += 1

                            if cost_not_found[0] == float("inf") or cost_not_found[0] > new_cost:
                                passed_points = founded_cost[1]
                                pass_points = []
                                for passed_point in passed_points:
                                    if passed_point[0] == None:
                                        pass_point = [passed_point[0]]
                                        pass_points.append(pass_point)
                                    else:
                                        pass_point = [passed_point[0], passed_point[1]]
                                        pass_points.append(pass_point)

                                pass_points.append(founded_point)

                                point_cost[str(point_not_found[0]), str(point_not_found[1])] = [new_cost, pass_points]  # apex_pointまでのcostと一つ前のpointを格納

                            temporary_founded_points.append([point_not_found, founded_point])  # 次のループにおいて求まっていない方の点を求まっている点にする




                        elif founded_index == 1:
                            point_not_found = edge_point[0]
                            cost_not_found = point_cost[str(point_not_found[0]), str(point_not_found[1])]

                            founded_cost = point_cost[str(founded_point[0]), str(founded_point[1])]
                            new_cost = founded_cost[0]
                            new_cost += 1

                            if cost_not_found[0] == float("inf") or cost_not_found[0] > new_cost:
                                passed_points = founded_cost[1]
                                pass_points = []
                                for passed_point in passed_points:

                                    if passed_point[0] == None:
                                        pass_point = [passed_point[0]]
                                        pass_points.append(pass_point)
                                    else:
                                        pass_point = [passed_point[0], passed_point[1]]
                                        pass_points.append(pass_point)
                                pass_points.append(founded_point)

                                point_cost[str(point_not_found[0]), str(point_not_found[1])] = [new_cost, pass_points]  # apex_pointまでのcostと一つ前のpointを格納

                            temporary_founded_points.append([point_not_found, founded_point])  # 次のループにおいて求まっていない方の点を求まっている点にする

            # founded_points = []  # founded_pointを初期化
            founded_points = temporary_founded_points

        goal = point_cost[str(goal_point[0]), str(goal_point[1])]
        goal_cost = goal[0]
        passed = goal[1]

        print("cost", goal_cost)
        print("passed", passed)
        print("goal", goal_point[0], goal_point[1])
        return passed

root = tk.Tk()

price_font = font.Font(size=20)
type_font = font.Font(size=20)
price_label = tk.Label(root, text="料金", background="gray", width=30, height=2, font=price_font, fg="blue")
type_label = tk.Label(root, text="空車", background="gray", width=20, height=2, font=type_font, fg="orange")
price_label.pack(pady=30)
type_label.pack()
root.geometry("800x600")
root.mainloop()








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


# map.plot_graph(point_data)

x = []
y = []
for graph_points in map.all_points:
    graph_point = graph_points[0]
    x.append(graph_point[0])
    y.append(graph_point[1])

def move_map(start_point_x, start_point_y):

    plt.pause(0.1)
    map.decide_point(start_point_x, start_point_y, None)
    map.moving_road(map.decided_road, [start_point_x, start_point_y], x, y)

    while True:


        plt.scatter(x, y, s=50, c="blue")
        map.decide_point(map.now_point[0], map.now_point[1], map.former_graph)
        map.moving_road(map.decided_road, map.now_point, x, y)
        plt.pause(0.1)


move_map(19, 9)
GPIO.cleanup()
