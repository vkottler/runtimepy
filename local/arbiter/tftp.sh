#!/bin/bash

set -e

REPO=$(git rev-parse --show-toplevel)
REL=local/arbiter
CWD=$REPO/$REL
TMP=$CWD/tmp

PORT=8001

tftp_cmd() {
	rlwrap tftp -m octet localhost $PORT "$@"
}

test_get_file() {
	for FILE in LICENSE README.md tags; do
		if [ -f "$REPO/$FILE" ]; then
			tftp_cmd -c get "$FILE"
			diff "$REPO/$FILE" "$TMP/$FILE"
		fi
	done
}

test_large_file() {
	fallocate -l 30M "$REPO/dummy.bin"
	tftp_cmd -c get dummy.bin
	diff "$REPO/dummy.bin" "$TMP/dummy.bin"
	rm "$REPO/dummy.bin"
}

clear_tmp() {
	rm -f "$TMP/*"
}

test_write_files() {
	for FILE in LICENSE README.md tags; do
		tftp_cmd -c put "$REPO/$FILE" $REL/tmp/$FILE
		sleep 0.25
		diff "$REPO/$FILE" "$TMP/$FILE"
	done
}

mkdir -p "$TMP"
pushd "$TMP" >/dev/null || exit
set -x

# Test that we can retrieve files.
test_get_file
test_large_file

# Clear directory.
clear_tmp

# Test that we can write files.
test_write_files

set +x
popd >/dev/null || exit

# rm -rf "$TMP"

echo "Success."
