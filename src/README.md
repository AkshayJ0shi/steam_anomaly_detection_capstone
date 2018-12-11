## AnomalyPipeline:
### The most recent update includes a complete pipeline from data gathering to results:
#### Database update:
  * First I gather a list of all the items that do not have fully up-to-date data.
    * (Data for the past 31 days is hourly and my data needs to be daily, so I cannot use those data points.)
  * I request from Steam the data for each of those items and update the database with the data between the most recent data 
  I have and the data from 32 days ago.
  * Since I check which items need updating before requesting any data, I can stop the script at any point without worrying
  about wasting time making requests I don't need.

_This step takes quite a while, the only way I can think to speed it up is to make more accounts and make requests in parallel_
  
#### DataFrame update: _UNFINISHED_
Now that my database has been updated, the pipeline moves to update the Dataframe that I use for my model.
  * This involves adding the new datapoints to the dataframe and applying any feature engineering I've done
  * The out-of-date pickle file is overwritten with the new one.
  
#### Model fitting: _UNFINISHED_
  * Disregard timeseries that do not meet certain criteria:
    * Minimum quantity sold (variance is too high)
    * Minimum price threshold* (cannot detect negative anomalies)
  * Use auto-arima to smooth each timeseries. This helps the anomaly detection algorithm spot the larger anomalies.
  * Run anomaly detection on each timeseries.
  * The results are combined, and for any given date I take the percent of items that had that date marked as anomalous.
  This gives me a sort of "anomaly factor" for each date.
  * Save the results.

_I want to save the ARIMA models. auto-arima fits each timeseries with several ARIMA predictions to find the one that fits best.
This is time consuming and likely unnecessary to refit if I updated the data recently._

*Minimum price threshold: the minimum price of an item is $0.03. $0.01 goes to the developers, $0.01 goes to the publisher,
and $0.01 goes to the seller. If an item sells for the minimum price, the price cannot fall, and negative anomalies would not
appear, so I disregard these items.

<br>

I now have a full pipeline from data gathering to results.
