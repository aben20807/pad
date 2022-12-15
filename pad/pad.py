import argparse
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import datetime
import multiprocessing
import signal
from urllib.request import urlretrieve
import sys


def add_date_to_img(inpath: str, outpath: str, config: dict):
    try:
        with Image.open(inpath) as img:
            width, height = img.size

            # get date from exif or st_mtime
            exif = img._getexif()
            if exif is None or 36867 not in exif.keys():
                print(f"'{inpath}' does not have exif info, use modified date instead")
                date = Path(inpath).stat().st_mtime
                date = datetime.datetime.fromtimestamp(date)
            else:
                # get date that photo was generated to be used
                # ref: https://www.awaresystems.be/imaging/tiff/tifftags/privateifd/exif/datetimeoriginal.html
                date = exif[36867]  # exif original format is "YYYY:MM:DD hh:mm:ss"
                date = datetime.datetime.fromisoformat(
                    date.replace(":", "-", 2) + ".000"
                )

            # get formated date
            text = date.strftime(config["format"])

            # get a font
            font_size = (width if width > height else height) // 36
            fnt = ImageFont.truetype(str(config["font_path"]), font_size)

            # get a drawing context
            draw = ImageDraw.Draw(img)

            # draw text
            draw.text(
                (width * config["pos_w"], height * config["pos_h"]),
                text,
                anchor=config["text_anchor"],
                font=fnt,
                fill=config["text_color"],
                stroke_width=config["stroke_width"],
                stroke_fill=config["stroke_color"],
            )

            # create parent directors
            if not Path(outpath).absolute().parent.exists():
                Path(outpath).absolute().parent.mkdir(parents=True, exist_ok=True)

            # save processed photo
            if exif is None:
                img.save(outpath, quality=config["quality"], subsampling=0)
            else:
                img.save(
                    outpath,
                    quality=config["quality"],
                    subsampling=0,
                    exif=img.info["exif"],
                )

    except Exception as e:
        print(e, locals())
        import traceback, sys

        traceback.print_exc(file=sys.stdout)


def setup():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def add_date_in_dir_mt(
    in_dir: str, out_dir: str, recursive: bool, overwrite: bool, config: dict
):
    files = Path(in_dir).rglob("*") if recursive else Path(in_dir).glob("*")
    allowed_exts = ["." + str(i).lower() for i in config["img_exts"].split(",")]

    with multiprocessing.Manager():
        tasks = []
        pool = multiprocessing.Pool(multiprocessing.cpu_count(), setup)
        for file in files:

            if str(file.suffix).lower() not in allowed_exts:  # Skip non-img files
                continue

            in_path = file.absolute()
            out_path = str(in_path).replace(
                str(Path(in_dir).absolute()), str(Path(out_dir).absolute())
            )

            if not overwrite and Path(out_path).exists():
                print(f"'{out_path}' exists and overwrite is set to False.")
                continue

            if str(in_path) == str(out_path):
                print(
                    f"Out '{out_path}' equals to In '{in_path}'. Please specify other path"
                )
                continue

            tasks.append(pool.apply_async(add_date_to_img, (in_path, out_path, config)))

        for task in tasks:
            try:
                task.get(10)
            except multiprocessing.TimeoutError:
                print("TLE")
                continue
            except KeyboardInterrupt:
                pool.terminate()
                pool.join()
                return 1

        pool.close()
        pool.join()


def tuple_type(strings):
    strings = strings.replace("(", "").replace(")", "")
    mapped_int = map(int, strings.split(","))
    return tuple(mapped_int)


def get_args():
    """Init argparser and return the args from cli."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-s", "--src", help="input dir (required)", type=str, required=True
    )
    parser.add_argument(
        "-d",
        "--dst",
        help="output dir",
        type=str,
        default="./pad_result/",
    )
    parser.add_argument(
        "-f", "--force", help="overwrite existing files", action="store_true"
    )
    parser.add_argument(
        "-r", "--recursive", help="recursively process", action="store_true"
    )
    parser.add_argument(
        "--text_color", help="text color", type=tuple_type, default=(255, 149, 21)
    )
    parser.add_argument(
        "--text_anchor",
        help="text anchor (ref: https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors)",
        type=str,
        default="rb",
    )
    parser.add_argument(
        "--pos_w", help="position for width (0~1)", type=float, default=0.94
    )
    parser.add_argument(
        "--pos_h", help="position for height (0~1)", type=float, default=0.94
    )
    parser.add_argument(
        "--stroke_width", help="stroke width for text", type=int, default=1
    )
    parser.add_argument(
        "--stroke_color", help="stroke color", type=tuple_type, default=(242, 97, 0)
    )
    parser.add_argument("--quality", help="jpg output quality", type=int, default=95)
    parser.add_argument(
        "--format",
        help="date format (ref: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)",
        type=str,
        default="`%y %-m %-d",
    )
    parser.add_argument(
        "--img_exts",
        help="support extensions for processed photos (case insensitive)",
        type=str,
        default="jpg,jpeg,png,tiff",
    )
    return parser.parse_args()


def cli():
    args = get_args()
    print(f"args: {args}")

    config = {
        "text_color": args.text_color,
        "text_anchor": args.text_anchor,
        "pos_h": args.pos_h,
        "pos_w": args.pos_w,
        "stroke_width": args.stroke_width,
        "stroke_color": args.stroke_color,
        "quality": args.quality,
        "format": args.format,
        "font_path": Path("~/.cache/pad/CursedTimerUlil-Aznm.ttf").expanduser(),
        "img_exts": args.img_exts,
    }

    if not config["font_path"].exists():
        print(f"download font file from online to {config['font_path']}")
        config["font_path"].parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(
            "https://github.com/aben20807/pad/blob/master/font/CursedTimerUlil-Aznm.ttf?raw=true",
            config["font_path"],
        )

    if Path(args.src).exists() and Path(args.src).is_file():
        if not Path(args.dst).is_file():
            print(f"Error: Because 'args.src' is a file, 'args.dst' should be also a file")
            sys.exit(1)
        if not args.force and Path(args.dst).exists():
            print(f"'{args.dst}' exists and 'args.force' (overwrite) is set to False.")
            sys.exit(1)
        add_date_to_img(args.src, args.dst, config)
    else:
        add_date_in_dir_mt(args.src, args.dst, args.recursive, args.force, config)


if __name__ == "__main__":
    cli()
