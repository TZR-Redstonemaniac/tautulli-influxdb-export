from datetime import datetime
import logging
import requests
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

logging.basicConfig(format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')


def get_queue(sonarr_url, influxdb_client, influxBucket, sonarr_api):
    try:
        data = requests.get('{0}/api/{1}/?apikey={2}'.format(sonarr_url, 'queue', sonarr_api), verify=False).json()

        if data:
            write_client = influxdb_client.write_api(write_options=SYNCHRONOUS)
            queue = data['response']['data']

            queueLength = queue['totalRecords']

            json_body = {
                "measurement": "get_queue",
                "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "queue_length": queueLength
                }
            }

            for record in queue['records']:
                json_body['fields'][record['title']] = {
                    "season_count": record['series']['statistics']['seasonCount'],
                    "episode_file_count": record['series']['statistics']['episodeFileCount'],
                    "episode_count": record['series']['statistics']['episodeCount'],
                    "size_on_disk": record['series']['statistics']['sizeOnDisk'],
                    "estimated_completion_time": record['estimatedCompletionTime'],
                    "tracked_download_state": record['trackedDownloadState']
                }

            line = Point(json_body['measurement']).time(json_body['time'])
            for key, value in json_body['fields'].items():
                line.field(key, str(value))

            write_client.write(bucket=influxBucket, record=line.to_line_protocol())

    except Exception as e:
        logging.warning(str(e))
        pass


def export(sonarr_url, influxdb_client, influxBucket, sonarr_api):
    get_queue(sonarr_url, influxdb_client, influxBucket, sonarr_api)
