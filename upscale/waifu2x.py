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
                    process='cudnn', crop_size=512,
                    tta_mode=0, waifu2x_path='./bin/waifu2x-caffe', waifu2x_exe='waifu2x-caffe-cui.exe'):

        cmd = ['"'+waifu2x_path+'/'+waifu2x_exe+'"',
               '-t '+str(tta_mode),
               '--gpu '+str(0),
               '-b ' + str(1),
               '-c '+str(crop_size),
               '-d '+str(output_depth),
               '-q '+str(-1),
               '-p '+process,
               '--model_dir '+'"'+waifu2x_path+'/'+model+'"',
               '-s '+str(scale_ratio),
               '-n '+str(noise_level),
               '-m '+mode,
               '-e '+output_ext,
               '-l '+input_ext,
               '-o '+output_dir,
               '-i ' + input_dir,
               ]

        # logging
        stdout = subprocess.DEVNULL
        if logger.getEffectiveLevel() == 10:  # DEBUG
            stdout = None

        # run cmd
        logger.debug(' '.join(cmd))
        subprocess.run(' '.join(cmd), stdout=stdout)

        return output_dir
