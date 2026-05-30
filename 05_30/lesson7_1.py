try:
	with open("student.txt", "r", encoding="utf-8") as file:
			data = file.read()
			print(data)
except Exception as e:
	print("發生錯誤:", e)
	
#===============

# open(file="student.txt") 引數名稱的呼叫

try:
	with open(file="student.txt") as file:
			data = file.read()
			print(data)
except Exception as e:
	print("發生錯誤:", e)


#=====================
# open("student.txt") 引數值的呼叫,必需依順序

try:
	with open("student.txt",'r',-1,'utf-8') as file:
			data = file.read()
			print(data)
except Exception as e:
	print("發生錯誤:", e)


#===================

# open(file="student.txt") 引數名稱的呼叫,可以不依順序,只要依照名

try:
	with open(file="student.txt",encoding="utf-8") as file:
			data = file.read()
			print(data)
except Exception as e:
	print("發生錯誤:", e)


#=================

# open(file="student.txt") 混合的呼叫,可以不依順序,只要依照名

try:
	with open("student.txt",encoding="utf-8",mode="r") as file:
			data = file.read()
			print(data)
except Exception as e:
	print("發生錯誤:", e)

