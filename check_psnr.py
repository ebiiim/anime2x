import sys
from similarity_checker import psnr


if __name__ == '__main__':
    import logging

    LOG_FMT = "%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s"
    LOG_LEVEL = logging.DEBUG
    logging.basicConfig(format=LOG_FMT, level=LOG_LEVEL)

    if len(sys.argv) < 3:
        usage_str = 'Usage: python check_psnr.py [INPUT_DIR] [OUTPUT_FILENAME] \n' \
                    'Example: python check_psnr.py ./input ./output.csv'
        print(usage_str)
        sys.exit(0)

    input_directory = sys.argv[1]
    output_fileName = sys.argv[2]

    psnr.CalcPSNR.calc_psnr_frames(input_directory, output_fileName)
