# World of Warcraft Classic: Mists of Pandaria
[World of Warcraft Classic](https://en.wikipedia.org/wiki/World_of_Warcraft_Classic "World of Warcraft Classic") is a version of the original [World of Warcraft](https://worldofwarcraft.blizzard.com/en-us/ "World of Warcraft") (WoW) game that was re-released by [Blizzard Entertainment](https://www.blizzard.com/en-us/ "Blizzard Entertainment") to hopes of recreating the experience of the game as it was in its early days. Blizzard has released several versions of Classic, each reflecting a different era of WoW:
- Classic Era: Based on version 1.12 (original game).
- [The Burning Crusade](https://en.wikipedia.org/wiki/World_of_Warcraft:_The_Burning_Crusade "The Burning Crusade") Classic and [Wrath of the Lich King](https://en.wikipedia.org/wiki/World_of_Warcraft:_Wrath_of_the_Lich_King "Wrath of the Lich King") Classic: Followed as progression options.
- [Cataclysm](https://en.wikipedia.org/wiki/World_of_Warcraft:_Cataclysm "Cataclysm") Classic: Most recently launched, reintroducing the fourth expansion.
  
[Mists of Pandaria](https://en.wikipedia.org/wiki/World_of_Warcraft:_Mists_of_Pandaria "Mists of Pandaria") (MoP) is the up and coming expansion to WoW classic. MoP was WoW’s most distinct and stylistically bold expansion. It introduced a new playable race and class, a beautifully crafted continent, and a more introspective story. Though met with skepticism early on, it’s now remembered as one of the game’s most well-rounded and polished expansions.

Recently, the classic team at Blizzard has decided to give players early-access to this expansion through the use of a public beta. In this public beta players are asked to test out their ideas and provide feedback to Blizzard in hopes to provide a more polished full-access experience. These ideas are asked to be tested in PvP arenas and battle ground as well as the expansion's introductory raid, Mogushan Vaults.

# Overview
In this analysis, we will be looking into the raid data in hopes of gaining more insight into the characters being played. The data flow of this project is the following:

1. Gather raw data from the video game's most popular combat log analysis website, [WarcraftLogs](https://www.warcraftlogs.com "WarcraftLogs")
2. Transform the raw data into more digestable snippets that can be used for analysis
3. Visualize the data to aid in gathering insights; we will be using [Tableau](https://www.tableau.com/ "Tableau")
4. Gain meaningful and objective conclusions from the visualizations

### Important Keywords and Abbreviations
- <ins>**Class**</ins>: A permanent classification of a playable character. Each class is unique from one another and defines how you play the game.
- <ins>**Spec**</ins>: A specialization of a class that provides characters with special abilities and an inherant role.
- <ins>**Role**</ins>: A job that each player is "assigned" to complete while within group-focused gameplay.
- <ins>**Raid**</ins>: A group-focused zone within the game filled with unique non-playable characters (NPC), challenges, and rewards.
- <ins>**Boss**</ins>: A special and reward-dropping NPC within a raid whom is greater than the other NPCs within the raid.
- <ins>**Fight**</ins>: The encounter a group of players has with a boss that includes combat information.
- <ins>**DPS**</ins>: Damage per second. This is the primary metric used to generally measure the success of a damage dealer.

# Code
The first step of our analysis is to gather some data on the topic. Luckily, the WoW community has created a website (WarcraftLogs) that is used to house and display this information. Likely due to the fact that the current iteration of MoP classic is a beta version, the website has not completed any analysis/visualization of their own using this data. However, the data is still housed on their site and some of it is available for public use.

WarcraftLogs is seemingly setup to only allow data gathering through the use of their API. My initial attempts to collect data through Python's BeautifulSoup library resulted in me receiving error codes due to unauthorized access. Later on in the data collection phase I was able to extract some data from their website directly using the Seleniun library but implementing the use of their API would provide me with more consistent data as well as teach me more about a personally unexplored query language.

WarcraftLogs API uses GraphQL to handle their data. With the provided documentation I was able to submit requests and receive data in return. The files within this repository contain comments that gives the user more information. The following is a rundown of the process:

Step 1, receive access to their data through the use of a token:

```python
def get_access_token(client_id: str, client_secret: str) -> any:
    data = {'grant_type':'client_credentials'}
    auth = (client_id, client_secret)
    with requests.Session() as session:
        response = session.post(token_uri, data=data, auth=auth)
        if response.status_code == 200:
            return response
        print('Something went wrong...')
        return None
```

WarcraftLogs optionally provides all users with a client ID and a client secret. These are strings that are used to be sent to their API through the POST method in order to receive access to their data. Within this function, the client information is passed through and the user is either given the access token or nothing (depending on the response from the server). This token is then used throughout the rest of the code to authorize communication with WarcraftLogs. If the user does not receive an access token then none of the other functions within the code will work.

Step 2, request information from the server with the previously provided token as authorization:

```python
def get_information(token: dict, query: str, **kwargs) -> dict:
    headers = {'Authorization':f'Bearer {token['access_token']}'}
    data = {'query': query, 'variables': kwargs}
    with requests.Session() as session:
        session.headers = headers
        return session.get(public_url, json=data).json()
```

This function takes the token, a query, and any other information provided in a dictionary in order to complete the task. The token is stored in the GET method's headers and then the query and the other variables are stored within the json variable of the GET method.

Step 3, send a specific query to the server that provides us with information through the use of URL codes

```python
def get_fights_from_url_code(token: dict, code: str) -> list:
    query = '''query($code:String) {
                reportData{
                    report(code:$code){
                        fights(killType: Kills) {
                            id
                            startTime
                            endTime
                            name
                        }
                    }
                }
            }'''
    resp = get_information(token, query=query, code=code)
    fights = []
    for i in resp['data']['reportData']['report']['fights']:
        fights.append(i)
    return fights
```

For our analysis, we are accessing users' raid log data, targetting specific bosses within their raid log data, and extracting the character information within. The first part of this process is to access users' log data. WarcraftLogs stores these logs within a base url, which is then followed by a unique String of characters that corresponds to each log. This functions takes in the access token and a code variable that represents the URL code where a single log is being held. The query within this function is requesting information from the server the in the following order:
- Submit a base query with our provided code as a String typed variable.
- Access report data from the server.
- Access the specific report that corresponds to the initially provided code.
- Access the fights within the specific report that contains a boss kill; we are only analyzing data where a group of players successfully defeats a boss
- For each fight within the report, provide the ID, start time and end time of the fight, and the name of the boss that was defeated.

We then iterate through the returned log information and store each individual fight within a list. After all fights are iterated through, we return the list of fight information.
# Data Visualization
# Insights
