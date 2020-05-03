#!/bin/bash

if [[ "$1" = "-c" ]]; then
    clipboard=1
    shift
fi

path="$1"
shift
passfile="$PREFIX/$path.gpg"
check_sneaky_paths "$path"

if [[ -f $passfile ]]; then
    if [[ -n "$1" ]]; then
        key="$1"
        $GPG -d "${GPG_OPTS[@]}" "$passfile" | tail -n +2 | while read line; do
            if echo -n "$line" | grep -q ^$key'\s*[:=]'; then
                line="$(echo $line | sed -e 's/^'$key'\s*[:=]\s*//')"
                if [[ -n "$clipboard" ]]; then
                    clip "$line"
                else
                    echo "$line"
                fi
            fi
        done
    else
        $GPG -d "${GPG_OPTS[@]}" "$passfile" | tail -n +2 || exit $?
    fi
elif [[ -z $path ]]; then
    die ""
else
    die "Error: $path is not in the password store."
fi
