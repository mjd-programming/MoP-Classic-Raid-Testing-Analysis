import requests
import json

CLIENT_ID = '9f160fff-ae6c-4460-ae41-0b0027f6c303'
CLIENT_SECRET = 'rlLvxxf0Xqbubdvn0JSlq9y81XrZI7sTh8ZnMSHt'

authorization_uri = 'https://www.warcraftlogs.com/oauth/authorize'
token_uri = 'https://www.warcraftlogs.com/oauth/token'

public_url = 'https://www.warcraftlogs.com/api/v2/client'

def get_access_token():
    data = {'grant_type':'client_credentials'}
    auth = (CLIENT_ID, CLIENT_SECRET)
    with requests.Session() as session:
        response = session.post(token_uri, data=data, auth=auth)
        if response.status_code == 200:
            return response
        else:
            return None
        
def get_information(token, query: str, **kwargs):
    headers = {'Authorization':f'Bearer {token['access_token']}'}
    data = {'query': query, 'variables': kwargs}
    with requests.Session() as session:
        session.headers = headers
        response = session.get(public_url, json=data)
        return response.json()

def get_fights_from_url_code(code: str, token) -> list:
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

def get_damage_for_fight(code: str, id: int, delta_time: int, fight_name: str, token):
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
        spec = player['icon']
        dps = round(float(player['total'] / (delta_time / 1000)), 2)
        ilvl = -1
        if 'itemLevel' in player:
            ilvl = player['itemLevel']
        fight_length = delta_time
        damage_information.append([spec, dps, ilvl, fight_name, fight_length])
    return damage_information

def gather_data(report_codes):
    access_token = get_access_token().json()
    with open(report_codes, 'r+') as f:
        for current_code in f.readlines():
            url_code = current_code
            fights = get_fights_from_url_code(url_code, access_token)
            with open('my_damage.txt', 'a+') as f:
                for fight in fights:
                    delta_time = fight['endTime'] - fight['startTime']
                    fight_name = fight['name']
                    damage_for_fight = get_damage_for_fight(url_code, fight['id'], delta_time, fight_name, access_token)
                    for player in damage_for_fight:
                        f.write(str(player) + '\n')

# comment added to test git
if __name__ == '__main__':
    gather_data('warcraft_logs_html.txt')