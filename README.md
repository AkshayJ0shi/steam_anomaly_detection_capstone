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

In the source code I was able to find the API the graphs were drawing from. To gather this data systematically, I needed the ID of the game, and the name of the item for all 97,636 items I was after. I found a site [SteamApis](https://steamapis.com/) that had the names of every item for a given game. To get a list of every game that offered items on the Steam Market, I used BeautifulSoup to scrape a dropdown menu in the "Advanced Search" page of the market. With the list of every game, I was able to get a list of every item for each game from SteamAPIs, then use that list of every item to get price history records from Steam. As the price history data came in, I saved it to a MongoDB with the following schema:
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
I performed heirarchical clustering and looked at examples of items that were clustered tightly. As you can see in this example of three items (with standardized mean and standard deviation), their prices move similarly, and price changes that look anomalous appear in the same places.

### Anomaly Detection
Many anomaly detection methods only find one anomalous point or rely on knowing the number of anomalies. Largely they use mean and standard deviation to find anomalies, which is inherantly problematic if the time series has many because the mean and standard deviation are sensitive to outliers. Twitter developed an anomaly detection algorithm that replaces mean and standard deviation with median and Median Absolute Deviation. This allows the algorithm to function consistently despite the number or severity of outliers.

Twitter didn't always work

I forked Pyramid and made slight changes that weren't caught when they moved from 2.7 to 3.6 to make it run on my machine. This allowed me to perform auto ARIMA to smooth each time series and incorporate the `quantity` feature.

I gave each date an anomaly score which was the number of items tagged with anomalies on that date, divided by the number of items on the market on that day. This gave the percent of items tagged with anomalies for each day. I had a list of dates that the collections of items were released on, dates of major tournaments, and a way to search Reddit by date range. I investigated 25 dates with the highest anomaly score, and found that many of them occured with the release of new items.

# Results
![](./images/results_graph.png)

This kind of information is useful for companies who rely on revenue from these items to be able to plan based on their estimated income. Some games, like Team Fortress 2, are free-to-play and their revenue stream relies almost soley around these items.

# Future Work

---
# References
Twitter repo

Pyramid repo
