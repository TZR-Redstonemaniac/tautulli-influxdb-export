from datetime import datetime
import requests
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

from exception_handler import ExceptionHandler, CustomException


def get_queue(radarr_url, influxdb_client, influxBucket, radarr_api):
    data = {}

    try:
        data = requests.get('{0}/api/v3/{1}/?apikey={2}'.format(radarr_url, 'queue', radarr_api), verify=False).json()

        if data:
            write_client = influxdb_client.write_api(write_options=SYNCHRONOUS)
            queue = data

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
                    "size_on_disk": record['size'],
                    "estimated_completion_time": record.get('estimatedCompletionTime'),
                    "tracked_download_state": record['trackedDownloadState']
                }

            line = Point(json_body['measurement']).time(json_body['time'])
            for key, value in json_body['fields'].items():
                line.field(key, str(value))

            write_client.write(bucket=influxBucket, record=line.to_line_protocol())

    except requests.exceptions.ConnectionError:
        exception = ExceptionHandler("Invalid URL or Port", "Radarr")
        exception.Debug()

        raise CustomException

    except Exception:
        exception = ExceptionHandler(data['response']['message'], "Radarr")
        exception.Debug()

        raise CustomException


def export(radarr_url, influxdb_client, influxBucket, radarr_api):
    get_queue(radarr_url, influxdb_client, influxBucket, radarr_api)
