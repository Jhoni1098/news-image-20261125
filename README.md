# news-image-20261125

[![make.fun competition](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![make.fun rank](https://make.fun/badge/news-image-20261125/Jhoni1098/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![make.fun reward](https://make.fun/badge/news-image-20261125/Jhoni1098/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

One image summing up the world's news of Wednesday, 25 November 2026:
Zelenskiy confirms Ukraine's drone strike on the Russian cargo ship
Sparta II in the Gulf of Finland (and a Russian warship sunk off Libya);
Houthis hit Riyadh's tallest tower a second time in a week, wounding 11;
the CIA and ODNI are hit by a cyberattack on an unclassified system;
a US jury finds Huawei guilty on 10 of 12 counts; COP31 ends with no
deal; US inflation and GDP data land ahead of the Fed's December meeting;
the WHO pulls staff from an Ebola hospital in DR Congo amid fighting;
and the Democrats clinch the US House with at least 259 seats.

Built for the [make.fun competition](https://make.fun/bounty/news-image-20261125)
of the same name. `main.py` (Python 3.13, standard library only) draws the
1024x1024 newspaper front page from scratch — raster canvas, embedded
bitmap fonts, hand-rolled PNG encoder — and writes it to the output
directory. No network, no clock, no randomness: two runs write
byte-identical files. `entry.png` beside it is the rendered output, kept
for preview.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
