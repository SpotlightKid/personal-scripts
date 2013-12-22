#!/bin/bash
#
# block_ping.sh - Block PING from monitoring server for testing purposes
#

REMOTE_IP="${2:-217.69.69.69}"
SERVER_IP="217.69.76.38"

if [ "x$1" = "xon" ]; then
    iptables -I INPUT -p icmp --icmp-type echo-request -s $REMOTE_IP -d $SERVER_IP -j DROP
    iptables -I OUTPUT -p icmp --icmp-type echo-reply -s $SERVER_IP -d $REMOTE_IP -j DROP
    #iptables -I INPUT -p icmp --icmp-type echo-request -s $REMOTE_IP -d $SERVER_IP -m state --state NEW,ESTABLISHED,RELATED -j DROP
    #iptables -I OUTPUT -p icmp --icmp-type echo-reply -s $SERVER_IP -d $REMOTE_IP -m state --state ESTABLISHED,RELATED -j DROP
elif [ "x$1" = "xoff" ]; then
    iptables -D INPUT 1
    iptables -D OUTPUT 1
fi
