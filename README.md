# WikiRec

Listen to [WikiMon](https://github.com/hatnote/wikimon), for record-keeping purposes.

## Usage

```
usage: wikirec.py [-h] [--logfile LOGFILE] [--websocket WEBSOCKET] [--debug]
                  [--db DB]

Save edits from wikimon

optional arguments:
  -h, --help            show this help message and exit
  --logfile LOGFILE     file to save log
  --websocket WEBSOCKET
                        wikimon websocket url
  --debug               print log in the console
  --db DB               database to save log
```

## Requirements
 * Twisted==13.0.0
 * autobahn==0.5.14
