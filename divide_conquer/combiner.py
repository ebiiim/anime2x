from pathlib import Path
import sys
import cv2
from logging import getLogger
logger = getLogger(__name__)


class MovCombiner(object):

    @staticmethod
    def mkdir4combiner(src, divide_w, divide_h):
        src_dir = Path(src.replace('-' + str(divide_w) + '_' + str(divide_h), '')).resolve() # ./input
        base_dir = src_dir.parent.joinpath(src_dir.name + '-' + str(divide_w) + '_' + str(divide_h)).resolve()
        dst_dir = Path(base_dir.as_posix() + '-combined')  # ./input-4_3-combined
        print(dst_dir)
        src_dirs = [base_dir.joinpath(src_dir.name+'_'+'{:04g}'.format(idx+1)) for idx in range(divide_w*divide_h)]

        for path in src_dirs:
            if not path.exists():
                logger.critical('not found: ' + path.as_posix())
                sys.exit(-1)

        if not dst_dir.exists():
            logger.info('mkdir: ' + dst_dir.as_posix())
            dst_dir.mkdir()

        return [p.as_posix() for p in src_dirs], dst_dir.as_posix()

    @staticmethod
    def combine_image(src_file, src_dirs, dst_dir, divide_w, divide_h):

        # img path list
        concat_lists = list()

        idx_dir = 0
        for idx_h in range(divide_h):
            w_list = list()
            for idx_w in range(divide_w):
                w_list.append(Path(src_dirs[idx_dir]).joinpath(src_file).as_posix())
                idx_dir += 1
            concat_lists.append(w_list)

        # read images
        concat_lists_im = [[cv2.imread(im) for im in h_list] for h_list in concat_lists]

        # concat
        dst_path = dst_dir + '/' + src_file
        logger.debug(dst_path + ' <- ' + str(concat_lists))
        img = cv2.vconcat([cv2.hconcat(h_list) for h_list in concat_lists_im])
        return cv2.imwrite(dst_path, img)

    @staticmethod
    def combine_images(src_dir, divide_w, divide_h):
        src_dirs, dst_dir = MovCombiner.mkdir4combiner(src_dir, divide_w, divide_h)
        logger.info('src_dirs: ' + str(src_dirs))
        logger.info('dst_dir: ' + str(dst_dir))

        for img in Path(src_dirs[0]).iterdir():
            MovCombiner.combine_image(img.name, src_dirs, dst_dir, divide_w, divide_h)

        return dst_dir
