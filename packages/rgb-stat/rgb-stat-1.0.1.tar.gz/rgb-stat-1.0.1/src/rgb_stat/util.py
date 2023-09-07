""""""

import cv2
import subprocess
from pathlib import Path
import json
from typing import List
import os
from matplotlib import pyplot as plt


def db_to_db_stat(db):
    db_stat = [ [], [], [] ]

    for im in db:
        for i, stat in enumerate(im["stat"]):
            db_stat[i].append(stat["mean"])
    
    return db_stat


def im_to_im_hist(im: cv2.typing.MatLike) -> List[cv2.UMat]:
    im_hist = []

    for i in [0, 1, 2]:
        im_hist.append(
            cv2.calcHist(
                [im],
                # cv2 indexes blue to red, but we are indexing
                # red to blue
                [2 - i],
                # want the entire image, no subset
                None,
                # one bucket for each rgb value
                [256],
                [0, 256])
        )

    return im_hist


def im_to_im_stat(im: cv2.typing.MatLike) -> List[cv2.UMat]:
    im_stat = []

    for i, im_x in enumerate(
        cv2.split(im)[::1]
    ):
        im_stat.append(
            im_x.flatten()
        )

    return im_stat


def create_dir(path: str) -> None:
    Path(path).parent.mkdir(exist_ok=True)


def write_hist(im_hist: List[cv2.UMat], hist_path: str) -> None:
    color = ["r", "g", "b"]

    for i, im_x in enumerate(im_hist):
        plt.plot(im_x, color[i])

    plt.title(f"Count of Pixel per RGB Bucket [0, 256]")
    plt.xlabel("rgb_bucket")
    plt.ylabel("n_pixel")

    create_dir(hist_path)

    plt.savefig(hist_path)


def read_db(db_path):
    if db_path.exists():
        if db_path.stat().st_size > 0:
            with open(db_path, "r") as dbfile:
                return json.load(dbfile)
    
    return []


def write_db(db_path, db):
    with open(db_path, "w") as dbfile:
        json.dump(db, dbfile, indent=4)
