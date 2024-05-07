#!/bin/bash

set -e

SCALE_ARGS=()

create_gif() {
	set -x
	ffmpeg -y -i "$1" "${SCALE_ARGS[@]}" "${1%.*}.gif"
	set +x
}

# https://askubuntu.com/questions/1440589/how-to-compress-videos-properly-with-webm
COMPRESS_ARGS=(-c:v libvpx-vp9 -b:v 0 -crf 48 -deadline best)
COMPRESS_ARGS+=(-row-mt 1 -b:a 96k -ac 2)

compress_and_gif() {
	# Two pass compression.
	COMPRESSED="compressed-$1"

	set -x
	ffmpeg -i "$1" "${COMPRESS_ARGS[@]}" \
		-pass 1 -an -f null /dev/null
	ffmpeg -y -i "$1" "${COMPRESS_ARGS[@]}" \
		-pass 2 -c:a libopus "$COMPRESSED"
	set +x

	# Create GIF.
	create_gif "$COMPRESSED"
}

# Scale gif down.
SCALE_ARGS+=(-vf scale="832:-1")
create_gif "$1"

# compress_and_gif "$1"
