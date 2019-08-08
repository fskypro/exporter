#! /bin/bash

echo "begin stop cfgserver..."
ps -aux | grep cfgserver | grep -v grep | awk '{print $2}' | xargs kill -9
echo "cfgserver stoped!"

