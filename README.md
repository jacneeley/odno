# ODNO

The all-in-one CD Ripper.

## What is ODNO?

Odno is a one stop CD Ripper application. ODNO can be used to rip CDs & and update metadata.

I listen to a lot of music and I enjoy collectiong CDs. My preferred way to listen to music is to use my phone as an mp3 player, but when I am at home I like to use my physical media.
I no longer use streaming services such as spotify, I purchase music off of bandcamp or I hunt for CDs at record stores, thrift stores &  book store bargain bins.
I rip my CDs so that I can transfer the tracks to my phone. The only problem is that metadata often gets lost during the ripping process or it is difficult to preserve. I am aware of other software that solves this problem, but many of the options out there I didn't like using for this or that reason. I wanted something different and I wanted to build something myself. I also wanted to understand how CDs actually work. Thus, ODNO was born.

## Installation and Setup

### Pre-reqs

- Install python 3.11 or greater.

### From Source

1. clone the repository on your machine
2. create venv directory `python -m venv .venv`
3. start venv `source bin/activate`
4. install dependencies `pip3 install requirements.txt`
5. start odno `python3 -m scripts.main`
    i. alternatively, you can use `run.sh` to activate the venv and start odno.

#### Build Executable From Source

```
    pyinstaller --onedir scripts/main.py
    mkdir ./dist/main/_internal/.logs
```

or

```
    bash build.sh
```

### Using the Executable

Simply download one of the builds, unzip the zip file into a given directory and enter the path of the executable like so ```your/path/to/main```
and ODNO will start.

From here you can create your own symbolic links and execute ODNO from your terminal.

## CLI

A CLI is in the works and is coming soon.

## Windows?

I am currently working on a windows version. Windows has a completely different API for interacting with CDROMs. I still need time to learn how to work with it. It is coming soon.