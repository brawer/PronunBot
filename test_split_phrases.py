#!/usr/bin/env python3
#
# Copyright (c) 2018 Sascha Brawer <sascha@brawer.ch>
# SPDX-License-Identifier: MIT

import codecs
import os
import subprocess
import sys
import tempfile
import unittest


class TestSplitPhrases(unittest.TestCase):
    def test_run(self):
        with tempfile.TemporaryDirectory(prefix='test') as workdir:
            subprocess.check_output([
                '/usr/bin/env', 'python3', 'split_phrases.py',
                '-o', workdir, '--language', 'rm-sursilv',
                '--date', '2007-03-09', '--performer', 'Erwin Ardüser',
                '--organization', 'Lia Rumantscha, Conradin Klais',
                '--license', 'Creative Commons Zero v1.0 Universal',
                'testdata/split_phrases'], stderr=sys.stdout.buffer)
            self.assertEqual(read_text_file(workdir, 'fails.txt'),
                             'testdata/split_phrases/bien di.mp3\n')
            self.assertTrue(exists(workdir, 'jeu-1.flac'))
            self.assertTrue(exists(workdir, 'savess-1.flac'))
            self.assertTrue(exists(workdir, 'prender-1.flac'))
            subprocess.check_output([
                'ffmpeg', '-i', os.path.join(workdir, 'jeu-1.flac'),
                '-f', 'ffmetadata', os.path.join(workdir, 'metadata.txt')],
                stderr=sys.stdout.buffer)
            metadata = read_text_file(workdir, 'metadata.txt')
            self.assertIn(r'TITLE=jeu', metadata)
            self.assertIn(r'PERFORMER=Erwin Ardüser', metadata)
            self.assertIn(r'LANGUAGE=rm-sursilv', metadata)
            self.assertIn(r'DATE=2007-03-09', metadata)
            self.assertIn(r'ORGANIZATION=Lia Rumantscha, Conradin Klais',
                          metadata)


# Helper for running unit tests.
def exists(directory, filename):
    return os.path.exists(os.path.join(directory, filename))


# Helper for running unit tests.
def read_text_file(directory, filename):
    path = os.path.join(directory, filename)
    with codecs.open(path, 'r', encoding='utf-8') as f:
        return f.read()


if __name__ == '__main__':
    unittest.main()
