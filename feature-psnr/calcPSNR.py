import math
import cv2
import subprocess
import numpy as np


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
    def calc_psnr_frames(input_directory, output_fileName):

        # フレーム数の検出
        cmd = 'ls ' + input_directory
        out = subprocess.check_output(cmd.split()).decode('utf-8')
        f_names = out.split()

        csvFile = open(output_fileName, 'w')
        csvFile.write('FrameID,FileName,PSNR\n')

        fileName = input_directory + '/' + f_names[0]
        prev_frame = cv2.imread(fileName)
        print(fileName)

        for i in range(1, len(f_names)):

            fileName = input_directory + '/' + f_names[i]
            now_frame = cv2.imread(fileName)
            if now_frame is None:
                break
            print(fileName)

            psnr = CalcPSNR.calc_psnr(prev_frame, now_frame)
            csvFile.write(str(i+1) + ',' + fileName + ',' + str(psnr) + '\n')

            prev_frame = now_frame

        return None
