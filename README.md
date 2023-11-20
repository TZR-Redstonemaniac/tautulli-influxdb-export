# tautulli/sonarr/radarr/ombi-influxdb-export

This script will query Tautulli/Sonarr/Radarr/Ombi to pull basic stats and store them in InfluxDB. Stay tuned for further additions!

You should install the script as a service to boot with your OS.

## Dependencies
  * Tautulli (aka PlexPy) (https://github.com/Tautulli/Tautulli)
  * Python (v2.7.x)
  * InfluxDB (https://github.com/influxdata/influxdb)
  * InfluxDB Python Client (https://github.com/influxdata/influxdb-client-python)

## Example

  ```
  python /path/to/tautulli_influxdb_export.py
  ```

## Docker Example

  ```
  cd <folder>
  docker build -t tautulli_influxdb_export .
  docker run -d --name=tautulli_influxdb_export --restart unless-stopped -e TAUTULLI_HOST=<host> -e TAUTULLI_KEY=<key> -e INFLUXDB_HOST=<influxdbhost> -e INFLUXDB_DB=<influxdbdatabase> tautulli_influxdb_export
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

### To Do:
  * Activity
    - *#* Audio Transcode Streams
    - *#* Audio Transcode Streams (Playing)
    - *#* Audio Direct Play Streams
    - *#* Audio Direct Play Streams (Playing)
  * Users
    - Current Streaming Users Location Data (via IP lookup)

## Use-Case
  With the data exported to influxdb, you can create some useful stats/graphs in graphing tools such as grafana (http://grafana.org/)

  ![alt tag](https://cloud.githubusercontent.com/assets/4528753/17122931/7176e2aa-52a5-11e6-8ff1-89ab6a8e7f82.png)
