# PronunBot

PronunBot is a tool for uploading a batch of recorded pronunciations
to [Wikimedia Commons](https://commons.wikimedia.org/) and
[Wikidata](https://www.wikidata.org).

## Background

We’ve built this tool at the [Plurilinguism
Hackathon](https://forum-helveticum.ch/en/hackathon/) in November
2018.  [Lia Rumantscha](http://www.liarumantscha.ch/?changeLang=_en)
contributed recorded pronunciations of about 5000 phrases in the [Sursilvan
variant](https://en.wikipedia.org/wiki/Sursilvan_dialects_(Romansh))
of the [Romansh
language](https://en.wikipedia.org/wiki/Romansh_language) to the
hackathon. Back in March 2007, the pronunciations had been recorded
as language training material; at the 2018 hackathon, Lia Rumantscha kindly
gave permission to upload them to Wikidata under the Creative Commons Zero
license.


## Setup

We’ve used a Macintosh laptop with
[Docker](https://docs.docker.com/docker-for-mac/install/) running a
Linux container. For setup instructions, see the comments in `Dockerfile`.


## Splitting multi-word phrases

Many of the original recordings are multi-word phrases.
An example is the phrase [“jeu savess prender” 🔉](https://cdn.jsdelivr.net/gh/brawer/PronunBot/testdata/split_phrases/jeu%20savess%20prender.mp3). Because
the initial recording was done for language training, the words are often
separated by spans of silence; this is rather unusual in recorded
speech. Also, the original recordings often contain a few seconds of silence
before and after the spoken phrase.

For using the sound snippets in Wikidata lexemes, however, we need a
separate sound snippet for every word without surrounding silence.
The tool `split_phrases.py` helps to solve this problem: it goes over the
input files, calls [FFmpeg](https://www.ffmpeg.org/) to detect
silences, and then applies a simple heuristic to split the sound file
into single words.  Finally, the tool will tag each snippet with
metadata (such as license, performer, or language) and compress the
sound in the lossless [FLAC format](https://en.wikipedia.org/wiki/FLAC).

To run the splitting script, we’ve used the following command inside
the Linux container:

```
python split_phrases.py -o split  \
  --language=rm-sursilv --date=2007-03-09  \
  --performer="Erwin Ardüser"  \
  --organization="Lia Rumantscha / Conradin Klaiss, 7001 Chur, Switzerland"  \
  --copyright="2007 Lia Rumantscha"  \
  --license="Creative Commons Zero v1.0 Universal"  \
  /recordings
```

Some input files, for example the recorded phrase [“bien
di” 🔉](https://cdn.jsdelivr.net/gh/brawer/PronunBot/testdata/split_phrases/bien%20di.mp3),
do not have enough silent spans for splitting the phrase into
words. The tool logs the problem cases into `split-failures.txt`
next to the output files.


## Quality assessment

To check the quality of recorded phrases, run `python3 assess_quality.py split`
on the Mac command line. For each phrase or word, the tool plays the available
recordings; the user then picks the best, or enters `0` if they’re all bad.
The quality assessment gets recorded into a file `qa.txt`.


## Uploading sound files to Wikimedia Commons

TODO


## Uploading to Wikidata

TODO


## License

The code in this repository is copyright 2018 by [Sascha
Brawer](http://www.brawer.ch), and has been released as free software
under the [MIT license](https://spdx.org/licenses/MIT.html).

