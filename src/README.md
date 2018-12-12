## [Anomaly Pipeline](anomaly_pipeline.py):
### The most recent update includes a complete pipeline from data gathering to results:
#### Database update:
  * First I gather a list of all the items that do not have fully up-to-date data.
    * (Data for the past 31 days is hourly and my data needs to be daily, so I cannot use those data points.)
  * I request from Steam the data for each of those items and update the database with the data between the most recent data 
  I have and the data from 32 days ago.
  * Since I check which items need updating before requesting any data, I can stop the script at any point without worrying
  about wasting time making redundant requests when I restart it.

_This step takes around 2 hours, and the only way I can think to speed it up is to make more accounts and make requests in parallel_

**Optimization attempts**:
  * Reduced number of queries to the largest table
  * Reduced number of times I connect to the database, although this only accounted for an estimated 1 min increase over all
  
#### Model fitting:
  * I take the data from my Postgres database and put it into a Pandas DataFrame to easily add features needed for my model.
  * Disregard timeseries that do not meet certain criteria:
    * Minimum quantity sold (variance is too high)
    * Minimum price threshold* (cannot detect negative anomalies)
  * Use auto-arima to smooth each timeseries. This helps the anomaly detection algorithm spot the general anomalies.
  * Run anomaly detection on each timeseries.
  * The results are combined, and for any given date I take the percent of items that had that date marked as anomalous.
  This gives me a sort of "anomaly factor" for each date.
  * Save the results to a pickle for ease of use. I currently also print the top 10 anomalous dates with their anomaly factors.

_This step currently takes 1-2 hours._

**Optimization attempts**:
  * Timed querying a subset of the database before importing to a DataFrame vs importing all into a DataFrame, then filtering. It appears querying once is faster.
  * Timed iterating through df.groupby('item_name') instead of iterating through the item names and masking as I went. The groupby was many times faster, but because the number of items was relatively low, the time gained from this was negligible compared to the time it took to fit the model.

*Minimum price threshold: the minimum price of an item is $0.03. $0.01 goes to the developers, $0.01 goes to the publisher,
and $0.01 goes to the seller. If an item sells for the minimum price, the price cannot fall, and negative anomalies would not
appear, so I disregard these items.
