# pad: photo add date

## Install

```bash
pip3 install git+https://github.com/aben20807/pad.git
```

## Usage

```bash
pad -s 20221012/ -r
```

## Screenshot

![DSC_0005](https://user-images.githubusercontent.com/14831545/195342599-26c714d1-37f2-4ec6-9f0d-f90b814ff67a.JPG)

## Font

+ [Cursed Timer ULiL](https://blogfonts.com/cursed-timer-ulil.font)

## Help

```bash
$ pad -h
usage: pad [-h] -s SRC [-d DST] [-f] [-r] [--text_color TEXT_COLOR] [--text_anchor TEXT_ANCHOR] [--pos_w POS_W] [--pos_h POS_H] [--stroke_width STROKE_WIDTH] [--stroke_color STROKE_COLOR] [--quality QUALITY] [--format FORMAT]

optional arguments:
  -h, --help            show this help message and exit
  -s SRC, --src SRC     input dir (required) (default: None)
  -d DST, --dst DST     output dir (default: ./pad/)
  -f, --force           overwrite existing files (default: False)
  -r, --recursive       recursively process (default: False)
  --text_color TEXT_COLOR
                        text color (default: (255, 149, 21))
  --text_anchor TEXT_ANCHOR
                        text anchor (ref: https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors) (default: rb)
  --pos_w POS_W         position for width (0~1) (default: 0.94)
  --pos_h POS_H         position for height (0~1) (default: 0.94)
  --stroke_width STROKE_WIDTH
                        stroke width for text (default: 1)
  --stroke_color STROKE_COLOR
                        stroke color (default: (242, 97, 0))
  --quality QUALITY     jpg output quality (default: 95)
  --format FORMAT       date format (ref: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) (default: `%y %-m %-d)
```

## License

MIT

