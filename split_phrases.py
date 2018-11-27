#!/usr/bin/env python3
#
# Copyright (c) 2018 Sascha Brawer <sascha@brawer.ch>
# SPDX-License-Identifier: MIT
#
# Tool for splitting multi-word pronunciations
#
# In our project, many of the original recordings are multi-word phrases
# such as “jeu savess prender”. Typically (and rather unusually for
# recorded speech), each word is separated by a brief span of silence.
# For Wikidata, however, we need a separate sound file for each word.
# This tool goes over the input files, calls [FFmpeg](https://www.ffmpeg.org/)
# to detect silences, and then applies a simple heuristic to split the
# sound file into single words.  Finally, the tool will tag each snippet
# with metadata (such as license, performer, or language) and convert it
# to the lossless [FLAC format](https://en.wikipedia.org/wiki/FLAC).

import argparse
import os
import re
import subprocess
import shutil


def get_text(filepath):
    """'jeu savess prender.mp3' --> 'jeu savess prender'"""
    text = filepath[:-len('.mp3')]
    text = text.replace('Ç', 'é')
    text = ' '.join(text.replace(',', ' ').split())
    if text[-1] == '.':
        text = text[:-1]
    if ' ' in text:
        words = text.split()
        if words[0] not in {'Anita', 'Julia', 'Peter', 'Sonja'}:
            text = text[0].lower() + text[1:]
    return text.replace("'", "’")


def find_silences(filepath):
    """Find silent spans in recorded pronunciations.

    For example, 'path/to/pronunciation.mp3' --> [(0.0, 0.3), (3.2, None)]
    if there is silence for the initial 0.3 seconds, and from 3.2s to the end.
    Calls `ffmpeg` for silence detection and parses its debug logs.
    """
    command = ['ffmpeg', '-i', filepath, '-af', 'silencedetect=n=-40dB:d=0.05',
               '-f', 'null', '-']
    try:
        dump = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        return None
    lines = [line.split(']', 1)[1].strip()
             for line in dump.decode('utf-8').splitlines()
             if line.startswith('[silencedetect')]
    silences = ['silence_start:' + s
                for s in' | '.join(lines).split('silence_start:') if s]
    result = []
    for s in silences:
        start = re.search(r'silence_start:\s*([0-9\-\.]+)', s)
        end = re.search(r'silence_end:\s*([0-9\-\.]+)', s)
        start_sec = float(start.group(1)) if start is not None else None
        end_sec = float(end.group(1)) if end is not None else None
        result.append((start_sec, end_sec))
    return result


def score_silence(item):
    """Compute a goodness score for a silent audio span (start, end).

    Used by `find_spoken_wordspans()` to find where to split phrases.
    """
    start, end = item
    # We definitely want to split at the first and last detected silent span,
    # since these indicate the beginning and end of the actual recording.
    # Otherwise, we rank by duration, so we prefer to split at longer pauses.
    if start <= 0.0 or end is None:
        return 100000.0  # seconds
    else:
        return end - start  # seconds


def find_spoken_wordspans(filepath, text):
    """('jeu savess.mp3', 'jeu savess') --> [('jeu', 0.1, 0.3), ('savess', 0.7, 0.8)]
    """
    words = text.split()
    silences = find_silences(filepath)
    if not silences:
        return None
    # For N words, take the best (N + 1) silences in the audio.
    if len(silences) <= len(words):
        return None  # fewer silences than expected; needs manual splitting
    silences = sorted(silences, key=score_silence, reverse=True)[:len(words)+1]
    silences = list(sorted(silences))
    # We’re interested in the non-silent spans _between_ silences.
    spans = []
    for i in range(len(words)):
        spans.append((words[i], silences[i][1], silences[i+1][0]))
    return spans


def convert(filepath, start, end, performer, language, date, organization,
            license, copyright, word, outpath):
    command = ['ffmpeg', '-i', filepath, '-ss', str(start),
               '-t', str(end - start), '-ac', '1',
               '-compression_level', '12',
               '-metadata', 'TITLE=' + word,
               '-metadata', 'GENRE=']
    if performer:
        command.extend(['-metadata', 'PERFORMER=' + performer])
    if language:
        command.extend(['-metadata', 'LANGUAGE=' + language])
    if organization:
        command.extend(['-metadata', 'ORGANIZATION=' + organization])
    if date:
        command.extend(['-metadata', 'DATE=' + date])
    if license:
        command.extend(['-metadata', 'LICENSE=' + license])
    if copyright:
        command.extend(['-metadata', 'COPYRIGHT=' + copyright])
    command.append(outpath)
    try:
        dump = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        os.remove(outpath)
        return False
    return True


def process(filepath, fails):
    """Tries to process one single file, recording failures into `fails`."""
    print(filepath)
    text = get_text(filepath.split('/')[-1])
    spans = find_spoken_wordspans(filepath, text)
    if not spans:
        fails.write(filepath + '\n')
        return
    for word, start, end in spans:
        i = 0
        while True:
            i = i + 1
            outpath = os.path.join(args.output, '%s-%d.flac' % (word, i))
            if not os.path.exists(outpath):
                break
        if not convert(filepath, start, end, performer=args.performer,
                       language=args.language, date=args.date,
                       organization=args.organization, license=args.license,
                       copyright=args.copyright, word=word, outpath=outpath):
            fails.write(filepath + '\n')


def add_replay_gain_metadata(dirpath):
    # Add ReplayGain metadata to all FLAC files in `dirpath`.
    flacfiles = [f for f in os.listdir(dirpath) if f.endswith('.flac')]
    command = ['/usr/bin/metaflac', '--add-replay-gain'] + flacfiles
    subprocess.check_output(command, cwd=dirpath, stderr=subprocess.STDOUT)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='extract words from a collection of MP3 files')
    argparser.add_argument('--language', required=True,
                           help='language being processed')
    argparser.add_argument('--performer',
                           help='name of speaker who did the reading')
    argparser.add_argument('--copyright',
                           help='copyright attribution, eg. "2001 Foo Bar"')
    argparser.add_argument('--license',
                           help='license for the work')
    argparser.add_argument(
        '--organization',
        help='name of the organization who produced the track')
    argparser.add_argument('--date', help='date of recording')
    argparser.add_argument('--output', '-o', required=True,
                           help='path for writing output files')
    argparser.add_argument('recordings',
                           help='path to directory with MP3 files')
    args = argparser.parse_args()
    if os.path.exists(args.output):
        shutil.rmtree(args.output)
    os.mkdir(args.output)
    with open(os.path.join(args.output, 'split-failures.txt'), 'w') as fails:
        for filename in sorted(os.listdir(args.recordings)):
            # if 'seprepara' in filename: break
            if filename.endswith('.mp3'):
                filepath = os.path.join(args.recordings, filename)
                process(filepath, fails)
    add_replay_gain_metadata(args.output)
