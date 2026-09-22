#!/usr/bin/env bash

pyinstaller --onedir scripts/main.py

mkdir ./dist/main/_internal/.logs

zip -r dist/odno.zip dist/main/

tar -czvf dist/odno.tar.gz dist/main