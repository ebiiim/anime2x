import logging
import time
from divide_conquer import divider as d
from divide_conquer import combiner as c


if __name__ == '__main__':
    LOG_FMT = "%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s"
    LOG_LEVEL = logging.INFO
    DIVIDE_W = 4
    DIVIDE_H = 3
    SRC_DIR = './input'

    logging.basicConfig(format=LOG_FMT, level=LOG_LEVEL)
    start_time = time.time()

    d.MovDivider.divide_images(SRC_DIR, DIVIDE_W, DIVIDE_H)
    c.MovCombiner.combine_images(SRC_DIR, DIVIDE_W, DIVIDE_H)

    elapsed_time = time.time() - start_time
    print(elapsed_time)
