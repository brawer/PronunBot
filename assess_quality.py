#!/usr/bin/env python3
#
# Copyright (c) 2018 Sascha Brawer <sascha@brawer.ch>
# SPDX-License-Identifier: MIT
#
# Tool for assessing the quality of recorded pronunciations
#
# For each recorded phrase or word, this tool asks the user to assess
# (“vet”) the recorded pronunciations. After hearing all the available
# variants, the user enters the number of the best recording, or `0`
# if they’re all bad.  The decision gets recorded into `qa.txt`.

import argparse
import codecs
import os
import subprocess


def check(workdir):
    qa_path = os.path.join(workdir, 'qa.txt')
    qa = read_qa(qa_path)
    qa_file = codecs.open(qa_path, 'a', 'utf-8')
    phrases = {}
    for f in os.listdir(workdir):
        if not f.endswith('.flac'):
            continue
        [phrase, num] = os.path.basename(f)[:-len('.flac')].rsplit('-', 1)
        phrases.setdefault(phrase, set()).add(num)
    for phrase in sorted(phrases.keys()):
        if phrase in qa:
            continue
        v = vet_phrase(phrase, phrases[phrase], workdir)
        if v != 'skip':
            qa_file.write('%s\t%s\n' % (phrase, v))
            qa_file.flush()
    qa_file.close()


def read_qa(qa_path):
    if not os.path.exists(qa_path):
        return set()
    qa = set()
    with codecs.open(qa_path, 'r', 'utf-8') as logfile:
        for line in logfile:
            phrase, verdict = line.split('\t')
            qa.add(phrase.strip())
    return qa


def vet_phrase(phrase, ids, workdir):
    print('-' * 50)
    print(phrase, len(ids))
    for phraseid in sorted(ids, key=int):
        filename = '%s-%s.flac' % (phrase, phraseid)
        if input(filename[:-len('.flac')]) == 'skip':
            return 'skip'
        subprocess.check_output(['afplay', os.path.join(workdir, filename)])
    while True:
        selection = input('--> ')
        if selection in ['skip', '0']:
            return selection
        elif selection in ids:
            return selection


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='assess the quality of available recordings')
    argparser.add_argument('workdir', help='path to output from split_phrases.py')
    args = argparser.parse_args()
    check(args.workdir)
