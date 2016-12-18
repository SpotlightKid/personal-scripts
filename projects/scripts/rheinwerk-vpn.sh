#!/bin/bash
#
# rheinwerk-vpn.sh
#

sudo modprobe tun
sudo openvpn --config /etc/openvpn/rheinwerk.conf
