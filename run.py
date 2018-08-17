import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from logging import getLogger
logger = getLogger(__name__)

PATH_SELF = os.path.dirname(os.path.abspath(__file__))
PATH_TMP = PATH_SELF + '/tmp'
PATH_INPUT = PATH_SELF + '/input'
PATH_OUTPUT = PATH_SELF + '/output'
PATH_BIN = PATH_SELF + '/bin'
PATH_FFMPEG = PATH_BIN + '/ffmpeg.exe'
_directories = [PATH_TMP, PATH_INPUT, PATH_OUTPUT, PATH_BIN, ]
_binaries = [PATH_FFMPEG, ]


def init_check():
    logger.debug('check dirs')
    for path in _directories:
        if not os.path.exists(path):
            logger.debug('mkdir: ' + path)
            os.makedirs(path)

    logger.debug('check bins')
    for path in _binaries:
        if not os.path.exists(path):
            logger.critical('not found:' + path)
            sys.exit(1)


def ssim_hist_gen(target: pd.Series, bins=10, min_ssim=0.0, max_ssim=1.0, cumulative=True):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    target.hist(ax=ax, bins=bins, range=[min_ssim, max_ssim], cumulative=cumulative)
    ax.set_xlabel('SSIM')
    ax.set_ylabel('Freq.')
    ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.4g'))
    # ax.set_title('Similarity')
    # plt.plot()
    # fig.show()
    plt.savefig(PATH_OUTPUT + '/' + datetime.datetime.now().strftime('%Y%m%d%H%M%SZ') + '.png')


def load_similarity_csv(similarity_csv) -> pd.DataFrame:
    df = pd.read_csv(similarity_csv, index_col=0)
    print(df.head(3))
    print(df.info())
    print(df.describe())
    return df


def get_copy_lists(df: pd.DataFrame, target: pd.Series, ssim_threshold):
    """
    (src_list, del_list)を返す。
    del_listはSSIMしきい値以上のファイル名を格納したリスト。
    src_listはdel_listの1個前のファイル名を格納したリスト。
    利用方法: del_listのファイルを削除して、src_listのファイルをdel_listの同indexのファイル名で保存する。
    """
    col_filename = 'FileName'
    copy_index_list = df[target >= ssim_threshold].index

    logger.debug('ssim_threshold: ' + str(ssim_threshold))
    lo = len(df)
    lc = len(copy_index_list)
    logger.debug('length_original: ' + str(lo))
    logger.debug('length_copy: ' + str(lc))
    logger.debug('rate: ' + str(lc/lo))

    src_list = list()
    del_list = list()
    for each in copy_index_list:
        src_list.extend(list(df.query('index == ' + str(each - 1))[col_filename]))
        del_list.extend(list(df.query('index == ' + str(each))[col_filename]))

    return list(del_list), list(src_list)


if __name__ == '__main__':
    import logging
    LOG_LEVEL = logging.DEBUG
    LOG_FMT = "%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s"
    logging.basicConfig(format=LOG_FMT, level=LOG_LEVEL)

    init_check()

    if len(sys.argv) < 3:
        print('Usage: run.py MODE [SSIM_THRESHOLD] SIMILARITY_CSV_FILE\n'
              '\tMODE hist: Generate a histogram\n'
              '\tMODE check: Check duplicate images\n'
              '\tMODE copy: Copy images\n'
              '\tMODE enc: Encode images to a mp4 file\n'
              'Example: run.py hist ./similarity.csv\n'
              'Example: run.py check 0.85 ./similarity.csv\n'
              'Example: run.py copy 0.85 ./similarity.csv\n'
              'Example: run.py enc ./similarity.csv\n'
              )
        sys.exit(0)

    if sys.argv[1] == 'hist':
        data = load_similarity_csv(sys.argv[2])
        ssim_hist_gen(data['SSIM(Whole)'], bins=1000, min_ssim=0.90, cumulative=True)

    if sys.argv[1] == 'check':
        data = load_similarity_csv(sys.argv[3])
        src_l, del_l = get_copy_lists(data, data['SSIM(Whole)'], float(sys.argv[2]))
        print(del_l)

    if sys.argv[1] == 'copy':
        data = load_similarity_csv(sys.argv[3])
        src_l, del_l = get_copy_lists(data, data['SSIM(Whole)'], float(sys.argv[2]))
        pass

    if sys.argv[1] == 'enc':
        pass
