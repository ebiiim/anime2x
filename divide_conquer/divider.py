import os
from PIL import Image
from logging import getLogger
logger = getLogger(__name__)


class MovDivider(object):

    def __init__(self):
        pass

    @staticmethod
    def mkdir4divider(src, divide_w, divide_h):
        """
        divide_image()のためにディレクトリを作成する
        """
        base_dir = '/'.join(src.split('/')[:-1])  # ./input
        output_base_dir = base_dir + '-' + str(divide_w) + '_' + str(divide_h)  # ./input-4_3
        dirs = [output_base_dir + '/' + base_dir + '_' + '{:04g}'.format(idx+1) for idx in range(divide_w*divide_h)]
        for path in dirs:
            if not os.path.exists(path):
                logger.debug('mkdir: ' + path)
                os.makedirs(path)

        return dirs

    @staticmethod
    def divide_image(src, dst_dirs, divide_w, divide_h):
        im = Image.open(src)
        im_w = im.size[0]
        im_h = im.size[1]
        crop_w = im_w/divide_w
        crop_h = im_h/divide_h
        logger.debug('(src, w, h, crop) = ('+src+', '+str(im_w)+', '+str(im_h)+', '+str(divide_w*divide_h)+')')

        file_name = src.split('/')[-1]
        idx_dir = 0
        for idx_h in range(divide_h):
            for idx_w in range(divide_w):
                box = (crop_w*idx_w, crop_h*idx_h, crop_w*(idx_w+1), crop_h*(idx_h+1))
                # logger.debug(str(idx_dir) + ': ' + str(box))
                tmp_im = im.crop(box)
                tmp_im.save(dst_dirs[idx_dir] + '/' + file_name)
                idx_dir = idx_dir+1

    @staticmethod
    def devide_images(src_dir, divide_w, divide_h):
        dst_dirs = MovDivider.mkdir4divider(src_dir+'/dummy.data', divide_w, divide_h)
        logger.debug('dst_dirs:' + str(dst_dirs))

        img_list = [src_dir + '/' + each for each in os.listdir(src_dir)]
        for img in img_list:
            MovDivider.divide_image(img, dst_dirs, divide_w, divide_h)
