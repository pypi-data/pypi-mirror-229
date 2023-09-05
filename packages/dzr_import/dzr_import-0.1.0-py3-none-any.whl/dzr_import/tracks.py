import requests
import json

def get_session_id():
    res = requests.get('https://www.deezer.com/ajax/gw-light.php?method=deezer.ping&api_version=1.0&api_token')
    return res.json()['results']['SESSION']

def get_user_data(session_id):
    res = requests.get('https://www.deezer.com/ajax/gw-light.php?method=deezer.getUserData&input=3&api_version=1.0&api_token=', cookies={'sid': session_id})
    user_token = res.json()['results']['USER_TOKEN']
    user_license = res.json()['results']['USER']['OPTIONS']['license_token']
    api_token = res.json()['results']['checkForm']

    return user_token, user_license, api_token

def get_tracks_ids(tracks):
    res = map(lambda track: requests.get('https://api.deezer.com/search?q=artist:"{}" track:"{}"'.format(*track)), tracks)
    
    return list(map(lambda r: r.json()['data'][0]['id'], res))

def get_tracks_data(tracks, api_token, session_id):
    res = requests.post(f'https://www.deezer.com/ajax/gw-light.php?method=song.getListData&input=3&api_version=1.0&api_token={api_token}', 
                       cookies={'sid': session_id},
                       headers={'Content-Type': 'application/json', 'Accept':'application/json'},
                       data=json.dumps({'sng_ids': tracks}))
    
    data = list(map(lambda track: {'id': track['SNG_ID'], 'token': track['TRACK_TOKEN']}, res.json()['results']['data']))
    
    return data
    
def get_cdns(tokens, user_license):
    res = requests.post('https://media.deezer.com/v1/get_url',
                        headers={'Content-Type': 'application/json', 'Accept':'application/json'},
                        data=json.dumps({
                            'track_tokens': tokens,
                            'license_token': user_license,
                            'media': [{
                                'type': 'FULL', 'formats': [{
                                    'cipher': 'BF_CBC_STRIPE',
                                    'format': 'MP3_128',
                                }]
                                }],
                            }))
    
    return list(map(lambda data: data['media'][0]['sources'][0]['url'], res.json()['data']))