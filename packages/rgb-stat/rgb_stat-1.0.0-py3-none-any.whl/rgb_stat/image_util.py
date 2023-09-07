""""""

from pathlib import Path
import psutil
import subprocess
import cv2
import numpy as np

from .util import create_dir


class GPhoto2Error(Exception):
    pass


class DigicamError(Exception):
    pass


def get_gphoto2_im(im_path: Path, port: str) -> cv2.typing.MatLike:
    import gphoto2

    # python-gphoto2 can only access the camera if another
    # process has not locked it
    for proc in psutil.process_iter():
        if proc.is_running() and "gphoto2" in proc.name():
            proc.terminate()

    cameras = gphoto2.Camera.autodetect()

    # if port specified, use it, but default to the
    # first camera found
    if port:
        for name, _port in cameras:
            if port == _port:
                break
        else:
            raise GPhoto2Error(
                f"No camera found at port '{port}'.")
    else:
        if cameras:
            name, port = cameras[0]
        else:
            raise GPhoto2Error("No camera detected.")

    camera = gphoto2.Camera()

    pi = gphoto2.PortInfoList()
    pi.load()
    n_pi = pi.lookup_path(port)
    camera.set_port_info(pi[n_pi])

    ab = gphoto2.CameraAbilitiesList()
    ab.load()
    n_ab = ab.lookup_model(name)
    camera.set_abilities(ab[n_ab])

    camera.init()
    fp_info = camera.capture(gphoto2.GP_CAPTURE_IMAGE)
    fp_data = camera.file_get(
        fp_info.folder, fp_info.name, gphoto2.GP_FILE_TYPE_NORMAL)
    data = memoryview(
        fp_data.get_data_and_size()
    )
    im_np = np.frombuffer(data, np.uint8)
    im = cv2.imdecode(im_np, cv2.IMREAD_COLOR)

    create_dir(im_path)

    cv2.imwrite(str(im_path), im)

    return im


def get_digicam_im(im_path: Path) -> cv2.typing.MatLike:
    sub = subprocess.Popen(
        "CameraControlCmd", "/filename", im_path, "/capture",
        timeout=10, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        sub.wait(timeout)
    except subprocess.TimeoutExpired as e:
        raise DigicamError(
            f"{e.cmd} exceeded the "
            f"timeout of {e.timeout}.")
    
    if sub.returncode > 0:
        raise DigicamError(
            f"{e.cmd} failed and returned a nonzero exit code. "
            f"Error: {e.stderr}")

    return sub

    im = cv2.imread(im_path, cv2.IMREAD_COLOR)

    return im
