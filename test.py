import tkinter as tk
import time

class test:
    def test1(self):
        price = 0
        root = tk.Tk()
        var = tk.StringVar()
        var.set(price)
        price_label = tk.Label(root, textvariable=var)
        price_label.pack()

        for i in range(1, 10):
            price += 60
            var.set(price)
            root.update_idletasks()

Test = test()
root = tk.Tk()
var = tk.StringVar()
Test.test1()

