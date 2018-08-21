# ![Steam Logo](./images/steam20prct.png) Market Anomaly Detection
[Steam](https://store.steampowered.com/) is the largest digital video game distribution platform. A subset of games on Steam include items that can be found in-game and sold to other players on [Steam's Community Market](https://steamcommunity.com/market/). My hypothesis was that significant events in the community (new item releases, big updates, tournaments, etc.) would affect the prices of these items. My goal was to detect anomalies in the market and investigate those dates to see if they did in fact correspond to events.

[__Summer 2018 Galvanize Data Science Immersive__](https://www.galvanize.com/austin)

[See the video](https://youtu.be/1V9y67HRVrE) overview of this project.

The presentation can be viewed in [Google Slides](https://docs.google.com/presentation/d/12XAat28ZXKdyjs9xiH4Vvo63eOOn7Ir9VesQmASp_0Y/edit?usp=sharing).

# Data Gathering
<img src='images/workflow_data_gathering.png' height=80% width=80%>
I wanted to gather all of the price history data that the graphs on the Steam Market pages were drawing from.
<details><summary>(Show/hide example)</summary>
<p>
<img src='images/market_example.png' height=80% width=80%>
</p>
</details>

In the source code I found the API the graphs were drawing from. I used [SteamApis](https://steamapis.com/) to gather the names of every item they tracked on the Market, and fed them into the Steam API call to gather all of the price history data into a MongoDB. This gave me a database that looked like:
```
 item_name: string
 game: number
 prices: list
     date: string
     median_sell_price: number
     quantity: string
```
Where 'prices' had an entry for each daily record. 

# Anomaly Detection
<img src='images/workflow_analysis.png' height=80% width=80%>
