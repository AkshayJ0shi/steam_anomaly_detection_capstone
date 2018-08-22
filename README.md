# ![Steam Logo](./images/steam20prct.png) Market Anomaly Detection
[__Summer 2018 Galvanize Data Science Immersive__](https://www.galvanize.com/austin)

[See the video](https://youtu.be/1V9y67HRVrE) overview of this project.

The presentation can be viewed in [Google Slides](https://docs.google.com/presentation/d/12XAat28ZXKdyjs9xiH4Vvo63eOOn7Ir9VesQmASp_0Y/edit?usp=sharing).

---

[Steam](https://store.steampowered.com/) is the largest digital video game distribution platform. A subset of games on Steam include items that can be found in-game and sold to other players on [Steam's Community Market](https://steamcommunity.com/market/). My hypothesis was that significant events in the community (new item releases, big updates, tournaments, etc.) would affect the prices of these items. My goal was to detect anomalies in the market and investigate those dates to see if they did in fact correspond to events.


# Data Gathering
<img src='images/workflow_data_gathering.png' height=80% width=80%>
I wanted to gather all of the price history data for every item on the Steam Market pages.
<details><summary>(Show/hide market page example)</summary>
<img src='images/market_example.png' height=80% width=80%>
</details>

In the source code I was able to find the API the price history graphs were drawing from. To gather this data systematically, I needed the ID of the game, and the name of the item for all 97,636 items I was after. I found a site [SteamApis](https://steamapis.com/) that had the names of every item for a given game. To get a list of every game that offered items on the Steam Market, I used BeautifulSoup to scrape a dropdown menu in the "Advanced Search" page of the market. With the list of every game, I was able to get a list of every item for each game from SteamAPIs, then use that list of every item to get price history records from Steam. As the price history data came in, I saved it to a MongoDB with the following schema:
```
 item_name: string
 game: number
 prices: list
     date: string
     median_sell_price: number
     quantity: string
```
Where 'prices' had a {date, median_sell_price, quantity} entry for each daily record. I transfered the data I'd gathered into Pandas and created a Pickle to easily load the DataFrame without having to query Mongo.

# Exploration
basic stats on items and games

After working with the data for a while, I learned that not all items were created equally. Some items had special properties (blue/red/green versions of the item) that were sold under the same name, for (sometimes) drastically different prices. I explored the economies of games and found that Counter Strike: Global Offensive had the third most items, but the most number of transaction and the highest total value over the past year of data. Counter Strike was not without the same issue, but those items were easily filtered out in this case. At this point I decided to just focus on Counter Strike.

# Features
There were many features I planned to use but did not have time to incorporate. They will be useful when I  future work.

The features I used most frequently were:
  * Item name / Description (concatenation of item name and release date)
  * Date of sale (Unix Time)
  * Date of sale (Timestamp)
  * Median sell price
  * Quantity
  * Estimated release date (by the first sale date for the item)
  * Days since release

### Datetimes
<img src='https://i.stack.imgur.com/uiXQd.png' height=75% width=75% ALIGN='right'>

Woof. There sure are a lot of different (and frustratingly incompatible) formats that dates can appear in.
  * String
  * Datetime
  * Timestamp
  * np.datetime64
  * Unix time (float)
  * DateTimeIndex
 
Some of these have underly timezones associated with them. Sometimes it's GMT and sometimes it's the local timezone. My data was stored in a different format than ARIMA took, which was a different format than the anomaly detection function took. I created [`date_util.py`](date_util.py) to help convert between them.

[figure source](https://stackoverflow.com/a/21916253)

# Analysis
<img src='images/workflow_analysis.png' height=80% width=80%>

### The Plan
My plan was to run some kind of anomaly detection on every item's time series, aggregate the results, and categorize every date as anomalous or normal. Before I went too far, I wanted to make sure items actually did follow common trends, or have common anomalies. 

### Clustering
<img src='images/clustered_items_scaled.png' height=80% width=80% ALIGN='right'>
I performed heirarchical clustering and looked at examples of items that were clustered tightly. As you can see in this example of three items (with standardized mean and standard deviation), their prices move similarly, and price changes that look anomalous appear in the same places.


### Anomaly Detection
Many anomaly detection methods only find one anomalous point or rely on knowing the number of anomalies. Largely they use mean and standard deviation to find anomalies, which is inherantly problematic if the time series has many because the mean and standard deviation are sensitive to outliers. Twitter developed an anomaly detection algorithm that replaces mean and standard deviation with median and Median Absolute Deviation. This allows the algorithm to function consistently despite the number or severity of outliers.
Twitter's Anomaly Detection was originally written in R and ported to Python by Nicolas Steven Miller. The Python port is called [pyculiarity](https://github.com/mosho-p/pyculiarity). It was originally written for Python 2.7 and was not 100% up to date with Python 3.6, so I forked it and made the minor changes necessary.

### Twitter didn't always work
The top graph is of a particularly bad example of the anomaly detection function in action. It failed to hit the big drop in price in the middle, and the sharp spike on the right.

<img src='images/detect_bad.png' height=80% width=80%>

[Pyramid]() is a Python port of a popular R function auto.arima. This allowed me to automatically fit the best ARIMA parameters to each time series, then run in-sample predictions. I used ARIMA for two reasons:
  1 Smooth each time series to avoid false positives
  2 Incorporate the `quantity` feature into the regression model

This is the same graph after it was fit with ARIMA:
<img src='images/detect_good.png' height=80% width=80%>

I gave each date an anomaly score which was the number of items tagged with anomalies on that date, divided by the number of items on the market on that day. This gave the percent of items tagged with anomalies for each day. To do broad investigations of dates, I had a list of dates that the collections of items were released on[1][2], dates of major tournaments[3], and a way to search the Counter Strike SubReddit by date range[4] to see if there were popular posts talking about big events. 

# Results
![](./images/results_graph.png)

I investigated 25 dates with the highest anomaly score, and found that many of them occured with the release of new items. When I varied the parameters of the anomaly detection function, or minimum price/quantity/days on the market thresholds, many of the top anomalous dates changes, except anomalies in late November 2016 and late May 2017 seemed to show up every time. The anomalies in May 2017 corresponded with the release of new items, but I want to look more into it to see why it would be more prevalent than other release dates. It is not immediately obvious why anomalies consistantly show up in late November 2016, but I want to investigate that further.

This kind of information is useful for companies who rely on revenue from these items to be able to plan based on their estimated income. Some games, like Team Fortress 2, are free-to-play and their revenue stream relies almost soley around these items.

# Future Work

---
# References
Twitter repo

Pyramid repo

Twitter papers

resources [1][2][3][4]
