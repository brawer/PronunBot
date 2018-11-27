# PronunBot

PronunBot is a tool for uploading a batch of recorded pronunciations
to [Wikimedia Commons](https://commons.wikimedia.org/) and
[Wikidata](https://www.wikidata.org).

## Background

We’ve built this tool at a [Plurilinguism
Hackathon](https://forum-helveticum.ch/en/hackathon/) in November
2018.  [Lia Rumantscha](http://www.liarumantscha.ch/?changeLang=_en)
contributed about 5000 recorded pronunciations in the [Sursilvan
variant](https://en.wikipedia.org/wiki/Sursilvan_dialects_(Romansh))
of the [Romansh
language](https://en.wikipedia.org/wiki/Romansh_language) to the
hackathon. The pronunciations had been recorded back in 2007 as
language training material; at the hackathon, Lia Rumantscha kindly
gave permission to upload them to Wikidata under the Creative Commons Zero
license.


## Setup

We’ve used a Macintosh laptop with
[Docker](https://docs.docker.com/docker-for-mac/install/) running a
Linux container. For setup instructions, see the comments in `Dockerfile`.


## Splitting multi-word phrases

In our project, many of the original recordings are multi-word phrases
such as “jeu savess prender”. Typically (and rather unusually for
recorded speech), each word is separated by a brief span of silence.
For Wikidata, however, we need a separate sound file for each word.
This tool goes over the input files, calls [FFmpeg](https://www.ffmpeg.org/)
to detect silences, and then applies a simple heuristic to split the
sound file into single words.  Finally, the tool will tag each snippet
with metadata (such as license, performer, or language) and convert it
to the lossless [FLAC format](https://en.wikipedia.org/wiki/FLAC).

To run the splitting script, we’ve used the following command inside
the Linux container:

```
python split_phrases.py -o split  \
  --language=rm-sursilv --date=2007-03-09  \
  --performer="Erwin Ardüser"  \
  --organization="Lia Rumantscha, Conradin Klaiss"  \
  --license="Creative Commons Zero v1.0 Universal"  \
  /recordings
```


## Vetting the recordings

TODO


## Uploading sound files to Wikimedia Commons

TODO


## Uploading to Wikidata

TODO


## License

The code in this repository is copyright 2018 by [Sascha
Brawer](http://www.brawer.ch), and has been released as free software
under the [MIT license](https://spdx.org/licenses/MIT.html).

