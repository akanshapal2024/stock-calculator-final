# Stock Price Visualization and Backup Solution

This document outlines the implementation of a Flask web application for visualizing stock prices using the Yahoo Finance API. Additionally, it describes a backup solution using the Alpha Vantage API in case the primary data source becomes unavailable.

## 1. Main Application Implementation

The main application is built using Flask, a lightweight web framework for Python. The application allows users to input a stock symbol, a date range, a time step for resampling data, and a color for the plot. It then fetches the stock data from Yahoo Finance, processes it, and displays a plot of the stock's closing prices.

### Key Components

1. **Flask Setup**:

   - The Flask application is initialized and configured with a secret key required for using flash messages.
   - The route `/` is set up to handle both GET and POST requests.
2. **Form Handling**:

   - The form captures user inputs including the stock symbol, start and end dates, time step, and color for the plot.
   - Input dates are parsed using `pandas` to ensure they are in the correct format (`DD/MM/YYYY`).
3. **Data Fetching**:

   - The application uses the `yfinance` library to download stock data based on the user's inputs. This data includes daily stock prices over the specified date range.
4. **Data Resampling**:

   - The stock data can be resampled based on the user's selected time step (e.g., 1 hour, 1 week) to adjust the granularity of the data shown in the plot.
5. **Plotting**:

   - A plot of the stock's closing prices is created using `matplotlib`. The plot is customized based on the user's input, including the line color.
   - The plot is saved to the `static` directory and then displayed on the web page.
6. **Error Handling**:

   - Flash messages are used to notify the user of any errors, such as invalid date formats or missing data.

### Code Snippet

```python
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI environments

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock = request.form['stockname']

        # Attempt to parse start and end dates
        try:
            start_date = pd.to_datetime(request.form['start'].strip(), format="%d/%m/%Y")
            end_date = pd.to_datetime(request.form['end'].strip(), format="%d/%m/%Y")
        except ValueError:
            flash("Invalid date format. Please use DD/MM/YYYY.")
            return redirect(url_for('index'))

        time_step = request.form['timestep']
        color = request.form['color'].lower()

        # Download stock data
        data = yf.download(stock, start=start_date, end=end_date)

        # Resample data based on time_step
        if time_step == "1 hour":
            data = data.resample('H').ffill()
        elif time_step == "1 week":
            data = data.resample('W').ffill()

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data.index, data['Close'], color=color)
        ax.set_title(f"{stock} Price from {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")

        # Save the plot
        plot_path = os.path.join('static', 'plot.png')

        # Ensure the 'static' directory exists
        if not os.path.exists('static'):
            os.makedirs('static')

        fig.savefig(plot_path)
        plt.close(fig)  # Close the figure to free memory

        return redirect(url_for('index', filename='plot.png'))

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
```


## 2. Backup Solution

In case the Yahoo Finance API becomes unavailable, we have implemented a backup solution using the Alpha Vantage API. This backup solution allows us to fetch stock data in a similar format. However, due to licensing and pricing it is only a backup strategy as real time data have to be fetched only with premium subscription.

### Backup Strategy

* **Fetching Data** : The Alpha Vantage API is used to fetch intraday stock prices. A request is made to the API endpoint, and the JSON response is processed.
* **Data Processing** : A function `get_high_low_prices` is provided to extract high and low prices within a specified date range from the JSON data returned by Alpha Vantage.
* **Error Handling** : The solution checks for valid dates and properly formats them for API requests.



### Backup Code Snippet


```python
from datetime import datetime
import json
import requests

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

# Example usage of Alpha Vantage API
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=15min&apikey=YOUR_API_KEY'
r = requests.get(url)
data = r.json()

# Save the JSON data to a file for backup purposes
file_path = 'test_data.json'
with open(file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

```
