import requests

#n=10
#print(n)
print("__name__:",__name__ )
print("__file__:",__file__ )
print("__doc__:",__doc__ )
print("__spec__ :",__spec__ )
print("__annotations__:",__annotations__ )
print("__builtins__:",__builtins__ )
print("__cached__:",__cached__ )
print("__import__ :",__import__ )
print("__debug__:",__debug__ )

def main(): 
    print("這裡是main function的命名空間")
    n=10
    print(n)

def rectangle_area(length, width):
    return length * width

if __name__ == "__main__":
    print("這是主程式")
    main()
    #pprint(n)
    #length = float(input("輸入長度: "))
    #width = float(input("輸入寬度: "))
    #area = rectangle_area(length, width)
    #print(f"矩形面積為: {area}")*/

