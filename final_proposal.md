# Marshall Payne's Galvanize Capstone Project
## Steam Market Anomaly Detection
[Steam](https://store.steampowered.com/) is the largest digital video game distribution platform. A subset of games on Steam include items that can be found in-game and sold to other players on [Steam's Community Market](https://steamcommunity.com/market/). I am interested in finding anomolies in item prices that might indicate that some event occured. An extension of the project would be to automate a way to search news articles for events happening around the time the anomalies occured. I could then use similar future events as likely predictors of acute changes in item prices.

### How the problem was solved before:

With time series data, there will be seasonal and long term trends that need to be accounted for. ARIMA can be used to remove the trends, then outliers will appear. I found an auto-arima package called [pyramid](https://github.com/tgsmith61591/pyramid) and anomaly detection was solved by [Twitter](https://github.com/twitter/AnomalyDetection), but it only runs in R. Nicolas Steven Miller ported the Twitter anomaly detection from R to Python with [pyculiarity](https://github.com/nicolasmiller/pyculiarity), and I [forked it](https://github.com/mosho-p/pyculiarity) and made some minor changes to make it run on my machine.

### What's new about my approach and why it will be successful:

I haven't seen this problem applied to Steam. I think it's likely there will be changes in item prices that align with significant events in the gaming community. It seems like anomaly detection is primarily used to remove outliers to form more predictive models, whereas I will be using it to identify specific events that can be investigated.

### Who would this impact?

People who are involved in trading items on Steam would be interested to know how to predict changes in item prices. Valve (the owner of Steam) and game Developers get a cut of every item traded through the Steam Market, so they might also be interested in leveraging spikes in trade quantity. For example, releasing new items right before a large event if that causes people to get involved in trading, or avoiding releasing new items around the time of events if they would be missing out on potential profit by overlapping opportunities.

### Presentation:

I would love to do a web-app, and that could be an extension of my project, but I don't see myself having enough time to put one together that I'm proud of. I think it could be neat to create a Jupyter Notebook that gives a glimps of my work at each step of the project, especially if I can put together interactive graphs. I could be convinced to put together a powerpoint, but I am not a fan and would rather avoid if other options are just as good.

### Data I have a way to get:

  * Reviews per month for every game
  * Mean price and quantity sold per day for every item for every game
  * User-defined tags/categories for every game, with number of people who classified it that way

### How I plan to get the data:
I have links to API endpoint for the price/quantity of sold in-game items. I have piplines to scrape the store pages of games to get the tags that I can use to categorize games. I also have the link to the endpoint that Steam uses to graph the game's reviews over time. I plan to run EC2s to gather the data and house it in a MongoDB hosted on a different EC2. I still need to configure the EC2s to run scripts continuously, push the data to the MongoDB, and build in redundancy to avoid losing data.

### Estimated size of the dataset:
I collected ~70% of the Counter-strike: Global Offensive (CS:GO) item sales, and it came out to be ~7.5m entries. CS:GO is a game with one of the largest collections of items so this is one of the larger games in terms of data points, but I think the number of items I collected data from represents ~2% of the total items on the Steam Market, which would put a liberal estimate at ~375m data points for the Market item sales. Each game will also have ~20 tags/categories and \[number of positive reviews, number of negative reviews\] per month since the game was released associated with it.

### Potential Problems:

From what I've seen items generally trade for a much higher prices when they first come out, then they plateau. This could cause issues with anomaly detection. I also expect the dataset to be extremely inbalanced with some items trading houndred of thousands every day, while others are sold once a month.

### Next things to work on:
First and foremost I need to get data coming in. I think need to do research on anomaly detection and timeseries analysis. After that I plan to start doing some EDA to gather the simplest metrics.
