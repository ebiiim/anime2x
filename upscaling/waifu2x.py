from pathlib import Path
import subprocess
from logging import getLogger
logger = getLogger(__name__)


class Waifu2xUpscaler(object):

    @staticmethod
    def upscale_dir(input_dir, output_dir,
                    input_ext='png', output_ext='png', output_depth=8,
                    model='models/upconv_7_photo',
                    scale_ratio=2, mode='noise_scale', noise_level=1,
                    # crop_w=None, crop_h=None,
                    process='cudnn', crop_size=512, gpu_id=0,
                    tta_mode=0, waifu2x_path='./bin/waifu2x-caffe', waifu2x_exe='waifu2x-caffe-cui.exe'):

        cmd = ['"'+Path(waifu2x_path).joinpath(waifu2x_exe).resolve().as_posix()+'"',
               '-t '+str(tta_mode),
               '--gpu '+str(gpu_id),
               '-b '+str(1),
               '-c '+str(crop_size),
               '-d '+str(output_depth),
               '-q '+str(-1),
               '-p '+process,
               '--model_dir '+Path(waifu2x_path).joinpath(model).resolve().as_posix(),
               '-s '+str(scale_ratio),
               '-n '+str(noise_level),
               '-m '+mode,
               '-e '+output_ext,
               '-l '+input_ext,
               '-o '+Path(output_dir).resolve().as_posix(),
               '-i '+Path(input_dir).resolve().as_posix(),
               ]

        # logging
        stdout = subprocess.DEVNULL
        if logger.getEffectiveLevel() == 10:  # DEBUG
            stdout = None

        # run cmd
        logger.debug(' '.join(cmd))
        subprocess.run(' '.join(cmd), stdout=stdout)

        return Path(output_dir).resolve().as_posix()
