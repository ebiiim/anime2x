import time
from pathlib import Path
import shutil
from divide_conquer.divider import MovDivider
from divide_conquer.combiner import MovCombiner
from de_duplication.mdedup import MultiDeDup
from similarity_checker.psnr import CalcPSNR
from de_duplication.movconv import MovieConverter
from upscaling.waifu2x import Waifu2xUpscaler
from logging import getLogger
logger = getLogger(__name__)


def run_all(input_file='input-movie.mp4', output_file='output-movie.mp4',
            threshold=55, divide_w=4, divide_h=3, cleanup = True):
    logger.info('Input/Output: '+input_file+' -> '+output_file)
    logger.info('PSNR Threshold: '+str(threshold))
    logger.info('divide(W, H): ('+str(divide_w)+', '+str(divide_h)+')')
    start_time = time.time()

    logger.info('start')
    fps = MovieConverter.probe_file(input_file)
    logger.info('extract audio')
    sound_file = 'tmp-sound.mp4'
    MovieConverter.extract_audio(input_file, sound_file)
    logger.info('convert video to images')
    tmp_dir = MovieConverter.mov2pic(input_file, 'tmp-input')
    logger.info('divide images')
    divided_dirs = MovDivider.divide_images(tmp_dir, divide_w, divide_h)
    logger.info('calc PSNR')
    for idx, each in enumerate(divided_dirs):
        CalcPSNR.calc_psnr_frames(each, Path(each).parent.joinpath('psnr_' + '{:04g}'.format(idx + 1) + '.csv'))
    logger.info('copy unique images')
    copied_dirs = MultiDeDup.multi_copy1(divided_dirs, threshold)
    logger.info('waifu2x')
    for each in copied_dirs:
        Waifu2xUpscaler.upscale_dir(each, each)
    logger.info('copy duplicated images')
    MultiDeDup.multi_copy2(divided_dirs, threshold)
    logger.info('combine images')
    copied_dir = Path(copied_dirs[0]).resolve().parent
    combined_dir = MovCombiner.combine_images(copied_dir, divide_w, divide_h)
    logger.info('convert images to video')
    p2m_out = MovieConverter.pic2mov(input_dir=combined_dir, output_file='tmp-movie.mp4', fps=fps, preset='fast')
    logger.info('mix audio and video')
    MovieConverter.mix(p2m_out, sound_file, output_file)
    if cleanup:
        logger.info('cleanup')
        for each in [sound_file, tmp_dir, Path(divided_dirs[0]).resolve().parent, copied_dir, p2m_out]:
            shutil.rmtree(each)
    logger.info('completed')

    elapsed_time = time.time() - start_time
    logger.info(time.strftime('elapsed time: %H:%M:%S', time.gmtime(elapsed_time)))


if __name__ == '__main__':
    import logging
    LOG_FMT = "%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s"
    LOG_LEVEL = logging.INFO
    logging.basicConfig(format=LOG_FMT, level=LOG_LEVEL)

    run_all(cleanup=False)
