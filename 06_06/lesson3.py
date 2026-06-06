import requests
import pandas as pd


def main():
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # list[dict] -> DataFrame
        df = pd.DataFrame(data)

        # 顯示總筆數
        print(f"總筆數：{len(df)}")

        # 顯示前 10 筆（避免截斷）
        print(df.head(10))
        
        # 或者直接顯示全部
        # print(df)

    else:
        print("下載失敗")


if __name__ == '__main__':
    main()