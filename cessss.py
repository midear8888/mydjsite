from matplotlib import pyplot as plt
import csv
import numpy as np
# 用来正常显示中文标签
plt.rcParams['font.sans-serif'] = ['SimHei']
# 用来正常显示负号
plt.rcParams['axes.unicode_minus'] = False

# 定义两个空列表存放x,y轴数据点
x = []
y = []
with open("b.csv", 'r') as f:
    plots = csv.reader(f, delimiter=',')
    # plots_length = np.array(list(plots)).shape[0]
    # print(plots_length)
    n = 20
    for row in plots:
        x.append(int(row[0]))
        y.append(int(row[1]))
    for i in range(2, len(x)):
        if x[i] == x[i-1]:
            x.remove(x[i])
            y.remove(y[i])
# 画折线图
print(x)
print(y)
# plt.scatter(x, y, 'or', linewidth=0, s=20, label='心电图')
plt.scatter(x, y, c='b', cmap='brg', s=3, alpha=0.2, marker='8')
plt.xlabel('时间t')
plt.ylabel('电压v')
plt.title('')
plt.legend()
plt.savefig('test30.jpg')
plt.show()
