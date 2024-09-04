import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI environments

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import os
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock1 = request.form['stockname']
        start_date = request.form['start']
        end_date = request.form['end']
        time_step = request.form['timestep']
        color1 = request.form['color1'].lower()
        stock2 = request.form.get('stockname2', None)
        color2 = request.form.get('color2', None)
        show_best_fit = 'bestfit' in request.form  # Check if the checkbox was selected

        # Attempt to parse start and end dates
        try:
            start_date_parsed = pd.to_datetime(start_date.strip())  # 'YYYY-MM-DD' format from date picker
            end_date_parsed = pd.to_datetime(end_date.strip())
            current_date = pd.to_datetime(datetime.now())  # Get the current date

            # Check if the start date is after the end date, and swap them if necessary
            if start_date_parsed > end_date_parsed:
                start_date_parsed, end_date_parsed = end_date_parsed, start_date_parsed
                flash("Start date was after the end date, so the dates have been swapped.")

            # Clip the end date to the current date if it's in the future
            if end_date_parsed > current_date:
                end_date_parsed = current_date
                flash(f"End date was after the current date and has been clipped to {current_date.strftime('%Y-%m-%d')}.")

            print(f"Parsed start date: {start_date_parsed}, Parsed end date: {end_date_parsed}")  # Debugging line
        except ValueError:
            flash("Invalid date format. Please use the date picker.")
            return redirect(url_for('index'))

        # Ensure the start and end dates are valid
        if pd.isna(start_date_parsed) or pd.isna(end_date_parsed):
            flash("Please enter valid start and end dates.")
            return redirect(url_for('index'))

        # Download stock1 data from yfinance
        data1 = yf.download(stock1, start=start_date_parsed, end=end_date_parsed)

        # Check if data1 has at least 2 points
        if len(data1) < 2:
            flash(f"Not enough data points to generate the graph for {stock1}. At least 2 data points are required.")
            return redirect(url_for('index'))

        # Resample data based on time_step
        if time_step == "1 week":
            data1 = data1.resample('W').ffill()  # Resample weekly

        # Download and process second stock data (if provided)
        data2 = None
        if stock2:
            data2 = yf.download(stock2, start=start_date_parsed, end=end_date_parsed)

            # Check if data2 has at least 2 points
            if len(data2) < 2:
                flash(f"Not enough data points to generate the graph for {stock2}. At least 2 data points are required.")
                return redirect(url_for('index'))

            if time_step == "1 week":
                data2 = data2.resample('W').ffill()  # Resample weekly

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 5))

        # Plot stock 1
        ax.plot(data1.index, data1['Close'], color=color1, label=stock1)

        # Add line of best fit for stock 1 if checkbox is selected
        if show_best_fit:
            x_values = np.arange(len(data1))  # Create a sequence of numbers as x-axis values
            y_values = data1['Close'].values

            # Check for NaN, Inf, or degenerate data
            if len(x_values) > 1 and len(np.unique(y_values)) > 1 and np.all(np.isfinite(y_values)):
                try:
                    coeffs = np.polyfit(x_values, y_values, 1)  # Linear regression (1st-degree polynomial)
                    best_fit_line = np.polyval(coeffs, x_values)  # Generate y-values for the line
                    ax.plot(data1.index, best_fit_line, color='orange', linestyle='--', label=f'{stock1} Best Fit')
                except np.linalg.LinAlgError:
                    flash(f"Could not generate a line of best fit for {stock1} due to data issues.")
            else:
                flash(f"Insufficient data to generate a best fit line for {stock1}.")

        # Plot stock 2 (if selected)
        if data2 is not None:
            ax.plot(data2.index, data2['Close'], color=color2, label=stock2)

            # Add line of best fit for stock 2 if checkbox is selected
            if show_best_fit:
                x_values2 = np.arange(len(data2))
                y_values2 = data2['Close'].values

                # Check for NaN, Inf, or degenerate data
                if len(x_values2) > 1 and len(np.unique(y_values2)) > 1 and np.all(np.isfinite(y_values2)):
                    try:
                        coeffs2 = np.polyfit(x_values2, y_values2, 1)
                        best_fit_line2 = np.polyval(coeffs2, x_values2)
                        ax.plot(data2.index, best_fit_line2, color='purple', linestyle='--', label=f'{stock2} Best Fit')
                    except np.linalg.LinAlgError:
                        flash(f"Could not generate a line of best fit for {stock2} due to data issues.")
                else:
                    flash(f"Insufficient data to generate a best fit line for {stock2}.")

        # Reduce axis text size by 25%
        ax.set_xlabel("Date", fontsize=9)
        ax.set_ylabel("Price", fontsize=9)

        # Reduce the tick label size for both axes
        ax.tick_params(axis='both', which='major', labelsize=9)

        # Add a grid to the plot
        ax.grid(True)

        # Add a legend
        ax.legend()

        # Set the title with default font size
        ax.set_title(f"Stock Prices from {start_date_parsed.strftime('%Y-%m-%d')} to {end_date_parsed.strftime('%Y-%m-%d')}")

        # Save the plot
        plot_path = os.path.join('static', 'plot.png')

        # Ensure the 'static' directory exists
        if not os.path.exists('static'):
            os.makedirs('static')

        fig.savefig(plot_path)
        plt.close(fig)  # Close the figure to free memory

        # Pass back the form data to retain in the form after submission
        return render_template('index.html',
                               start=start_date_parsed.strftime('%Y-%m-%d'),
                               end=end_date_parsed.strftime('%Y-%m-%d'),  # Send back clipped date if necessary
                               stockname=stock1,
                               stockname2=stock2,
                               color1=request.form['color1'],
                               color2=request.form.get('color2'),
                               time_step=time_step,
                               filename='plot.png',
                               bestfit_checked=show_best_fit)

    # Initial page load without form submission
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
