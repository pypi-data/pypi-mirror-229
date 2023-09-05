import eyed3
import requests
import json
import os
from dzr_import.tracks import get_session_id, get_tracks_ids, get_user_data


def get_tracks_metadata(tracks, api_token, session_id):
    res = requests.post(f'https://www.deezer.com/ajax/gw-light.php?method=song.getListData&input=3&api_version=1.0&api_token={api_token}', 
                       cookies={'sid': session_id},
                       headers={'Content-Type': 'application/json', 'Accept':'application/json'},
                       data=json.dumps({'sng_ids': tracks}))
    
    data = list(map(lambda track: {
        'artist': track['ART_NAME'], 
        'release_date': track['PHYSICAL_RELEASE_DATE'],
        'title': track['SNG_TITLE'],
        'album': track['ALB_TITLE'],
        'track_number': track['TRACK_NUMBER'],
        'album_art': track['ALB_PICTURE'],
        }, res.json()['results']['data']))
    
    return data


def add_track_metadata(track, metadata, path):
        audiofile = eyed3.load(f"{path}/{track[0]} - {track[1]}.mp3")
        if audiofile.tag == None:
            audiofile.initTag()

        # Add basic tags
        audiofile.tag.title = metadata["title"]
        audiofile.tag.album = metadata["album"]
        audiofile.tag.artist = metadata["artist"]
        audiofile.tag.release_date = metadata["release_date"]
        audiofile.tag.track_num = metadata["track_number"]
        audiofile.tag.file_name = f"{track[0]} - {track[1]}.mp3"

        image_url = f"https://e-cdn-images.dzcdn.net/images/cover/{metadata['album_art']}/1024x1024-000000-100-0-0.jpg"
        image_data = requests.get(image_url, timeout=60).content
        audiofile.tag.images.set(3, image_data, "image/jpeg")
        audiofile.tag.save()
        

def tag_tracks(tracks):
    tracks_ids = get_tracks_ids(tracks)
    session_id = get_session_id()
    user_token, user_license, api_token = get_user_data(session_id)
    tracks_data = get_tracks_metadata(tracks_ids, api_token, session_id)
    for track, metadata in zip(tracks, tracks_data):
        add_track_metadata(track, metadata, "output")
    