# Plex Statistic Exporter

This script will query Tautulli/Sonarr/Radarr/Ombi to pull basic stats and store them in InfluxDB. Stay tuned for further additions!

You can install the script as a service to boot with your OS, or as a docker container.

## Dependencies
  * Tautulli (aka PlexPy) (https://github.com/Tautulli/Tautulli)
  * Python (v3.11.x)
  * InfluxDB (https://github.com/influxdata/influxdb)
  * InfluxDB Python Client (https://github.com/influxdata/influxdb-client-python)

## Example

  ```
  python /path/to/plex_statistic_exporter.py
  ```

## Docker Example

  ```
  cd <folder>
  docker build -t plex_statistic_exporter .
  docker run -d --name=plex_statistic_exporter --restart unless-stopped -v /path/to/config:/config
  ```

## Exported Data
  * Activity
    - *#* Total Streams
    - *#* Total Streams (Playing)
    - *#* Transcode Streams
    - *#* Transcode Streams (Playing)
    - *#* Direct Play Streams
    - *#* Direct Play Streams (Playing)
  * Users
    - *#* Total Users
    - *#* Home Users
    - *#* Users currently streaming concurrently
    - *#* Users currently streaming concurrently (with different IP addresses)
  * Libraries
    - *#* Total Items Per Library

## Use-Case
  With the data exported to influxdb, you can create some useful stats/graphs in graphing tools such as grafana (http://grafana.org/)

  ![alt tag](https://cloud.githubusercontent.com/assets/4528753/17122931/7176e2aa-52a5-11e6-8ff1-89ab6a8e7f82.png)
