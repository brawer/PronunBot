#!/usr/bin/env python3
#
# Copyright (c) 2018 Sascha Brawer <sascha@brawer.ch>
# SPDX-License-Identifier: MIT
#
# Tool for uploading sound files with pronunciations to Wikimedia Commons.
# Needs the output of the Quality Assurance (qa.txt) as input; see README.

import argparse
import codecs
import os
import pywikibot
from pywikibot.specialbots import UploadRobot
import re
import subprocess


def find_uploadable_files(qa_path, workdir):
    result = {}  # make sure that last verdict wins for a phrase
    with codecs.open(qa_path, 'r', 'utf-8') as logfile:
        for line in logfile:
            phrase, verdict = [col.strip() for col in line.split('\t')]
            if verdict != '0':
                result[phrase] = os.path.join(workdir, '%s-%s.flac' % (phrase, verdict))
    return result.values()


def extract_metadata(filepath):
    dump = subprocess.check_output(['metaflac', '--list', filepath])
    dump = dump.decode('utf-8')
    md = dict(re.findall(r'\n\s+comment\[\d+\]: ([A-Z]+)=(.[^\n]+)', dump))
    return md


def make_description(metadata):
    params = dict(metadata)
    params['_LANGUAGE_CATEGORY'] = LANGUAGE_CATEGORY[metadata['LANGUAGE']]
    params['_VOICE_GENDER'] = VOICE_GENDER[metadata['PERFORMER']]
    params['_ORG_CATEGORY'] = ORG_CATEGORY[metadata['ORGANIZATION']]
    params['_LICENSE_TAG'] = WIKIMEDIA_COMMONS_LICENSE_TAG[metadata['LICENSE']]
    return WIKIMEDIA_COMMONS_DESCRIPTION.format(**params)


VOICE_GENDER = {
    'Erwin Ardüser': 'Male voice',
}


LANGUAGE_CATEGORY = {
    'rm-sursilv': 'Sursilvan pronunciation',
}

ORG_CATEGORY = {
    'Lia Rumantscha / Conradin Klaiss, 7001 Chur, Switzerland': 'Lia Rumantscha',
}


WIKIMEDIA_COMMONS_LICENSE_TAG = {
   'Creative Commons Zero v1.0 Universal': '{{cc-zero}}'
}


WIKIMEDIA_COMMONS_DESCRIPTION = """
=={{int:filedesc}}==
{{Information
|description={{en|1={{Pronunciation|lang={LANGUAGE}|1={TITLE}}}}}
|date={DATE}
|source={ORGANIZATION}
|author=Speaker: {PERFORMER}
}}

{_VOICE_GENDER}

=={{int:license-header}}==
{_LICENSE_TAG}

[[Category:{_LANGUAGE_CATEGORY}]]
[[Category:{PERFORMER}]]
[[Category:{_ORG_CATEGORY}]]
"""


def upload(filepath):
    metadata = extract_metadata(filepath)
    description = make_description(metadata)
    wikimedia_filename = (
        'Pronunciation %s %s.flac' %
        (metadata['LANGUAGE'], metadata['TITLE']))
    bot = UploadRobot(
        url=[filepath], description=description,
        useFilename=wikimedia_filename,
        keepFilename=False, verifyDescription=True,
        targetSite=pywikibot.getSite('commons', 'commons'))
    bot.run()


if __name__ == '__main__':
    if not os.path.exists('qa.txt'):
        sys.stderr.write('Quality Assurance must be done before uploading.\n')
        sys.stderr.write('See README for instructions.\n')
        sys.exit(1)
    argparser = argparse.ArgumentParser(
        description='upload recorded pronunciations to Wikimedia commons')
    argparser.add_argument('workdir', help='path to output from split_phrases.py')
    args = argparser.parse_args()

    files = find_uploadable_files('qa.txt', args.workdir)
    for filepath in sorted(find_uploadable_files('qa.txt', args.workdir)):
        # TODO: Remove the following after getting approval to run the bot.
        if filepath not in [
                'split/la constituziun federala-1.flac',
                #'split/Grönlanda-1.flac',
                #'split/calcogn-2.flac',
                #'split/jeu carezel tei-1.flac'
        ]:
            continue
        upload(filepath)
