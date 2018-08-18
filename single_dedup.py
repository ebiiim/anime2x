import os
import sys
import subprocess
import datetime
from de_duplication import mov_dedup as m
from logging import getLogger
logger = getLogger(__name__)


if __name__ == '__main__':
    import logging
    LOG_LEVEL = logging.DEBUG
    LOG_FMT = "%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s"
    logging.basicConfig(format=LOG_FMT, level=LOG_LEVEL)

    mdp = m.MovDeDup()
    mdp.init_check()

    if len(sys.argv) < 3:
        print('Usage: single_dedup.py CMD [SSIM_THRESHOLD] SIMILARITY_CSV_FILE\n'
              '\tCMD hist: Generate a histogram\n'
              '\tCMD check: Check duplicate images\n'
              '\tCMD copy1: Copy de-duplicated images to /tmp\n'
              '\tCMD copy2: Copy filtered images to /tmp\n'
              '\tCMD enc: Encode images in /tmp to a mp4 file\n'
              'Example: single_dedup.py hist ./similarity.csv\n'
              'Example: single_dedup.py check 0.85 ./similarity.csv\n'
              'Example: single_dedup.py copy1 0.85 ./similarity.csv\n'
              'Example: single_dedup.py copy2 0.85 ./similarity.csv\n'
              'Example: single_dedup.py enc ./similarity.csv\n'
              )
        sys.exit(0)

    ssim_col_name = 'SSIM(Whole)'

    if sys.argv[1] == 'hist':
        data = mdp.load_similarity_csv(sys.argv[2])
        mdp.ssim_hist_gen(data, ssim_col_name)

    if sys.argv[1] == 'check':
        data = m.MovDeDup.load_similarity_csv(sys.argv[3])
        m.MovDeDup.get_copy_lists(data, ssim_col_name, float(sys.argv[2]))

    if sys.argv[1] == 'copy1':
        data = m.MovDeDup.load_similarity_csv(sys.argv[3])
        del_l, src_l = m.MovDeDup.get_copy_lists(data, ssim_col_name, float(sys.argv[2]))
        mdp.copy_dedup(del_l)

    if sys.argv[1] == 'copy2':
        data = m.MovDeDup.load_similarity_csv(sys.argv[3])
        del_l, src_l = m.MovDeDup.get_copy_lists(data, ssim_col_name, float(sys.argv[2]))
        mdp.copy_dup(del_l, src_l)

    if sys.argv[1] == 'enc':
        # TODO: ffmpegのオプションを変更可能にする。現在は固定なのでファイル名など注意。
        encode_mp4 = [mdp.path_ffmpeg,
                      '-r 24',
                      '-i ' + mdp.path_tmp + '/image_%8d.png',
                      '-vcodec libx265 -preset fast -tune ssim -crf 22',
                      mdp.path_output + '/tmp.mp4',
                      ]

        add_sound = [mdp.path_ffmpeg,
                     '-i ' + mdp.path_output + '/tmp.mp4',
                     '-i ' + mdp.path_output + '/audio.aac',  # XXX: audio.aacをself.path_outputに置いてください！
                     '-vcodec copy',
                     '-acodec copy',
                     mdp.path_output + '/' + datetime.datetime.now().strftime('%Y%m%d%H%M%SZ') + '.mp4'
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

        os.remove(mdp.path_output + '/tmp.mp4')
