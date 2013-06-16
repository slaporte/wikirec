import sys
import sqlite3
from json import loads
from functools import partial
from twisted.internet import reactor
from autobahn.websocket import (WebSocketClientFactory,
                                WebSocketClientProtocol,
                                connectWS)
from twisted.python import log

DEFAULT_WEBSOCKET = 'ws://wikimon.hatnote.com:9000'
DEFAULT_DB = 'wikirec.db'


def create_db(db_name):
    connection = sqlite3.connect(db_name)
    with connection:
        cur = connection.cursor()
        cur.execute('CREATE TABLE revisions \
                (Page_title TEXT, URL TEXT, Flags TEXT, User TEXT, \
                Change_size INT, Geo_city TEXT, Geo_region_code TEXT, \
                Geo_region_name TEXT, Geo_areacode TEXT, Geo_ip TEXT, \
                Geo_zipcode TEXT, Geo_longitude TEXT, Geo_metro_code TEXT, \
                Geo_latitude TEXT, Geo_country_code TEXT, \
                Geo_country_name TEXT, Log_time)')


def db_observer(event_msg, connection):
    cursor = connection.cursor()
    try:
        msg = loads(event_msg['message'][0])
    except ValueError:
        return  # it's not a revision message
    query_msg = (msg['page_title'],
                 msg['url'],
                 msg['flags'],
                 msg['user'],
                 msg['change_size'],
                 msg.get('geo_ip', {}).get('city'),
                 msg.get('geo_ip', {}).get('region_code'),
                 msg.get('geo_ip', {}).get('region_name'),
                 msg.get('geo_ip', {}).get('areacode'),
                 msg.get('geo_ip', {}).get('ip'),
                 msg.get('geo_ip', {}).get('zipcode'),
                 msg.get('geo_ip', {}).get('longitude'),
                 msg.get('geo_ip', {}).get('metro_code'),
                 msg.get('geo_ip', {}).get('latitude'),
                 msg.get('geo_ip', {}).get('country_code'),
                 msg.get('geo_ip', {}).get('country_name'),
                 event_msg['time'])
    cursor.execute('INSERT into revisions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,\
                   ?,?,?,?)',
                   query_msg)
    connection.commit()


class RecordClientProtocol(WebSocketClientProtocol):
    def onMessage(self, msg, binary):
        log.msg(msg)


def create_parser():
    from argparse import ArgumentParser
    desc = "Save edits from wikimon"
    prs = ArgumentParser(description=desc)
    prs.add_argument('--logfile', help='file to save log')
    prs.add_argument('--websocket', default=DEFAULT_WEBSOCKET,
                     help='wikimon websocket url')
    prs.add_argument('--debug', action='store_true',
                     help='print log in the console')
    prs.add_argument('--db', default=DEFAULT_DB,
                     help='database to save log')
    return prs


def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.debug or (not args.logfile and not args.db):
        print 'debug logging to console'
        log.addObserver(log.FileLogObserver(sys.stdout).emit)
    if args.db:
        con = sqlite3.connect(args.db)
        try:
            # checking if db exists
            con.execute('select count(*) from revisions')
        except sqlite3.OperationalError:
            print 'creating db ' + args.db
            create_db(args.db)
            con = sqlite3.connect(args.db)
        print 'logging to ' + args.db
        log.addObserver(partial(db_observer, connection=con))
    if isinstance(args.logfile, basestring):
        log_file = open(args.logfile, 'a')
        print 'logging to ' + str(log_file)
        log.startLogging(log_file)
    factory = WebSocketClientFactory(args.websocket)
    factory.protocol = RecordClientProtocol
    connectWS(factory)
    reactor.run()

if __name__ == '__main__':
    main()
