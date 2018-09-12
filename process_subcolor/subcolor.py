import numpy as np
import cv2
from pathlib import Path


class SubtractiveColor:

    @staticmethod
    def is_power(x, pow_num):
        if x < pow_num:
            return 0

        base_num = 0
        while x != 1:
            if x % pow_num != 0:
                return 0
            else:
                x //= pow_num
            base_num += 1

        return base_num

    @staticmethod
    def quantize_uni(src, n_color):
        n_color_power = SubtractiveColor.is_power(n_color, 8)
        assert n_color_power != 0, \
            'quantize-number must be power of 8'''
        quantize_number = 256 // pow(2, n_color_power)

        dst = (src // quantize_number + 0.5) * quantize_number
        return dst

    @staticmethod
    def kmeans_uni(src, K):
        # Clustering
        clustering_sample = np.float32(src.reshape(-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(
            clustering_sample, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Apply new color
        center = np.uint8(center)
        dst = center[label.flatten()].reshape((src.shape))
        return dst

    @staticmethod
    def kmeans_dir(input_dir, output_dir, K):
        # Accumulate pixels
        src_names = list(Path(input_dir).glob('*.png'))
        src_all_data = []
        src_all_shape = []
        for src_name in src_names:
            src = cv2.imread(src_name.as_posix())
            src_all_shape.append(src.shape)
            src = np.asarray(src, dtype=np.float32).reshape(-1, 3)
            src_all_data.extend(src.tolist())

        # Clustering
        clustering_sample = np.array(src_all_data, dtype=np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(
            clustering_sample, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Apply new color
        id_src_all = 0
        center = np.uint8(center)
        for i in range(len(src_names)):
            # Extract pixels of source image from 'src_all_data,' which is accumulated samples
            dst_size = src_all_shape[i][0] * src_all_shape[i][1]
            dst = np.uint8(src_all_data[id_src_all:(id_src_all+dst_size)])
            id_src_all += dst_size

            # Match pixels to palette
            bf = cv2.BFMatcher()
            matches = bf.match(dst, center)
            dst = center[[m.trainIdx for m in matches]
                         ].reshape(src_all_shape[i])

            # Output dst
            dst_name = Path(output_dir) / Path(src_names[i].name)
            cv2.imwrite(dst_name.as_posix(), dst)


if __name__ == '__main__':
    SubtractiveColor.kmeans_dir('./frames', './k-means', 5)
