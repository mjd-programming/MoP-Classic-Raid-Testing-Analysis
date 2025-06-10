import requests

CLIENT_ID = '9f160fff-ae6c-4460-ae41-0b0027f6c303'
CLIENT_SECRET = 'rlLvxxf0Xqbubdvn0JSlq9y81XrZI7sTh8ZnMSHt'

token_uri = 'https://www.warcraftlogs.com/oauth/token'
public_url = 'https://www.warcraftlogs.com/api/v2/client'


def get_access_token(client_id: str, client_secret: str) -> any:
    '''
    Makes POST request to token_uri with client ID and client secret as authorization.
    If successful response, return the received access token.
    Else, return None.
    '''
    data = {'grant_type':'client_credentials'}
    auth = (client_id, client_secret)
    with requests.Session() as session:
        response = session.post(token_uri, data=data, auth=auth)
        if response.status_code == 200:
            return response
        return None
    
        
def get_information(token: dict, query: str, **kwargs) -> dict:
    '''
    Uses the token argument as a header to make GET request with the query and other variables. Returns the response.
    '''
    headers = {'Authorization':f'Bearer {token['access_token']}'}
    data = {'query': query, 'variables': kwargs}
    with requests.Session() as session:
        session.headers = headers
        return session.get(public_url, json=data).json()
        

def get_fights_from_url_code(token: dict, code: str) -> list:
    '''
    Specific query used to get fight information. Returns a list of all fights from the supplied log code.
    '''
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


def get_spec_from_abilities(abilities: str) -> str:
    '''
    Hard-coded list of popular/unique abilities used by each specialization. Returns the first spec with matching abilities.
    Returns nothing if no specialization was matched.
    '''
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


def get_damage_for_fight(token: dict, code: str, id: int, delta_time: int, fight_name: str) -> list:
    '''
    Function used to parse fight information. Returns general information from specific fight within the given log code.
    '''
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


def gather_data(client_id: str, client_secret: str, report_codes: str) -> None:
    '''
    Main function, takes a file path containing log codes and creates a formatted file with all fights' information.
    '''
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


if __name__ == '__main__':
    c_id = '' # removed for privacy
    c_secret = '' # removed for privacy
    gather_data(c_id, c_secret, 'warcraft_logs_html.txt')