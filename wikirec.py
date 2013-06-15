import sys
import os
from twisted.internet import reactor
from autobahn.websocket import (WebSocketClientFactory,
                                WebSocketClientProtocol,
                                connectWS)
from twisted.python import log

DEFAULT_WEBSOCKET = 'ws://wikimon.hatnote.com:9000'


class RecordClientProtocol(WebSocketClientProtocol):
    def onMessage(self, msg, binary):
        log.msg(msg)


def create_parser():
    from argparse import ArgumentParser
    desc = "record edits from wikimon"
    prs = ArgumentParser(description=desc)
    prs.add_argument('--log', help='log file to write')
    prs.add_argument('--websocket', default=DEFAULT_WEBSOCKET,
                     help='wikimon websocket url')
    prs.add_argument('--debug', action='store_true',
                     help='print logging')
    return prs


def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.debug or not args.log:
        print 'debug logging to console'
        log.addObserver(log.FileLogObserver(sys.stdout).emit)
    if isinstance(args.log, basestring):
        log_file = open(args.log, 'a')
        print 'logging to ' + str(log_file)
        log.startLogging(log_file)
    factory = WebSocketClientFactory(args.websocket)
    factory.protocol = RecordClientProtocol
    connectWS(factory)
    reactor.run()

if __name__ == '__main__':
    main()
