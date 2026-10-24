# ReStock CSV Demand Forecaster

## What it does

The Demand Forecast tab now accepts a CSV containing historical daily demand/sales. It forecasts the next 7 or 30 days and lets you download the results as a CSV.

## CSV format

A header row is required. The file should have:
- one date column (for example `Date`)
- one numeric demand column (for example `Units_Sold`, `Demand`, `Quantity`, or `Sales`)

One row per date is recommended. Multiple rows on the same date are summed. The app attempts to identify date and demand columns automatically, and you can change the selections after loading the file. Dates should be in a standard format such as `YYYY-MM-DD`.

Use **Download sample CSV** inside the app to download an example file.

## How to use

1. Start ReStock as usual from this folder.
2. Open **Demand forecast**.
3. Upload your CSV.
4. Check the detected Date and Demand columns.
5. Choose 7 days or 30 days.
6. Keep **Auto-select** or choose a forecasting method.
7. Click **Generate forecast**.
8. Click **Download forecast CSV** to export the prediction.

## Forecast methods

- **Auto-select:** compares candidate methods on a recent holdout window using mean absolute error (MAE), then chooses the lowest-error method.
- **Weekly seasonal naive:** predicts each day using demand from the same weekday one week earlier.
- **7-day moving average:** uses the recent seven-day average.
- **Linear trend:** extrapolates a fitted linear trend from up to the most recent 90 days.
- **Last observed value:** repeats the last observed demand.

The forecast range is a simple approximate interval based on holdout MAE and forecast magnitude. It is not a statistically calibrated prediction interval.

## Important assumptions and limits

- The model expects daily demand data. It aggregates multiple rows on the same date by summing demand.
- Missing calendar dates are filled with zero. If a missing date means the data is absent rather than actual zero sales, correct the source data before forecasting.
- The model cannot automatically account for promotions, holidays, prices, stockouts, weather or product assortment changes unless their effects are already reflected in the history. This version does not use external data or a trained deep-learning model.
- Results are estimates for planning support, not guarantees. Validate them against a holdout period and business context before acting.
- CSV processing is performed locally in the browser; the uploaded CSV is not sent to an external AI service.
