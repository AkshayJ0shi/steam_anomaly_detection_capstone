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

In the source code I found the API the graphs were drawing from. To gather this data systematically, I needed the ID of the game, and the name of the item for all 97,636 items I was after. I found a site [SteamApis](https://steamapis.com/) that had the names of every item for a given game. To get a list of every game that offered items on the Steam Market, I used BeautifulSoup to scrape a dropdown menu in the "Advanced Search" page of the market. With the list of every game, I was able to get a list of every item for each game from SteamAPIs, then use that list of every item to get price history records from Steam. As the price history data came in, I saved it to a MongoDB with the following schema:
```
 item_name: string
 game: number
 prices: list
     date: string
     median_sell_price: number
     quantity: string
```
Where 'prices' had a {date, median_sell_price, quantity} entry for each daily record. 

After working with the data for a while, I learned that not all items were created equally. Some items had special properties (maybe blue/red/green versions of the item) that were sold under the same name, for (sometimes) drastically different prices.

# Anomaly Detection
<img src='images/workflow_analysis.png' height=80% width=80%>
I brought the data I'd gathered into Pandas and created a Pickle to easily load the DataFrame without having to go through Mongo.
