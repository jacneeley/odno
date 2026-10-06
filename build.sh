#!/usr/bin/env bash

pyinstaller --clean -y --onedir scripts/main.py

mkdir ./dist/main/_internal/.logs

mkdir ./dist/main/.logs

mkdir ./dist/main/.resources

mkdir ./dist/main/scripts

cp ./scripts/bash -r ./dist/main/scripts/bash
