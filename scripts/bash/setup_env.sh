#!/usr/bin/env bash

echo '
DISCOGS_URL="https://api.discogs.com/masters/"
DISCOGS_USER_TOKEN=\"SWVQbGNiTWFOb3ltaWRMblBIeWlwbGN0dVluYXJvZmZYUkRLVVdtQg=="
LASTFM_KEY="MTQ5YmU0ODkxMDc5MDA1NzU1MTkzYmExYTRiOTU5OTM="
LASTFM_URL="http://ws.audioscrobbler.com/2.0/?method=album.getinfo"
MUSIC_BRAINZ_URL="https://beta.musicbrainz.org/ws/2/release/MBID/?inc=release-groups"
DEBUG=False
DISK_LINUX="/dev/cdrom"' > ../../.env
