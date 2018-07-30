# Marshall Payne's Galvanize Capstone Project
[Steam](https://store.steampowered.com/) is the largest digital distribution platform for video games. A subset of games on Steam include items that can be found in-game and sold to other players on [Steam's Community Market](https://steamcommunity.com/market/). I am interested to find out if there are any patterns between the reviews of games and the price their items sell for.

(How was the problem solved before?)

(What is new about your approach, why do you think it will be successful?)

(Who cares?)
Developers and Steam. They both get a cut of the steam market, so items selling at higher prices or quantities means higher income.

(How will you present your work?)
I would love to do a web-app, and that could be an extension of my project, but I don't see myself having enough time to put one together that I'm proud of. I think it could be neat to create a Jupyter Notebook that gives a glimps of my work at each step of the project, especially if I can put together interactive graphs. I could be convinced to put together a powerpoint, but I am not a fan and would rather avoid of other options are just as good.

### Data I have a way to get:

  * Reviews per month for every game
  * Mean price and quantity sold per day for every item for every game
  * User-defined tags/categories for every game, with number of people who classified it that way

### How I plan to get the data:
I have links to API endpoint for the price/quantity of sold in-game items. I have piplines to scrape the store pages of games to get the tags that I can use to categorize games. I also have the link to the endpoint that Steam uses to graph the game's reviews over time. I plan to run EC2s to gather the data and house it in a MongoDB hosted on a different EC2. I still need to configure the EC2s to run scripts continuously, push the data to the MongoDB, and build in redundancy to avoid losing data.

### Estimated size of the dataset:
I collected ~70% of the Counter-strike: Global Offensive (CS:GO) item sales, and it came out to be ~7.5m entries. CS:GO a game with one of the largest collections of items so this is one of the larger games in terms of data points, but I think the number of items I collected data from represents ~2% of the total items on the Steam Market, which would put a liberal estimate at ~375m data points for the Market item sales. Each game will also have ~20 tags/categories and \[number of positive reviews, number of negative reviews\] per month since the game was released associated with it.

(Potential Problems?)

(Next thing to work on)
