"""
Usage:
  anime2x.exe INPUT_FILE OUTPUT_FILE
              [--threshold=<psnr_value>] [--divide_x=<div_x>] [--divide_y=<div_y>]
              [--waifu2x_scale=<scale>] [--waifu2x_crop=<crop>] [--ffmpeg_vcodec=<vcodec>]
              [--ffmpeg_preset=<preset>] [--ffmpeg_tune=<tune>] [--ffmpeg_crf=<crf>]
              [--resize --resize_w=<width> --resize_h=<height>]
              [--no-cleanup] [--log-level=<level>]
  anime2x.exe --help
  anime2x.exe --version

Arguments:
  INPUT_FILE                Input file (e.g. input.mp4).
  OUTPUT_FILE               Output file (e.g. output.mp4).
  --threshold=<psnr_value>  Deduplication PSNR threshold, low value makes the video jittery [default: 55].
  --divide_x=<div_x>        Number of divisions on x axis [default: 8].
  --divide_y=<div_y>        Number of divisions on y axis [default: 6].
  --waifu2x_scale=<scale>   waifu2x-caffe scale ratio [default: 2].
  --waifu2x_crop=<crop>     waifu2x-caffe crop size [default: 128].
  --ffmpeg_vcodec=<vcodec>  FFmpeg vcodec [default: libx265].
  --ffmpeg_preset=<preset>  FFmpeg preset [default: slow].
  --ffmpeg_tune=<tune>      FFmpeg tune [default: ssim].
  --ffmpeg_crf=<crf>        FFmpeg crf [default: 22].
  --resize_w=<width>        Resize width of the output video to <width> if the -r option is set [default: 2560].
  --resize_h=<height>       Resize height of the output video to <height> if the -r option is set [default: 1440].
  --log-level=<level>       Python log level (DEBUG, INFO, WARNING, CRITICAL) [default: INFO].

Options:
  -r --resize               Resize the output video with the Lanczos 3 algorithm.
  -n --no-cleanup           Do not clean up cache files after conversion.
  -h --help                 Display this help and exit.
  -v --version              Output version information and exit.
"""

import os
import time
from pathlib import Path
import shutil
from docopt import docopt
from divide_conquer.divider import MovDivider
from divide_conquer.combiner import MovCombiner
from de_duplication.mdedup import MultiDeDup
from similarity_checker.psnr import CalcPSNR
from de_duplication.movconv import MovieConverter
from upscaling.waifu2x import Waifu2xUpscaler
from logging import getLogger
logger = getLogger(__name__)


def run_all(input_file, output_file, threshold, divide_w, divide_h, waifu2x_scale_ratio, waifu2x_crop_size,
            ffmpeg_vcodec, ffmpeg_preset, ffmpeg_tune, ffmpeg_crf, ffmpeg_resize, ffmpeg_resize_w, ffmpeg_resize_h,
            cleanup):
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
    divided_dirs = MovDivider.divide_images(tmp_dir, int(divide_w), int(divide_h))
    logger.info('calc PSNR')
    for idx, each in enumerate(divided_dirs):
        CalcPSNR.calc_psnr_frames(each, Path(each).parent.joinpath('psnr_' + '{:04g}'.format(idx + 1) + '.csv'))
    logger.info('copy unique images')
    copied_dirs = MultiDeDup.multi_copy1(divided_dirs, int(threshold))
    logger.info('waifu2x')
    for each in copied_dirs:
        Waifu2xUpscaler.upscale_dir(each, each, scale_ratio=int(waifu2x_scale_ratio), crop_size=int(waifu2x_crop_size))
    logger.info('copy duplicated images')
    MultiDeDup.multi_copy2(divided_dirs, int(threshold))
    logger.info('combine images')
    copied_dir = Path(copied_dirs[0]).resolve().parent
    combined_dir = MovCombiner.combine_images(copied_dir, int(divide_w), int(divide_h))
    logger.info('convert images to video')
    p2m_out = MovieConverter.pic2mov(input_dir=combined_dir, output_file='tmp-movie.mp4', fps=fps,
                                     vcodec=ffmpeg_vcodec, preset=ffmpeg_preset, tune=ffmpeg_tune, crf=int(ffmpeg_crf),
                                     resize=ffmpeg_resize, resize_w=int(ffmpeg_resize_w), resize_h=int(ffmpeg_resize_h))
    logger.info('mix audio and video')
    MovieConverter.mix(p2m_out, sound_file, output_file)
    if cleanup:
        [os.remove(f) for f in [sound_file, p2m_out, ]]
        [shutil.rmtree(d) for d in [tmp_dir, Path(divided_dirs[0]).resolve().parent, copied_dir, combined_dir]]

    logger.info('completed')
    elapsed_time = time.time() - start_time
    logger.info(time.strftime('elapsed time: %H:%M:%S', time.gmtime(elapsed_time)))


if __name__ == '__main__':
    args = docopt(__doc__, version='0.3.0')
    # print(args)

    import logging
    log_level = args['--log-level']
    if log_level == 'DEBUG':
        log_level = logging.DEBUG
    elif log_level == 'INFO':
        log_level = logging.INFO
    elif log_level == 'WARN' or 'WARNING':
        log_level = logging.WARNING
    elif log_level == 'CRITCAL':
        log_level = logging.CRITICAL
    LOG_FMT = "%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s"
    logging.basicConfig(format=LOG_FMT, level=log_level)

    # print('input_file', args['INPUT_FILE'], 'output_file', args['OUTPUT_FILE'],
    #       'threshold',args['--threshold'],
    #       'divide_w',args['--divide_x'], 'divide_h', args['--divide_y'],
    #       'waifu2x_scale_ratio', args['--waifu2x_scale'], 'waifu2x_crop_size', args['--waifu2x_crop'],
    #       'ffmpeg_vcodec', args['--ffmpeg_vcodec'], 'ffmpeg_preset', args['--ffmpeg_preset'],
    #       'ffmpeg_tune', args['--ffmpeg_tune'], 'ffmpeg_crf', args ['--ffmpeg_crf'],
    #       'ffmpeg_resize', args['--resize'], 'ffmpeg_resize_w', args['--resize_w'], 'ffmpeg_resize_h', args['--resize_h'],
    #       'cleanup', not args['--no-cleanup'])

    run_all(input_file=args['INPUT_FILE'], output_file=args['OUTPUT_FILE'],
            threshold=args['--threshold'],
            divide_w=args['--divide_x'], divide_h=args['--divide_y'],
            waifu2x_scale_ratio=args['--waifu2x_scale'], waifu2x_crop_size=args['--waifu2x_crop'],
            ffmpeg_vcodec=args['--ffmpeg_vcodec'], ffmpeg_preset=args['--ffmpeg_preset'],
            ffmpeg_tune=args['--ffmpeg_tune'], ffmpeg_crf=args['--ffmpeg_crf'],
            ffmpeg_resize=args['--resize'], ffmpeg_resize_w=args['--resize_w'], ffmpeg_resize_h=args['--resize_h'],
            cleanup=not args['--no-cleanup'])
