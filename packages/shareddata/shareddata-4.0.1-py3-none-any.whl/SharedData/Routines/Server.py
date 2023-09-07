from SharedData.RealTime import RealTime
import time
import sys
import json

from SharedData.Logger import Logger
from SharedData.SharedData import SharedData
shdata = SharedData('SharedData.Routines.Server', user='master')

if len(sys.argv) >= 2:
    _argv = sys.argv[1:]
else:
    Logger.log.error('Please specify IP and port!')
    raise Exception('Please specify IP and port!')

args = _argv[0].split(',')
host = args[0]
port = int(args[1])
RealTime.runserver(shdata, host, port)

Logger.log.info('ROUTINE STARTED!')

while True:
    n = 0
    sendheartbeat = True
    for client in RealTime.clients.keys():
        n = n+1
        c = RealTime.clients[client]
        if 'table' in c:
            table = c['table'].table
            Logger.log.debug('#heartbeat#Client %i:%s,%s' %
                            (n, client.getpeername(), table.relpath))
        else:            
            Logger.log.debug('#heartbeat#Client %i:%s' %
                            (n, client.getpeername()))
        sendheartbeat = False
    if sendheartbeat:
        Logger.log.debug('#heartbeat#host:%s,port:%i' % (host, port))
    time.sleep(15)
