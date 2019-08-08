#! /bin/bash
/ubin/cfgserver/bin/stop.sh

sleep 1
echo "begin start cfgserver..."
/ubin/cfgserver/bin/start.sh /data/zkroot/server.conf &
echo "cfgserver started."


