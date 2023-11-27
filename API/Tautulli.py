import logging
import traceback
from datetime import datetime
from exception_handler import *

import requests
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

logging.basicConfig(format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')


def get_activity(tautulli_url, influxdb_client, influxBucket):
    data = {}

    try:
        data = requests.get('{0}{1}'.format(tautulli_url, '&cmd=get_activity'), verify=False).json()

        if data:
            write_client = influxdb_client.write_api(write_options=SYNCHRONOUS)
            if data['response']['message'] is not None:

                total_stream_count = int(data['response']['data']['stream_count'])

                # loop over the streams
                sessions = data['response']['data']['sessions']
                users = {}
                total_stream_playing_count = 0
                transcode_stream_count = 0
                transcode_stream_playing_count = 0
                direct_play_stream_count = 0
                direct_play_stream_playing_count = 0
                direct_stream_stream_count = 0
                direct_stream_stream_playing_count = 0
                concurrent_stream_user_count = 0
                concurrent_stream_user_diffip_count = 0

                for s in sessions:
                    # check for concurrent streams
                    su = s['user']
                    ip = s['ip_address']
                    if su in users:
                        concurrent_stream_user_count += 1
                        if ip not in users[su]:
                            users[su].append(ip)
                    else:
                        users[su] = [ip]

                    playing = s['state'] == 'playing'
                    if s['transcode_decision'] == 'direct play':
                        direct_play_stream_count += 1
                        if playing:
                            direct_play_stream_playing_count += 1
                    else:
                        if s['video_decision'] == 'copy':
                            direct_stream_stream_count += 1
                            if playing:
                                direct_stream_stream_playing_count += 1
                        else:  # transcode = 'transcode'
                            transcode_stream_count += 1
                            if playing:
                                transcode_stream_playing_count += 1

                    if s['state'] == 'playing':
                        total_stream_playing_count += 1

                # determine how many concurrent users with diff IPs we have
                for k, v in list(users.items()):
                    if len(v) > 1:
                        concurrent_stream_user_diffip_count += 1

                json_body = {
                    "measurement": "Activity",
                    "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "fields": {
                        "stream_count": total_stream_count,
                        "stream_playing_count": total_stream_playing_count,
                        "stream_transcode_count": transcode_stream_count,
                        "stream_transcode_playing_count": transcode_stream_playing_count,
                        "stream_directplay_count": direct_play_stream_count,
                        "stream_directplay_playing_count": direct_play_stream_playing_count,
                        "stream_directstream_count": direct_stream_stream_count,
                        "stream_directstream_playing_count": direct_stream_stream_playing_count,
                        "user_concurrent_count": concurrent_stream_user_count,
                        "user_concurrent_diffip_count": concurrent_stream_user_diffip_count
                    }
                }
            else:
                json_body = {
                    "measurement": "Activity",
                    "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "fields": {
                        "stream_count": 0,
                        "stream_playing_count": 0,
                        "stream_transcode_count": 0,
                        "stream_transcode_playing_count": 0,
                        "stream_directplay_count": 0,
                        "stream_directplay_playing_count": 0,
                        "stream_directstream_count": 0,
                        "stream_directstream_playing_count": 0,
                        "user_concurrent_count": 0,
                        "user_concurrent_diffip_count": 0
                    }
                }

            line = Point(json_body['measurement']).time(json_body['time'])
            for key, value in json_body['fields'].items():
                line.field(key, str(value))

            write_client.write(bucket=influxBucket, record=line)

    except requests.exceptions.ConnectionError:
        exception = ExceptionHandler("Invalid URL or Port", "Tautulli")
        exception.Debug()

        raise CustomException

    except Exception:
        exception = ExceptionHandler(data['response']['message'], "Tautulli")
        exception.Debug()

        raise CustomException


def get_users(tautulli_url, influxdb_client, influxBucket):
    data = {}

    try:
        data = requests.get('{0}{1}'.format(tautulli_url, '&cmd=get_users'), verify=False).json()

        if data:
            write_client = influxdb_client.write_api(write_options=SYNCHRONOUS)

            users = data['response']['data']
            total_users = len(users)
            total_home_users = 0

            for s in users:
                if s['is_home_user'] == '1':
                    total_home_users += 1

            json_body = {
                "measurement": "Users",
                "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "user_count": total_users,
                    "home_user_count": total_home_users
                }
            }

            for u in users:
                json_body['fields'][u['username']] = {
                    "email": u['email']
                }

            line = Point(json_body['measurement']).time(json_body['time'])
            for key, value in json_body['fields'].items():
                line.field(key, str(value))

            write_client.write(bucket=influxBucket, record=line.to_line_protocol())

    except requests.exceptions.ConnectionError:
        exception = ExceptionHandler("Invalid URL or Port", "Tautulli")
        exception.Debug()

        raise CustomException

    except Exception:
        exception = ExceptionHandler(data['response']['message'], "Tautulli")
        exception.Debug()

        raise CustomException


def get_libraries(tautulli_url, influxdb_client, influxBucket):
    data = {}

    try:
        data = requests.get('{0}{1}'.format(tautulli_url, '&cmd=get_libraries'), verify=False).json()

        if data:
            libraries = data['response']['data']
            utcnow = datetime.utcnow()
            write_client = influxdb_client.write_api(write_options=SYNCHRONOUS)

            json_body = {
                "measurement": "",
                "time": utcnow.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "fields": {},
                "tags": {}
            }

            for l in libraries:
                section_name = l['section_name']
                section_type = l['section_type']
                count = num(l.get('count', 0))
                child_count = num(l.get('child_count', 0))

                json_body['measurement'] = section_name
                json_body['fields'] = {
                    "section_type": section_type,
                    "count": count,
                    "child_count": child_count
                }

                line = (Point(json_body['measurement']).time(json_body['time']))
                for key, value in json_body['fields'].items():
                    line.field(key, value)

                write_client.write(bucket=influxBucket, record=line.to_line_protocol())

    except requests.exceptions.ConnectionError:
        exception = ExceptionHandler("Invalid URL or Port", "Tautulli")
        exception.Debug()

        raise CustomException

    except Exception:
        exception = ExceptionHandler(data['response']['message'], "Tautulli")
        exception.Debug()

        raise CustomException


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def export(tautulli_url, influxdb_client, influxBucket):
    get_activity(tautulli_url, influxdb_client, influxBucket)
    get_users(tautulli_url, influxdb_client, influxBucket)
    get_libraries(tautulli_url, influxdb_client, influxBucket)
