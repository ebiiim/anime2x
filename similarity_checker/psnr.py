from pathlib import Path
import math
import cv2
import numpy as np
from logging import getLogger
logger = getLogger(__name__)


class CalcPSNR:

    @staticmethod
    def calc_mse(src_a, src_b):
        diff = cv2.absdiff(src_a, src_b)
        diff = np.float32(diff)
        diff = cv2.multiply(diff, diff)

        s = cv2.sumElems(diff)
        sse = s[0] + s[1] + s[2]
        mse = sse / float(src_a.size)

        return mse

    @staticmethod
    def calc_psnr(src_a, src_b):
        mse = CalcPSNR.calc_mse(src_a, src_b)
        if mse <= 1e-10:
            return float('inf')
        return 10.0 * math.log10(255.0 * 255.0 / mse)

    @staticmethod
    def calc_psnr_frames(input_directory, output_file_name):

        f_names = [p.as_posix() for p in Path(input_directory).resolve().iterdir()]
        f_names.sort()
        logger.debug('input: ' + input_directory + ', length: ' + str(len(f_names)))
        logger.debug(f_names)

        results = ['FrameID,FileName,PSNR', ]

        file_name = f_names[0]
        prev_frame = cv2.imread(file_name)

        for i in range(1, len(f_names)):
            prev_file_name = file_name  # for logging
            file_name = f_names[i]
            now_frame = cv2.imread(file_name)
            if now_frame is None:
                break
            logger.debug('PSNR(' + prev_file_name + ', ' + file_name + ')')

            psnr = CalcPSNR.calc_psnr(prev_frame, now_frame)
            results.append(str(i+1) + ',' + file_name + ',' + str(psnr))

            prev_frame = now_frame

        outfile = Path(output_file_name).resolve().as_posix()
        with open(outfile, 'w') as f:
            f.write('\n'.join(results))

        return outfile
