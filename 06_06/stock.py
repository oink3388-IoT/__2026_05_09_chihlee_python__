from fugle_marketdata import RestClient

client = RestClient(api_key='ZDY0ZGYwYjItYTNhYS00YmVlLWIwZjAtYWI3MThmOGE2MWZhIGY3MjgwYzg4LWUyZWQtNGE1Mi1iYjZjLTU4ZWI0MGEwY2ZjNQ==')
stock = client.stock

# 獲取即時報價
quote = stock.intraday.ticker(symbol='2317')
print(quote)