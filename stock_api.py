from datetime import datetime
import json
import requests

# # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
# url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=WFRZUL8P3JFVC9GG'
# r = requests.get(url)
# data = r.json()

# print(data)



def get_high_low_prices(data, start_date, end_date):
    """
    Extracts the highest and lowest prices for each day within a specified date range.

    :param data: JSON data from Alpha Vantage API containing time series information.
    :param start_date: The start date in 'YYYY-MM-DD' format.
    :param end_date: The end date in 'YYYY-MM-DD' format.
    :return: A tuple containing two lists: (list of lowest prices, list of highest prices).
    """
    # Convert the start and end dates to datetime objects
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Initialize lists to store high and low prices
    low_prices = []
    high_prices = []

    # Access the time series data
    time_series = data.get("Time Series (Daily)", {})

    # Iterate through the dates in the time series
    for date_str, daily_data in time_series.items():
        # Convert the current date string to a datetime object
        current_dt = datetime.strptime(date_str, '%Y-%m-%d')

        # Check if the current date is within the specified range
        if start_dt <= current_dt <= end_dt:
            # Extract the high and low prices and append to the respective lists
            low_price = float(daily_data.get("3. low"))
            high_price = float(daily_data.get("2. high"))
            low_prices.append(low_price)
            high_prices.append(high_price)

    return low_prices, high_prices

# # Example usage
# url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=WFRZUL8P3JFVC9GG'
# r = requests.get(url)
# data = r.json()

# # Load JSON data from a file
# file_path = 'test_api_request.json'

# with open(file_path, 'r') as file:
#     data = json.load(file)

# start_date = '2024-08-28'
# end_date = '2024-09-02'
# low_prices, high_prices = get_high_low_prices(data, start_date, end_date)

# print("Low Prices:", low_prices)
# print("High Prices:", high_prices)




url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=15min&apikey=WFRZUL8P3JFVC9GG'
r = requests.get(url)
# Get the JSON response
data = r.json()

# Define the path where you want to save the JSON file
file_path = 'test_data.json'

# Save the JSON data to a file
with open(file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)