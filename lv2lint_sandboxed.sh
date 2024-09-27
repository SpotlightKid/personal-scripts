#!/bin/bash

set -e
set -u

lv2lint()
{
	local spec
	local ret

	spec=$( mktemp -d )

	[ -d "${spec}" ] || return 1

	pushd "${spec}" >& /dev/null
		for ext in atom \
			buf-size \
			core \
			data-access \
			dynmanifest \
			event \
			instance-access \
			log \
			midi \
			morph \
			options \
			parameters \
			patch \
			port-groups \
			port-props \
			presets \
			resize-port \
			state \
			time \
			ui \
			units \
			urid \
			uri-map \
			worker
		do
			ln -s "/usr/lib/lv2/${ext}.lv2" "${ext}.lv2"
		done
	popd >& /dev/null

	LV2_PATH="${spec}" /usr/bin/lv2lint "$@"
	ret=$?

	rm -rf "${spec}"

	return ${ret}
}

lv2lint "$@"
