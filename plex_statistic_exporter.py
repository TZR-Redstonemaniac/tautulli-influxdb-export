#!/usr/bin/python
from __future__ import print_function

import configparser
import time

from influxdb_client import InfluxDBClient
from exception_handler import *

from API import Sonarr, Ombi, Radarr, Tautulli

tautulli_url_format = 'http://{0}{1}/api/v2?apikey={2}'
url_format = 'http://{0}{1}'


def main():
    print("Started")
    args = parse_config()

    tautulliBucket = args['InfluxDB']['TautulliBucket']
    sonarrBucket = args['InfluxDB']['SonarrBucket']
    radarrBucket = args['InfluxDB']['RadarrBucket']
    ombiBucket = args['InfluxDB']['OmbiBucket']

    tautulli_url = get_tautulli_url(args['Tautulli']['Host'], args['Tautulli']['Port'], args['Tautulli']['ApiKey'])
    sonarr_url = get_url(args['Sonarr']['Host'], args['Sonarr']['Port'])
    radarr_url = get_url(args['Radarr']['Host'], args['Radarr']['Port'])
    ombi_url = get_url(args['Ombi']['Host'], args['Ombi']['Port'])

    sonarr_api = args['Sonarr']['ApiKey']
    radarr_api = args['Radarr']['ApiKey']
    ombi_api = args['Ombi']['ApiKey']

    influxdb_client = InfluxDBClient(url=args['InfluxDB']['Url'], token=args['InfluxDB']['Token'], org=args['InfluxDB']['Org'])

    init_exporting(args['General']['Interval'], tautulli_url, tautulliBucket,
                   sonarr_url, sonarr_api, sonarrBucket,
                   radarr_url, radarr_api, radarrBucket,
                   ombi_url, ombi_api, ombiBucket,
                   influxdb_client)


def parse_config():
    config = configparser.ConfigParser()
    config.read('/config/config.ini')

    return config


def init_exporting(interval,
                   tautulli_url, tautulli_bucket,
                   sonarr_url, sonarr_api, sonarr_bucket,
                   radarr_url, radarr_api, radarr_bucket,
                   ombi_url, ombi_api, ombi_bucket,
                   influxdb_client):
    while True:
        try:
            Tautulli.export(tautulli_url, influxdb_client, tautulli_bucket)
            Sonarr.export(sonarr_url, influxdb_client, sonarr_bucket, sonarr_api)
            Radarr.export(radarr_url, influxdb_client, radarr_bucket, radarr_api)
            Ombi.export(ombi_url, influxdb_client, ombi_bucket, ombi_api)
        except CustomException:
            pass

        print("Exported")
        time.sleep(int(interval))


def get_tautulli_url(host, port, apikey):
    return tautulli_url_format.format(host, port, apikey)


def get_url(host, port):
    return url_format.format(host, port)


if __name__ == '__main__':
    main()
