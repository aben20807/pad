import argparse
import datetime
import multiprocessing
import platform
import signal
import sys
from fractions import Fraction
from pathlib import Path
from urllib.request import urlretrieve

from PIL import Image, ImageDraw, ImageFont, ImageOps


def add_date_to_img(inpath: str, outpath: str, config: dict):
    try:
        with Image.open(inpath) as img:
            # img = ImageOps.exif_transpose(img)

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
                # rotate the image based on the exif info
                img = ImageOps.exif_transpose(img)

            # get formated date
            text = date.strftime(config["format"])

            # fine tune for photo crop in different aspect ratio
            width, height = img.size
            offset_w, offset_h = 0, 0
            if config["fine_tune_aspect_ratio"] != "none":
                aspect_ratio = float(Fraction(config["fine_tune_aspect_ratio"]))

                if width > height:
                    if width / height > 1 / aspect_ratio + 0.01:
                        offset_w = (width - (1 / aspect_ratio * height)) / 2
                    elif width / height < 1 / aspect_ratio - 0.01:
                        offset_h = (height - (aspect_ratio * width)) / 2
                else:  # width <= height
                    if width / height > aspect_ratio + 0.01:
                        offset_w = (width - (aspect_ratio * height)) / 2
                    elif width / height < aspect_ratio - 0.01:
                        offset_h = (height - (1 / aspect_ratio * width)) / 2

                if offset_h > 0 or offset_w > 0:
                    print(f"'{inpath}' fine tune for cropping into aspect ratio")

            # get a font
            size = (
                float(config["text_size"]) * max(width, height) // 152
            )  # the longest side is 152mm for 4x6
            fnt = ImageFont.truetype(str(config["font_path"]), int(size))

            # get a drawing context
            draw = ImageDraw.Draw(img)

            # draw text
            draw.text(
                (
                    (width - offset_w) * config["pos_x"],
                    (height - offset_h) * config["pos_y"],
                ),
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
        import sys
        import traceback

        traceback.print_exc(file=sys.stdout)


def setup():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def add_date_in_dir_mt(
    in_dir: str, out_dir: str, recursive: bool, overwrite: bool, config: dict, jobs: int
):
    files = Path(in_dir).rglob("*") if recursive else Path(in_dir).glob("*")
    allowed_exts = ["." + str(i).lower() for i in config["img_exts"].split(",")]

    with multiprocessing.Manager():
        tasks = []
        pool = multiprocessing.Pool(jobs, setup)
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
        prog="picdate",
        description="PicDate: Quick and Simple Date Marking for Photos",
        formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(
            prog, width=80
        ),
    )
    parser.add_argument(
        "-s",
        "--src",
        metavar="DIR",
        help="input dir (required)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-d",
        "--dst",
        metavar="DIR",
        help="output dir",
        type=str,
        default="./picdate_result/",
    )
    parser.add_argument(
        "-f", "--force", help="overwrite existing files", action="store_true"
    )
    parser.add_argument(
        "-r", "--recursive", help="recursively process", action="store_true"
    )
    parser.add_argument(
        "-j",
        "--jobs",
        metavar="N",
        help="parallel jobs to process",
        type=int,
        default=multiprocessing.cpu_count(),
    )
    parser.add_argument(
        "--text_size", metavar="N", help="text size ('N' mm)", type=float, default=4.24
    )
    parser.add_argument(
        "--text_color",
        metavar="COLOR",
        help="text color",
        type=tuple_type,
        default=(255, 149, 21),
    )
    parser.add_argument(
        "--text_anchor",
        help="text anchor (ref: https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors)",
        type=str,
        default="rb",
    )
    parser.add_argument(
        "--pos_x",
        metavar="X",
        help="position for x-axis from 0 (left) to 1 (right)",
        type=float,
        default=0.94,
    )
    parser.add_argument(
        "--pos_y",
        metavar="Y",
        help="position for y-axis from 0 (top) to 1 (bottom)",
        type=float,
        default=0.94,
    )
    parser.add_argument(
        "--fine_tune_aspect_ratio",
        metavar="RATIO",
        help="expect aspect ratio for fine tune pos for cropping ('none' or 'M/N' (M<=N))",
        type=str,
        default="2/3",
    )
    parser.add_argument(
        "--stroke_width", metavar="N", help="stroke width for text", type=int, default=1
    )
    parser.add_argument(
        "--stroke_color",
        metavar="COLOR",
        help="stroke color",
        type=tuple_type,
        default=(242, 97, 0),
    )
    parser.add_argument(
        "--quality", metavar="N", help="jpg output quality", type=int, default=95
    )
    parser.add_argument(
        "--format",
        help="date format (ref: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)",
        type=str,
        default="`%y %#m %#d" if platform.system() == "Windows" else "`%y %-m %-d",
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
        "text_size": args.text_size,
        "text_color": args.text_color,
        "text_anchor": args.text_anchor,
        "pos_y": args.pos_y,
        "pos_x": args.pos_x,
        "fine_tune_aspect_ratio": args.fine_tune_aspect_ratio,
        "stroke_width": args.stroke_width,
        "stroke_color": args.stroke_color,
        "quality": args.quality,
        "format": args.format,
        "font_path": Path("~/.cache/picdate/CursedTimerUlil-Aznm.ttf").expanduser(),
        "img_exts": args.img_exts,
    }

    if not config["font_path"].exists():
        print(f"download font file from online to {config['font_path']}")
        config["font_path"].parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(
            "https://github.com/aben20807/picdate/blob/master/font/CursedTimerUlil-Aznm.ttf?raw=true",
            config["font_path"],
        )

    if Path(args.src).exists() and Path(args.src).is_file():
        if not Path(args.dst).is_file():
            print(
                f"Error: Because 'args.src' is a file, 'args.dst' should be also a file"
            )
            sys.exit(1)
        if not args.force and Path(args.dst).exists():
            print(f"'{args.dst}' exists and 'args.force' (overwrite) is set to False.")
            sys.exit(1)
        add_date_to_img(args.src, args.dst, config)
    else:
        add_date_in_dir_mt(
            args.src, args.dst, args.recursive, args.force, config, args.jobs
        )


if __name__ == "__main__":
    cli()
