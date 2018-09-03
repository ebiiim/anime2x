import sys
import math
import cv2
import subprocess
import numpy as np


def calcMSE(src_a, src_b):
    diff = cv2.absdiff(src_a, src_b)
    diff = np.float32(diff)
    diff = cv2.multiply(diff, diff)
    
    s = cv2.sumElems(diff)
    sse = s[0] + s[1] + s[2]
    mse = sse / float(src_a.size)

    return mse

def calcPSNR(src_a, src_b):
    mse = calcMSE(src_a, src_b)
    if mse <= 1e-10:
        return float('inf')
    return 10.0 * math.log10(255.0 * 255.0 / mse)

def calcPSNR_Frames(input_directory, output_fileName):

    # フレーム数の検出
    cmd = 'ls ' + input_directory
    out = subprocess.check_output(cmd.split()).decode('utf-8')
    f_names = out.split()

    csvFile = open(output_fileName, 'w')
    csvFile.write('frame_ID,PSNR\n')

    prev_frame = cv2.imread(input_directory + '/' + f_names[0])
    for i in range(1, len(f_names)):
        print(input_directory + '/' + f_names[i])

        now_frame = cv2.imread(input_directory + '/' + f_names[i])
        if now_frame is None:
            break

        psnr = calcPSNR(prev_frame, now_frame)
        csvFile.write(str(i+1) + ',' + str(psnr) + '\n')

        prev_frame = now_frame

    return None


if __name__ == '__main__':

    # 処理対象設定
    if len(sys.argv) < 3:
        usage_str = 'Usage: python run.py [INPUT_DIR] [OUTPUT_FILENAME] \n' \
                    'Example: python run.py ./input ./output.csv'
        print(usage_str)
        sys.exit(0)

    input_directory = sys.argv[1]
    output_fileName = sys.argv[2]

    calcPSNR_Frames(input_directory, output_fileName)
