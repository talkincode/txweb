#!/bin/sh

if [ ! -f "/var/txweb" ];then
    mkdir -p /var/txweb/data
    mkdir -p /var/txweb/logs
    mkdir -p /var/txweb/etc
fi

exec "$@"