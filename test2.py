import matplotlib.pyplot as plt
import time
x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y2 = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

while True:
    plt.scatter(x, y1, c="red")
    plt.pause(.01)
    for i in range(len(x)):

        time.sleep(1)
        plt.scatter(x[i], y1[i], c="blue")
        plt.pause(.01)
        time.sleep(1)
        plt.scatter(x[i], y1[i], c="red")