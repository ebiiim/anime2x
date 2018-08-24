import os
import sys
import cv2
from logging import getLogger
logger = getLogger(__name__)


class MovCombiner(object):

    @staticmethod
    def mkdir4combiner(src, divide_w, divide_h):

        base_dir = '/'.join(src.split('/')[:-1])  # ./input
        base_dir_name = src.split('/')[-2]  # input
        divided_base_dir = base_dir + '-' + str(divide_w) + '_' + str(divide_h)  # ./input-4_3
        dst_dir = divided_base_dir + '-combined'  # ./input-4_3-combined
        src_dirs = [divided_base_dir+'/'+base_dir_name+'_'+'{:04g}'.format(idx+1) for idx in range(divide_w*divide_h)]

        for path in src_dirs:
            if not os.path.exists(path):
                logger.critical('not found: ' + path)
                sys.exit(-1)

        if not os.path.exists(dst_dir):
            logger.info('mkdir: ' + dst_dir)
            os.makedirs(dst_dir)

        return src_dirs, dst_dir

    @staticmethod
    def combine_image(src_file, src_dirs, dst_dir, divide_w, divide_h):

        # img path list
        concat_lists = list()

        idx_dir = 0
        for idx_h in range(divide_h):
            w_list = list()
            for idx_w in range(divide_w):
                w_list.append(src_dirs[idx_dir] + '/' + src_file)
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

        src_dirs, dst_dir = MovCombiner.mkdir4combiner(src_dir+'/dummy.data', divide_w, divide_h)
        logger.info('src_dirs: ' + str(src_dirs))

        for img in os.listdir(src_dir):
            MovCombiner.combine_image(img, src_dirs, dst_dir, divide_w, divide_h)

        return dst_dir
