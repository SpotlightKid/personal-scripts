#!/bin/bash
#
# optimize-performance.sh
#

action="${1:-start}"
WLANDEV="wlp6s0"

case "$action" in
    start)
        # Set VM swapiness for improved performance
        sudo /sbin/sysctl -q -w vm.swappiness=10

        # Set CPU to performance
        sudo cpupower frequency-set -g performance

        # Turn off WiFi
        sudo iwconfig $WLANDEV txpower off

        # Disable screen blanking
        xset -dpms; xset s off
        ;;
    stop)
        # Set VM swapiness to default
        sudo /sbin/sysctl -q -w vm.swappiness=60

        # Set CPU to powersave
        sudo cpupower frequency-set -g powersave

        # Turn on WiFi
        sudo iwconfig $WLANDEV txpower on

        # Enable screen blanking
        xset +dpms; xset s on
esac

exit 0
