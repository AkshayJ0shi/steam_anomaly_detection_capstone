## [Anomaly Pipeline](anomaly_pipeline.py):
### The most recent update includes a complete pipeline from data gathering to results:
#### Database update:
  * First I gather a list of all the items that do not have fully up-to-date data.
    * (Data for the past 31 days is hourly and my data needs to be daily, so I cannot use those data points.)
  * I request from Steam the data for each of those items and update the database with the data between the most recent data 
  I have and the data from 32 days ago.
  * Since I check which items need updating before requesting any data, I can stop the script at any point without worrying
  about wasting time making redundant requests when I restart it.

_This step takes maybe 2 hours, the only way I can think to speed it up is to make more accounts and make requests in parallel_

*Optimization attempts*:

  * Timed querying a subset of the database before importing to a DataFrame vs importing all into a DataFrame, then filtering
  * Reduced number of queries to the largest table
  * Reduced number of times I connect to the database, although this only accounted for about a 1 min increase
  
#### Model fitting:
  * I take the data from my Postgres database and put it into a Pandas DataFrame to easily add features needed for my model,
  and change column names.
  * Disregard timeseries that do not meet certain criteria:
    * Minimum quantity sold (variance is too high)
    * Minimum price threshold* (cannot detect negative anomalies)
  * Use auto-arima to smooth each timeseries. This helps the anomaly detection algorithm spot the larger anomalies.
  * Run anomaly detection on each timeseries.
  * The results are combined, and for any given date I take the percent of items that had that date marked as anomalous.
  This gives me a sort of "anomaly factor" for each date.
  * Save the results to a pickle for ease of use.

_I want to save the ARIMA models. auto-arima fits each timeseries with several ARIMA predictions to find the one that fits best. This is time consuming and likely unnecessary to refit if I updated the data recently.
I also currently do not have a way to save progress if there's an error or keyboard interruption,
which is something I would like to add. This step takes 1-2 hours._

*Minimum price threshold: the minimum price of an item is $0.03. $0.01 goes to the developers, $0.01 goes to the publisher,
and $0.01 goes to the seller. If an item sells for the minimum price, the price cannot fall, and negative anomalies would not
appear, so I disregard these items.

<br>

I now have a full pipeline from data gathering to results.
