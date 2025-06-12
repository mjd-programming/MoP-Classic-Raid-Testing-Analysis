# World of Warcraft Classic: Mists of Pandaria
[World of Warcraft Classic](https://en.wikipedia.org/wiki/World_of_Warcraft_Classic "World of Warcraft Classic") is a version of the original [World of Warcraft](https://worldofwarcraft.blizzard.com/en-us/ "World of Warcraft") (WoW) game that was re-released by [Blizzard Entertainment](https://www.blizzard.com/en-us/ "Blizzard Entertainment") to hopes of recreating the experience of the game as it was in its early days. Blizzard has released several versions of Classic, each reflecting a different era of WoW:
- Classic Era: Based on version 1.12 (original game).
- [The Burning Crusade](https://en.wikipedia.org/wiki/World_of_Warcraft:_The_Burning_Crusade "The Burning Crusade") Classic and [Wrath of the Lich King](https://en.wikipedia.org/wiki/World_of_Warcraft:_Wrath_of_the_Lich_King "Wrath of the Lich King") Classic: Followed as progression options.
- [Cataclysm](https://en.wikipedia.org/wiki/World_of_Warcraft:_Cataclysm "Cataclysm") Classic: Most recently launched, reintroducing the fourth expansion.
  
[Mists of Pandaria](https://en.wikipedia.org/wiki/World_of_Warcraft:_Mists_of_Pandaria "Mists of Pandaria") (MoP) is the up and coming expansion to WoW classic. MoP was WoW’s most distinct and stylistically bold expansion. It introduced a new playable race and class, a beautifully crafted continent, and a more introspective story. Though met with skepticism early on, it’s now remembered as one of the game’s most well-rounded and polished expansions.

Recently, the classic team at Blizzard has decided to give players early-access to this expansion through the use of a public beta. In this public beta players are asked to test out their ideas and provide feedback to Blizzard in hopes to provide a more polished full-access experience. These ideas are asked to be tested in PvP arenas and battle ground as well as the expansion's introductory raid, Mogushan Vaults.

# Overview
In this analysis, we will be looking into the raid data in hopes of gaining more insight into the characters being played. With this insight, we can save time by choosing which character we play based on a number of factors. The data flow of this project is the following:

1. Gather raw data from the video game's most popular combat log analysis website, [WarcraftLogs](https://www.warcraftlogs.com "WarcraftLogs")
2. Transform the raw data into more digestable snippets that can be used for analysis
3. Visualize the data to aid in gathering insights; we will be using [Tableau](https://www.tableau.com/ "Tableau")
4. Gain meaningful and objective conclusions from the visualizations

### Important Keywords and Abbreviations
- <ins>**Class**</ins>: A permanent classification of a playable character. Each class is unique from one another and defines how you play the game.
- <ins>**Spec**</ins>: A specialization of a class that provides characters with special abilities and an inherant role.
- <ins>**(Spec)(Class)**</ins>: This is the primary way that a character is referred to; the specialization followed by the class.
- <ins>**Role**</ins>: A job that each player is "assigned" to complete while within group-focused gameplay.
- <ins>**Raid**</ins>: A group-focused zone within the game filled with unique non-playable characters (NPC), challenges, and rewards.
- <ins>**Boss**</ins>: A special and reward-dropping NPC within a raid whom is greater than the other NPCs within the raid.
- <ins>**Fight**</ins>: The encounter a group of players has with a boss that includes combat information.
- <ins>**DPS**</ins>: Damage per second. This is the primary metric used to generally measure the success of a damage dealer. This can also be used to describe the damage dealer role.
- <ins>**Tank**</ins>: A role in which the player is assigned to mitigate boss attacks and control the pace of the fight.
- <ins>**Item Level**</ins>: A metric used to show how powerful a specific character's items are. This can also be viewed as a correlating number to a character's damage; higher item level results in higher damage.

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

Step 4a, create a dictionary of specializations and corresponding abilities that can be used to "define" said spec:

```python
def get_spec_from_abilities(abilities: str) -> str:
    specs = {
        'Affliction Warlock':['Unstable Affliction', 'Agony', 'Corruption'],
        'Destruction Warlock':['Incinerate', 'Immolate', 'Chaos Bolt'],
        'Beastmaster Hunter':['Kill Command', 'Cobra Shot', 'Dire Beast'],
        'Fire Mage':['Pyroblast', 'Combustion', 'Ignite'],
        'Arcane Mage':['Arcane Blast', 'Arcane Missiles', 'Arcane Barrage'],
        'Survival Hunter':['Explosive Shot', 'Serpent Sting', 'Black Arrow'],
        'Feral Druid':['Shred', 'Rip', 'Ferocious Bite'],
        'Enhancement Shaman':['Stormstrike', 'Lava Lash'],
        'Shadow Priest':['Mind Blast', 'Devouring Plague', 'Mind Flay'],
        'Demonology Warlock':['Doom', 'Immolation Aura', 'Hand of Guldan'],
        'Frost DeathKnight':['Obliterate', 'Howling Blast', 'Frost Strike'],
        'Assassination Rogue':['Mutilate', 'Envenom', 'Dispatch'],
        'Balance Druid':['Starsurge', 'Moonfire', 'Sunfire'],
        'Subtlety Rogue':['Hemorrhage', 'Backstab', 'Ambush'],
        'Windwalker Monk':['Fists of Fury', 'Rising Sun Kick'],
        'Retribution Paladin':["Templar's Verdict", 'Execution Sentence', 'Divine Storm'],
        'Arms Warrior':['Mortal Strike', 'Overpower', 'Sweeping Strikes'],
        'Elemental Shaman':['Lava Burst'],
        'Combat Rogue':['Sinister Strike', 'Revealing Strike', 'Main Gauche', 'Blade Flurry'],
        'Fury Warrior':['Bloodthirst', 'Wild Strike'],
        'Frost Mage':['Frostbolt', 'Frostfire Bolt', 'Ice Lance'],
        'Marksmanship Hunter':['Chimera Shot', 'Aimed Shot'],
        'Blood DeathKnight':['Death Strike', 'Heart Strike', 'Blood Boil'],
        'Unholy DeathKnight':['Festering Strike', 'Scourge Strike'],
        'Brewmaster Monk':['Keg Smash'],
        'Protection Warrior':['Shield Slam'],
        'Protection Paladin':['Shield of the Righteous'],
        'Guardian Druid':['Maul', 'Pulverize']
    }
    for ability in abilities:
        for spec in specs:
            if ability in specs[spec]:
                return spec
    return ''
```

This helper function takes in a list of ability names and returns the corresponding specialization that an ability is linked to. All of the specializations within the game have unique abilities that can be used to differentiate themselves from other specs. We will be using these abilities in order to determine which specializaiton a specific player's character is. If there are no specs that correspond to any of the provided abilities, a blank String is returned to the user.

Step 4b, parse a single fight for the information we will be using for our analysis:

```python
def get_damage_for_fight(token: dict, code: str, id: int, delta_time: int, fight_name: str) -> list:
    query = '''query($code:String, $fight_id:Int) {
                reportData{
                    report(code:$code){
                        table(fightIDs: [$fight_id], dataType: DamageDone) 
                    }
                }
            }'''
    resp = get_information(token, query=query, code=code, fight_id=id)
    formatted_resp = resp['data']['reportData']['report']['table']['data']['entries']
    damage_information = []
    for player in formatted_resp:
        abilities = []
        for a in player['abilities']:
            abilities.append(a['name'])
        top_abilities = None
        if len(abilities) >= 5: 
            top_abilities = abilities[:5]
        else:
            top_abilities = abilities
        spec = get_spec_from_abilities(top_abilities)
        if spec == '':
            continue
        dps = round(float(player['total'] / (delta_time / 1000)), 2)
        if 'itemLevel' not in player:
            continue
        ilvl = player['itemLevel']
        damage_information.append([spec, dps, ilvl, fight_name, delta_time])
    return damage_information
```

This function uses the access token, a URL code, a fight ID, the fight length, and a fight name in order to provide the user with a list of character information. The response from the server after the query is sent contains a table that houses most of the requested individual fight's information. We iterate through the players involved within the fight and append certain data to a list. If certain data is not found within the current iterable, that character is skipped and the process continues with the next. The lack of some data signifies that the character is not directly controlled by a player and is thus not being used for this analysis. This list is then returned to the user.

Step 5, combine the use of all the previous functions to create a CSV-typed text document that will be used for analysis:

```python
def gather_data(client_id: str, client_secret: str, report_codes: str) -> None:
    access_token = get_access_token(client_id, client_secret).json()
    with open(report_codes, 'r+') as f:
        for current_code in f.readlines():
            fights = get_fights_from_url_code(access_token, current_code)
            with open('my_damage.txt', 'a+') as f:
                for fight in fights:
                    delta_time = fight['endTime'] - fight['startTime']
                    fight_name = fight['name']
                    damage_for_fight = get_damage_for_fight(access_token, current_code, fight['id'], delta_time, fight_name)
                    for player in damage_for_fight:
                        write_line = ''
                        for element_index in range(len(player)):
                            write_line += str(player[element_index])
                            if element_index < len(player) - 1:
                                write_line += ','
                            else:
                                write_line += '\n'
                        f.write(write_line)
```

This function is the "brain" of the code. It takes in the client information and the name of a file that contains URL codes. For each code within the provided file we will iterate through each fight, further iterate through each character within the fight, and then write that character information within a new file. Each line within our resulting data file will contain the following:
1. The specialization of an individual character during an individual fight.
2. The DPS said character did during the fight.
3. The item level of the character.
4. The name of the fight that this character's information corresponds to.
5. The length of the fight in milliseconds.

The code does not provide column names within the file so the information is to be appended into a file with the column names already written in.

# Data Visualization

We have collected and formatted the data; it's time to visualize. We will be using Tableau Public for this part. Tableau Public is a free and public version of Tableau that gives the user powerful tools for data visualization.

To start, we will create a new project and add our CSV-formatted text file as a data source. When the data source is added we manually update the data source to ensure that our data has correctly populated the corresponding fields within Tableau. After that, we will create an initial sheet. This sheet will be used to show the relathionship between a specialization and the average DPS of that specialization. The DPS field is added to the rows and the specialization field is added to the columns. Immediately I notice that there were incorrectly assigned specializations, both due to naming conventions as well as values, that I was going to have to remove. The below image is what we are initially given.

![Initial Graph](https://github.com/mjd-programming/MoP-Classic-Raid-Testing-Analysis/blob/main/Pictures/initial_graph.png)

After we trim the unusable data from our graph we begin to color coordinate the specializations based on their respective class. The colors are loosely linked to their in-game corresponding colors. You can explore the exact values of these colors as well as colors of classes that are not present in this analysis at this [link](https://wowpedia.fandom.com/wiki/Class_colors "WoW Class Colors"). The image below is what our sheet currently looks like.

This sheet helps bring up the idea that involving previously known information can also aid in analysis. While an initial look at this graph could show that the Survival Hunter seems to have a statistically huge leg up in the competition, the real issue can be found when looking at the Elemental Shaman bar. This analysis only focuses on the Tank and Damage Dealer roles but the information we gathered from WarcraftLogs contains all of the roles. The Shaman role that is not being shown has the capability of being incorrectly flagged as an Elemental Shaman within the Python code. This results in the bar height being lower than it should be. The function shown within the code section contains the correct version of the Elemental Shaman ability list. The image below is what our sheet currently looks like.

![Colored Graph](https://github.com/mjd-programming/MoP-Classic-Raid-Testing-Analysis/blob/main/Pictures/average_dps_per_spec_sheet.png)

After making some "helper" sheets, we create our dashboard. The Tableau dashboard is the avenue that allows users to interact with the data. The final dashboard shows us a list of all the analyzed specializations with filters on the top-right and a popularity graph on the bottom-right. The major use case of this dashboard is as follows:
- S
# Insights
