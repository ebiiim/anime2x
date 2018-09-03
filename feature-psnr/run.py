import sys
import calcPSNR


if __name__ == '__main__':

    # 処理対象設定
    if len(sys.argv) < 3:
        usage_str = 'Usage: python run.py [INPUT_DIR] [OUTPUT_FILENAME] \n' \
                    'Example: python run.py ./input ./output.csv'
        print(usage_str)
        sys.exit(0)

    input_directory = sys.argv[1]
    output_fileName = sys.argv[2]
    
    calcPSNR.CalcPSNR.calc_psnr_frames(input_directory, output_fileName)
