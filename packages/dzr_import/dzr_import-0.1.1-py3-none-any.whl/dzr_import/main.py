import exiftool
import requests
import os

from dzr_import.dec import calcbfkey, decryptfile
from dzr_import.tag import tag_tracks
from dzr_import.tracks import get_cdns, get_session_id, get_tracks_data, get_tracks_ids, get_user_data


def download_tracks(cdns, tracks):
    for cdn, track in zip(cdns, tracks):
        res = requests.get(cdn, stream=True)
        with open(f"output/{track[0]} - {track[1]}_encrypted.mp3", 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


def decrypt_tracks(tracks, ids):
    for track, id in zip(tracks, ids):
        with open(f"output/{track[0]} - {track[1]}_encrypted.mp3", 'rb') as fh, open(f"output/{track[0]} - {track[1]}.mp3", 'wb') as fo:
            decryptfile(fh, calcbfkey(id).encode('utf-8'), fo)
        os.remove(f"output/{track[0]} - {track[1]}_encrypted.mp3")

def run():
    files = [f"tracks/{track}" for track in os.listdir('tracks')]
    tracks = []
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(files)
        tracks = [(d['Vorbis:Artist'], d['Vorbis:Title']) for d in metadata]

    tracks_ids = get_tracks_ids(tracks)
    session_id = get_session_id()
    user_token, user_license, api_token = get_user_data(session_id)
    tracks_data = get_tracks_data(tracks_ids, api_token, session_id)
    cdns = get_cdns(list(map(lambda track: track['token'], tracks_data)), user_license)
    download_tracks(cdns, tracks)
    decrypt_tracks(tracks, list(map(lambda track: track['id'], tracks_data)))
    tag_tracks(tracks)