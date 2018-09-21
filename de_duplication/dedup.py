import sys
import shutil
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from logging import getLogger
logger = getLogger(__name__)


class MovDeDup(object):
    # /path/to/project_root/bin/ffmpeg/bin/ffmpeg.exe
    FFMPEG_PATH = Path(__file__+'/../../bin/ffmpeg/bin/ffmpeg.exe').resolve().as_posix()

    def __init__(self, path_tmp='tmp', path_input='input', path_output='output',
                 path_bin='bin', path_ffmpeg=FFMPEG_PATH):
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
    def get_copy_lists(similarity_file_path: str, threshold):
        """
        similarityのcsvファイルを読み込んで、(src_list, del_list)を返す。
        del_listは閾値以上のファイル名を格納したリスト。
        src_listはdel_listの1個前の重複しないファイルのファイル名を格納したリスト。
        利用方法: del_listのファイルを削除して、src_listのファイルをdel_listの同indexのファイル名で保存する。
        CSVファイルのフォーマット: `FrameID,FileName,PSNR`, 1行目はヘッダ(データを格納しない)
        """
        csv_ = []
        with open(similarity_file_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                csv_.append(row)

        # delete the header and cast `FrameID` and `PSNR` values
        data = [[int(l[0]), l[1], float(l[2])] for l in csv_[1:]]

        # 重複フレームのindexを取得
        copy_index_list = [l[0] for l in data if l[2] >= threshold]

        # 重複率の表示
        logger.info('similarity_threshold: ' + str(threshold))
        lo = len(data)
        lc = len(copy_index_list)
        logger.info('length_original: ' + str(lo))
        logger.info('length_copy: ' + str(lc))
        logger.info('rate: ' + str(lc/lo))

        # コピー元ファイル名リストとコピー先ファイル名リストを作る
        src_list = list()
        del_list = list()
        for each in copy_index_list:
            # コピー元ファイル名リスト
            src_idx = each-1-1  # FrameID=2はdata[1]なのでoffsetが-1, デフォルトは1枚前を採用するのでさらに-1
            for n in range(each):
                # n枚前が重複でない場合は採用（重複なら飛ばす）
                if data[each-1-n][2] < threshold:
                    src_idx = each-n-1
                    break
            src_list.append(data[src_idx][1])
            # コピー先ファイル名リスト
            del_list.append(data[each-1][1])

        logger.debug('del_list: ' + str(del_list))
        logger.debug('src_list: ' + str(src_list))
        logger.info('len(del_list): ' + str(len(del_list)))
        logger.info('len(src_list): ' + str(len(src_list)))
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
