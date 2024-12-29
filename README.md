# PicDate: Quick and Simple Date Marking for Photos

## Description

Existing tools are not for me, so I make this. The format and style are almost fully controlled by users. The [`DateTimeOriginal`](https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif/datetimeoriginal.html), i.e., the date the photo was taken, is added if the exif information exists; otherwise, [`stat.ST_MTIME`](https://docs.python.org/3/library/stat.html#stat.ST_MTIME), the time of last modification, is used for those photo without exif information. Note that ST_MTIME is just close to but not the taken time. The image quality are different after processed due to Pillow tool.

## Install

```bash
pip3 install git+https://github.com/aben20807/picdate.git
```

stable version:

```bash
pip3 install git+https://github.com/aben20807/picdate.git@v2.0.0
```

## Usage

```bash
picdate -s 20221012/ -r
```

## Screenshot

![DSC_0005](https://user-images.githubusercontent.com/14831545/207787756-1e98292a-2e5a-4fdb-9db4-1dbe9aad7227.JPG)

## Font

+ [CursedTimerUlil-Aznm.ttf](https://www.fontspace.com/cursed-timer-ulil-font-f29411): designed by [heaven castro](https://www.fontspace.com/heaven-castro) and licensed as Freeware

## Performance

+ 360 photos (1.72 GB) -> 360 photos with dates (1.31 GB): 5.967s

## Help

```bash
$ picdate -h
usage: picdate [-h] -s DIR [-d DIR] [-f] [-r] [--text_size N] [--text_color COLOR]
               [--text_anchor TEXT_ANCHOR] [--pos_x X] [--pos_y Y] [--fine_tune_aspect_ratio RATIO]
               [--stroke_width STROKE_WIDTH] [--stroke_color COLOR] [--quality QUALITY]
               [--format FORMAT] [--img_exts IMG_EXTS]

PicDate: Quick and Simple Date Marking for Photos

options:
  -h, --help            show this help message and exit
  -s DIR, --src DIR     input dir (required) (default: None)
  -d DIR, --dst DIR     output dir (default: ./picdate_result/)
  -f, --force           overwrite existing files (default: False)
  -r, --recursive       recursively process (default: False)
  --text_size N         text size ('N' mm) (default: 4.24)
  --text_color COLOR    text color (default: (255, 149, 21))
  --text_anchor TEXT_ANCHOR
                        text anchor (ref: https://pillow.readthedocs.io/en/stable/handbook/text-
                        anchors.html#text-anchors) (default: rb)
  --pos_x X             position for x-axis from 0 (left) to 1 (right) (default: 0.94)
  --pos_y Y             position for y-axis from 0 (top) to 1 (bottom) (default: 0.94)
  --fine_tune_aspect_ratio RATIO
                        expect aspect ratio for fine tune pos for cropping ('none' or 'M/N' (M<=N))
                        (default: 2/3)
  --stroke_width STROKE_WIDTH
                        stroke width for text (default: 1)
  --stroke_color COLOR  stroke color (default: (242, 97, 0))
  --quality QUALITY     jpg output quality (default: 95)
  --format FORMAT       date format (ref: https://docs.python.org/3/library/datetime.html#strftime-
                        and-strptime-format-codes) (default: `%y %-m %-d)
  --img_exts IMG_EXTS   support extensions for processed photos (case insensitive) (default:
                        jpg,jpeg,png,tiff)
```

## License

MIT
