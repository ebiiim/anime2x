import sys
import shutil
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from logging import getLogger
logger = getLogger(__name__)


class MovDeDup(object):

    def __init__(self, path_tmp='tmp', path_input='input', path_output='output',
                 path_bin='bin', path_ffmpeg='ffmpeg.exe'):
        self.path_tmp = Path(path_tmp).resolve()
        self.dir_input = Path(path_input).resolve()
        self.path_input = Path(self.dir_input).resolve()
        self.path_output = Path(path_output).resolve()
        self.path_bin = Path(path_bin).resolve()
        self.path_ffmpeg = (self.path_bin / path_ffmpeg).resolve()
        self._directories = [self.path_tmp, self.path_input, self.path_output, self.path_bin, ]
        self._binaries = [self.path_ffmpeg, ]
        logger.debug('_directories: ' + str(self._directories))
        logger.debug('_binaries: ' + str(self._binaries))

    def init_check(self, ):
        logger.debug('check dirs')
        for path in self._directories:
            if not path.exists():
                logger.debug('mkdir: ' + path.as_posix())
                path.mkdir()

        logger.debug('check bins')
        for path in self._binaries:
            if not path.exists():
                logger.critical('not found:' + path.as_posix())
                sys.exit(1)

    def hist_gen(self, df: pd.DataFrame, target_col_name, bins=1000,
                 range_min=0.90, range_max=1.0, cumulative=True):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        df[target_col_name].hist(ax=ax, bins=bins, range=[range_min, range_max], cumulative=cumulative)
        ax.set_xlabel(target_col_name)
        ax.set_ylabel('Freq.')
        ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.4g'))
        # ax.set_title('Similarity')
        # plt.plot()
        # fig.show()
        plt.savefig(self.path_output.joinpath(datetime.datetime.now().strftime('%Y%m%d%H%M%SZ') + '.png'))

    @staticmethod
    def load_similarity_csv(similarity_csv) -> pd.DataFrame:
        df = pd.read_csv(similarity_csv, index_col=0)
        logger.debug(df.head(3))
        logger.debug(df.info())
        logger.debug(df.describe())
        return df

    @staticmethod
    def get_copy_lists(df: pd.DataFrame, target_col_name, threshold):
        """
        (src_list, del_list)を返す。
        del_listは閾値以上のファイル名を格納したリスト。
        src_listはdel_listの1個前のファイル名を格納したリスト。
        利用方法: del_listのファイルを削除して、src_listのファイルをdel_listの同indexのファイル名で保存する。
        """
        col_filename = 'FileName'

        # 重複フレームのindexを取得
        copy_index_list = df[df[target_col_name] >= threshold].index

        # 重複率の表示
        logger.info('similarity_threshold: ' + str(threshold))
        lo = len(df)
        lc = len(copy_index_list)
        logger.info('length_original: ' + str(lo))
        logger.info('length_copy: ' + str(lc))
        logger.info('rate: ' + str(lc/lo))

        # コピー元ファイル名リストとコピー先ファイル名リストを作る
        src_list = list()
        del_list = list()
        for each in copy_index_list:
            # コピー元ファイル名リスト
            for n in range(each - 1):  # range(each)だと1枚目まで見に行く、2枚目開始なのでrange(each - 1)
                # n枚前が重複でない場合は採用（重複なら飛ばす）
                if list(df.query('index == ' + str(each - n))[target_col_name])[0] < threshold:
                    src_list.extend(list(df.query('index == ' + str(each - n))[col_filename]))
                    break
            # コピー先ファイル名リスト
            del_list.extend(list(df.query('index == ' + str(each))[col_filename]))

        return list(del_list), list(src_list)

    def copy_dedup(self, del_list):
        """
        input/のファイルをdel_listを除きすべてindex/からtmp/にコピーする。
        """
        input_name_list = [p.name for p in Path(self.dir_input).iterdir()]
        del_name_list = [Path(p).name for p in del_list]
        dedup_name_list = list(set(input_name_list) - set(del_name_list))
        dedup_list = [self.dir_input.joinpath(f) for f in dedup_name_list]
        logger.debug('dedup_list: ' + str(dedup_list))
        logger.info('len(dedup_list): ' + str(len(dedup_list)))
        for file in dedup_list:
            copy_src = file
            copy_dst = self.path_tmp.joinpath(file.name)
            shutil.copy2(copy_src, copy_dst)
            logger.debug('copy: ' + copy_src.as_posix() + ' -> ' + copy_dst.as_posix())

    def copy_dup(self, dup_list, src_list):
        """
        input/のsrc_listに記載のファイルをdup_listに記載の名前でtmp/からtmp/にコピーする。
        """
        for (dup, src) in zip(dup_list, src_list):
            copy_src = self.path_tmp / Path(src).name
            copy_dst = self.path_tmp / Path(dup).name
            shutil.copy2(copy_src, copy_dst)
            logger.debug('copy: ' + copy_src.as_posix() + ' -> ' + copy_dst.as_posix())
