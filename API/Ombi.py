from datetime import datetime
import logging
import requests
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

from exception_handler import ExceptionHandler, CustomException

logging.basicConfig(format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')


def get_requests(ombi_url, influxdb_client, influxBucket, ombi_api):
    movie_data = {}

    try:
        movie_data = requests.get('{0}/api/v1/{1}/?apikey={2}'.format(ombi_url, 'Request/movie', ombi_api), verify=False).json()
        tv_data = requests.get('{0}/api/v1/{1}/?apikey={2}'.format(ombi_url, 'Request/tv', ombi_api), verify=False).json()

        json_body = {
            "measurement": "get_requests",
            "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "fields": {
                "total_request_count": 0,
                "processing_request_count": 0,
                "completed_request_count": 0,
                "movie_request_count": 0,
                "show_request_count": 0
            }
        }

        write_client = influxdb_client.write_api(write_options=SYNCHRONOUS)

        if movie_data:
            movies = movie_data

            movieLength = len(movies)
            json_body['fields']['movie_request_count'] = movieLength
            json_body['fields']['total_request_count'] += movieLength

            for movie in movies:
                processingCount = 0
                doneCount = 0
                status = movie["requestStatus"]

                if status == "Common.ProcessingRequest":
                    processingCount += 1
                else:
                    doneCount += 1

                json_body['fields']['processing_request_count'] += processingCount
                json_body['fields']['completed_request_count'] += doneCount

        if tv_data:
            shows = tv_data

            showLength = len(shows)
            json_body['fields']['show_request_count'] = showLength
            json_body['fields']['total_request_count'] += showLength

            for show in shows:
                processingCount = 0
                doneCount = 0
                for childRequest in show["childRequests"]:
                    status = childRequest["requestStatus"]

                    if status == "Common.ProcessingRequest":
                        processingCount += 1
                    else:
                        doneCount += 1

                json_body['fields']['processing_request_count'] += processingCount
                json_body['fields']['completed_request_count'] += doneCount

        if tv_data or movie_data:
            line = Point(json_body['measurement']).time(json_body['time'])
            for key, value in json_body['fields'].items():
                line.field(key, str(value))

            write_client.write(bucket=influxBucket, record=line.to_line_protocol())

    except requests.exceptions.ConnectionError:
        exception = ExceptionHandler("Invalid URL or Port", "Ombi")
        exception.Debug()

        raise CustomException

    except Exception:
        exception = ExceptionHandler(movie_data['response']['message'], "Ombi")
        exception.Debug()

        raise CustomException


def get_request_count(ombi_url, influxdb_client, influxBucket, ombi_api):
    data = {}

    try:
        data = requests.get('{0}/api/v1/{1}/?apikey={2}'.format(ombi_url, 'Request/count', ombi_api), verify=False).json()

        if data:
            write_client = influxdb_client.write_api(write_options=SYNCHRONOUS)

            request = data['response']['data']

            total_requests = request['pending'] + request['approved'] + request['available']
            pending_requests = request['pending']
            approved_requests = request['approved']
            available_requests = request['available']

            json_body = {
                "measurement": "get_request_count",
                "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "pending_requests": pending_requests,
                    "approved_requests": approved_requests,
                    "available_requests": available_requests,
                    "total_requests": total_requests
                }
            }

            line = Point(json_body['measurement']).time(json_body['time'])
            for key, value in json_body['fields'].items():
                line.field(key, str(value))

            write_client.write(bucket=influxBucket, record=line.to_line_protocol())

    except requests.exceptions.ConnectionError:
        exception = ExceptionHandler("Invalid URL or Port", "Ombi")
        exception.Debug()

        raise CustomException

    except Exception:
        exception = ExceptionHandler(data['response']['message'], "Ombi")
        exception.Debug()

        raise CustomException


def export(ombi_url, influxdb_client, influxBucket, ombi_api):
    get_requests(ombi_url, influxdb_client, influxBucket, ombi_api)
