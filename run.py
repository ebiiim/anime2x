import os
import subprocess
import datetime
from divide_conquer import divider as d
from divide_conquer import combiner as c
from de_duplication import mdedup as mdd
from logging import getLogger
logger = getLogger(__name__)

if __name__ == '__main__':
    import logging

    # ロギング設定
    LOG_FMT = "%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s"
    LOG_LEVEL = logging.DEBUG

    # 分割設定
    DIVIDE_W = 4
    DIVIDE_H = 3
    SRC_DIR = './input'  # './hoge' のみ対応（'./hoge/hogehoge' などは途中でエラーが出ますorz）

    # コピー設定
    # METRICS = 'PSNR'  # (未使用) 'PSNR' or 'SSIM' or ...
    THRESHOLD = 55

    # エンコード設定
    DO_ENCODE = True
    DST_DIR = './output'  # audio.aacをDST_DIRに置いてください！
    FRAME_RATE = 24

    logging.basicConfig(format=LOG_FMT, level=LOG_LEVEL)

    # 処理
    # 1. 分割
    divided_dirs = d.MovDivider.divide_images(SRC_DIR, DIVIDE_W, DIVIDE_H)
    # 2. コピー1
    mdd.MultiDeDup.multi_copy1(divided_dirs, THRESHOLD)  # similarity*.csvがあることを確認してください！
    # 3. コピー2
    copied_dirs = mdd.MultiDeDup.multi_copy2(divided_dirs, THRESHOLD)
    # 4. 結合
    # ひどすぎるパス処理
    copied_dirs_root_for_combiner = copied_dirs[0].split('/')[-3].replace('-'+str(DIVIDE_W)+'_'+str(DIVIDE_H), '')
    output_dir = c.MovCombiner.combine_images(copied_dirs_root_for_combiner, DIVIDE_W, DIVIDE_H)
    # 5. エンコード
    if DO_ENCODE:
        path_ffmpeg = './bin/ffmpeg.exe'
        path_tmp = './' + output_dir
        path_output = './output'
        encode_mp4 = [path_ffmpeg,
                      '-r ' + str(FRAME_RATE),
                      '-i ' + path_tmp + '/image_%8d.png',
                      '-vcodec libx265 -preset fast -tune ssim -crf 22',
                      path_output + '/tmp.mp4',
                      ]

        add_sound = [path_ffmpeg,
                     '-i ' + path_output + '/tmp.mp4',
                     '-i ' + path_output + '/audio.aac',
                     '-vcodec copy',
                     '-acodec copy',
                     path_output + '/' + datetime.datetime.now().strftime('%Y%m%d%H%M%SZ') + '.mp4'
                     ]

        # logging
        stdout = subprocess.DEVNULL
        if logger.getEffectiveLevel() == 10:  # DEBUG
            stdout = None

        # run cmd
        logger.debug(' '.join(encode_mp4))
        subprocess.run(' '.join(encode_mp4), stdout=stdout)

        logger.debug(' '.join(add_sound))
        subprocess.run(' '.join(add_sound), stdout=stdout)

        os.remove(path_output + '/tmp.mp4')
