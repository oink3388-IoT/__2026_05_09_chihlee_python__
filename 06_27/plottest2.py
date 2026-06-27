# 步驟 1:匯入 matplotlib.pyplot,取別名為 plt
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Heiti TC", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

# 步驟 2:建立飲料名稱的串列(奶茶、紅茶、綠茶、咖啡)
drinks = ["奶茶", "紅茶", "綠茶", "咖啡"]

# 步驟 3:建立各飲料銷售杯數的串列(50、25、35、40)
sales = [50, 25, 35, 40]

# 步驟 4:建立四種顏色的串列
colors = ["#FFD700", "#C0392B", "#27AE60", "#8B4513"]

# 步驟 5:建立 explode 串列,讓奶茶那一塊突出 0.2,其餘為 0
explode = (0.2, 0, 0, 0)

# 步驟 6:建立 figure
fig = plt.figure()

# 步驟 7:用 add_subplot() 建立 axes
ax = fig.add_subplot(111)

# 步驟 8:呼叫 axes.pie(),傳入杯數,並設定 labels、colors、explode、
#         startangle=90、shadow=True、autopct='%1.1f%%'
ax.pie(sales, labels=drinks, colors=colors, explode=explode,
       startangle=90, shadow=True, autopct="%1.1f%%")

# 步驟 9:用 plt.show() 顯示圖表
plt.show()
