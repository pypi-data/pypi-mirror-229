"""stat, imstat, and rmstat command line utils."""

import platform
import logging
from pathlib import Path
import click
from datetime import datetime
from typing import List

from .util import *
from .stat import *
from .image_util import *

root_path = click.option(
    "--root",
    "root_path",
    default=Path("."),
    type=click.Path(
        file_okay=False, dir_okay=True,
        resolve_path=True, path_type=Path),
    help="""
The root path of the rgb run. The 'im' and 'plot'
directories are going to stem from the root. The default
is the current dir.
""",
    show_default=True,
)

alpha = click.option(
    "--alpha",
    "alpha",
    default=0.05,
    type=click.FLOAT,
    help="""
Amount of confidence. Increase the alpha to improve the
accuracy of the rgb test. In a higher alpha run, the photo must
be a closer match to the target to be accepted.
""",
    show_default=True
)

port = click.option(
    "-p",
    "--port",
    "port",
    default=None,
    help="""
The USB port id in Linux/Mac OS. The port is used to id the 
camera port. The flag is not going to have an effect on Windows.
""",
    show_default=True
)

mu = click.option(
    "-m",
    "--mu",
    "mu",
    type=click.Tuple([click.INT, click.INT, click.INT]),
    nargs=3,
    default=None,
    help="""
Target rgb mean. Each photo is accepted or rejected on its
statistical deviation from the target.
""",
    show_default=True
)

tag = click.argument("tag")


def is_unix() -> bool:
    return (
        platform.system() in ["Linux", "Darwin"]
    )


@click.group()
def rgb() -> None:
    pass


def _stat(root_path: Path, mu: List[int] | None, alpha: float) -> dict:
    db = read_db(
        root_path / "db.json"
    )

    # in the stat list, a dict object is inited
    # one time for each of r, g, and b
    ct = { "n": len(db), "mu": mu, "alpha": alpha, "stat": [ {}, {}, {} ]}

    if not len(db) > 0:
        return db, ct

    # data is not flat, need to separate stat from the rest
    # of the info and flatten it
    db_stat = db_to_db_stat(db)

    if mu:
        for stat in ct["stat"]:
            stat["mean"] = mu
    else:
        mean(db_stat, ct)

    var(db_stat, ct)

    std_error(db_stat, ct)

    confidence_test(db_stat, ct, alpha)

    return db, ct


@rgb.command()
@root_path
@mu
@alpha
def stat(root_path: Path, mu: List[int] | None, alpha: float) -> None:
    _, ct = _stat(root_path, mu, alpha)

    # print the ct in pretty json format
    print(
        json.dumps(ct, indent=4)
    )


@rgb.command()
@root_path
@mu
@alpha
@port
@tag
def imstat(
        root_path: Path,
        mu: List[int] | None,
        alpha: float,
        port: str | None,
        tag: str) -> None:
    # take photo
    im_path = root_path / "im" / f"{tag}.jpeg"

    if is_unix():
        im = get_gphoto2_im(im_path, port)

    if not is_unix():
        im = get_digicam_im(im_path)

    im_hist = im_to_im_hist(im)
    
    write_hist(im_hist, root_path / "plot" / f"{tag}.jpeg")

    db, ct = _stat(root_path, mu, alpha)
    
    sample_mu = None

    if len(db) > 0:
        sample_mu = []

        for color in ct["stat"]:
            sample_mu.append(color["mean"])

    # in the stat list, a dict object is inited
    # one time for each of r, g, and b
    im_ct = {"tag": tag, "mu": mu or sample_mu, "alpha": alpha, "stat": [{}, {}, {}]}

    # best im format for stats
    im_stat = im_to_im_stat(im)

    mean(im_stat, im_ct)

    # median(im_stat, im_ct)

    # maximum(im_stat, im_ct)

    # minimum(im_stat, im_ct)

    # var(im_stat, im_ct)

    if len(db) > 0:
        sig_test(ct, im_ct)

    # write before appending db
    write_db(root_path / "db.json", db + [im_ct])

    im_ct["db_stat"] = ct

    print(
        json.dumps(im_ct, indent=4)
    )


@rgb.command()
@root_path
def rmstat(root_path: Path):
    db_path = root_path / "db.json"
    db = read_db(db_path)
    if db:
        im_ct = db.pop()
    else:
        im_ct = {}

    write_db(db_path, db)

    print(
        json.dumps(im_ct, indent=4)
    )
