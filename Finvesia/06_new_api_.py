import requests

url = 'https://www.alphavantage.co/query'
params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': 'NSE:NIFTY50',
    'apikey': 'L2T23RHWZYCJ3357'
}

response = requests.get(url, params=params)

if response.ok:
    data = response.json()
    if 'Time Series (Daily)' in data:
        last_two_days = list(data['Time Series (Daily)'].keys())[:2]
        last_two_days_high = [float(data['Time Series (Daily)'][date]['2. high']) for date in last_two_days]
        last_two_days_low = [float(data['Time Series (Daily)'][date]['3. low']) for date in last_two_days]
        print('Last 2 days high:', last_two_days_high)
        print('Last 2 days low:', last_two_days_low)
    else:
        print('Daily time series data not found in response')
else:
    print('Error retrieving data:', response.status_code)

print(data)  # Print the full response for debugging purposes
