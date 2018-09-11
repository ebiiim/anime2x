from pathlib import Path
import cv2
from logging import getLogger
logger = getLogger(__name__)


class MovDivider(object):

    @staticmethod
    def mkdir4divider(src, divide_w, divide_h):
        """
        divide_image()のためにディレクトリを作成する
        """
        output_base_dir = src.parent.joinpath(src.name + '-' + str(divide_w) + '_' + str(divide_h)).resolve()
        dirs = [output_base_dir.joinpath(src.name + '_' + '{:04g}'.format(idx+1)) for idx in range(divide_w*divide_h)]
        for path in dirs:
            if not path.exists():
                logger.info('mkdir: ' + path.as_posix())
                path.mkdir()

        return [p.as_posix() for p in dirs]

    @staticmethod
    def divide_image(src, dst_dirs, divide_w, divide_h):
        im = cv2.imread(src)
        im_w = im.shape[1]
        im_h = im.shape[0]
        crop_w = im_w/divide_w
        crop_h = im_h/divide_h
        logger.debug('(src, w, h, crop) = ('+src+', '+str(im_w)+', '+str(im_h)+', '+str(divide_w*divide_h)+')')

        # 切り取りリストを作成する: (box, save_path)のlist
        divide_list = list()
        file_name = src.split('/')[-1]
        idx_dir = 0
        for idx_h in range(divide_h):
            for idx_w in range(divide_w):
                box = (int(crop_w*idx_w), int(crop_h*idx_h), int(crop_w*(idx_w+1)), int(crop_h*(idx_h+1)))
                # logger.debug(str(idx_dir) + ': ' + str(box))
                save_path = Path(dst_dirs[idx_dir]).joinpath(file_name).as_posix()
                divide_list.append((box, save_path))
                idx_dir = idx_dir+1

        # 切り取りリストに従って処理
        return [cv2.imwrite(s, im[b[1]:b[3], b[0]:b[2]]) for b, s in divide_list]

    @staticmethod
    def divide_images(src_dir, divide_w, divide_h):
        dst_dirs = MovDivider.mkdir4divider(Path(src_dir), divide_w, divide_h)
        logger.info('dst_dirs: ' + str(dst_dirs))

        img_list = [p.resolve().as_posix() for p in Path(src_dir).iterdir()]
        for img in img_list:
            MovDivider.divide_image(img, dst_dirs, divide_w, divide_h)

        return dst_dirs
