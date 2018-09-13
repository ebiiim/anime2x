import os
import sys
import shutil
from zipfile import ZipFile
from pathlib import Path
import requests
from logging import getLogger
logger = getLogger(__name__)

URL_CV = {
    '343_P35': 'https://download.lfd.uci.edu/pythonlibs/o4uhg4xd/opencv_python-3.4.3-cp35-cp35m-win_amd64.whl',
    '343_P36': 'https://download.lfd.uci.edu/pythonlibs/o4uhg4xd/opencv_python-3.4.3-cp36-cp36m-win_amd64.whl',
    '343_P37': 'https://download.lfd.uci.edu/pythonlibs/o4uhg4xd/opencv_python-3.4.3-cp37-cp37m-win_amd64.whl',
}
URL_FFM = {
    '402': 'https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-4.0.2-win64-static.zip',
}
URL_W2XC = {
    '1184': 'https://github.com/lltcggie/waifu2x-caffe/releases/download/1.1.8.4/waifu2x-caffe.zip'
}


def download_url(url, save_dir, content=False):
    save_dir = Path(save_dir)
    if not save_dir.exists():
        save_dir.mkdir()
    path = save_dir.resolve().joinpath(url.split('/')[-1])
    if path.exists():
        logger.info('Found: ' + path.as_posix())
    else:
        logger.info('Download : ' + url)
        res = requests.get(url, stream=True)
        with open(path, "wb") as fp:
            if content:
                fp.write(res.content)
            else:
                shutil.copyfileobj(res.raw, fp)
        logger.info('Saved : ' + path.as_posix())
    return path


def download_dependencies():
    bin_base_dir = Path('./bin')
    if not bin_base_dir.exists():
        bin_base_dir.mkdir()
    bin_base_dir = bin_base_dir.resolve().as_posix()

    # ffmpeg
    path_ffm_z = download_url(URL_FFM['402'], bin_base_dir, content=True)
    path_ffm = Path(path_ffm_z).parent.joinpath(Path(path_ffm_z).stem)
    path_ffm_exe = path_ffm.joinpath('bin/ffmpeg.exe')
    with ZipFile(path_ffm_z) as zip_:
        zip_.extractall(bin_base_dir)
    shutil.copy2(path_ffm_exe.as_posix(), Path(bin_base_dir).joinpath('ffmpeg.exe'))
    shutil.rmtree(path_ffm.as_posix())
    os.remove(path_ffm_z.as_posix())

    # waifu2x-caffe
    path_w2xc_z = download_url(URL_W2XC['1184'], bin_base_dir, content=True)
    with ZipFile(path_w2xc_z) as zip_:
        zip_.extractall(bin_base_dir)
    os.remove(path_w2xc_z.as_posix())

    # opencv-python binary
    url_cv = URL_CV['343_P3'+str(sys.version_info.minor)]
    download_url(url_cv, '.', content=True)


if __name__ == '__main__':
    import logging
    LOG_FMT = "%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s"
    LOG_LEVEL = logging.INFO
    logging.basicConfig(format=LOG_FMT, level=LOG_LEVEL)

    download_dependencies()
