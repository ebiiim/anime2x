# anime2x

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/nullpo-t/anime2x/blob/master/LICENSE) ![platform win-64](https://img.shields.io/badge/platform-win--64-lightgrey.svg)

## A Pre-rendered Super-resolution Video Up-converter with waifu2x

This program decomposes a video into frames, upscales them with [waifu2x](http://waifu2x.udp.jp), and then combines them.
Since the program performs deduplication before upscaling, processing is faster when there are many scenes with no motion (e.g. Slice of Life/Comedy Anime).

## Usage

Convert `input.mp4` using default settings (2x upscaling).
```
anime2x.exe input.mp4 output.mp4
```


## System Requirements

- Windows (64 bit)
- NVIDIA GPU with [Compute Capability 3.0](https://developer.nvidia.com/cuda-gpus)
    - CUDA 9.x and cuDNN 7.x are recommended (for [waifu2x-caffe]((https://github.com/lltcggie/waifu2x-caffe))). 
    - More than 3x slower on CPU.
- SSD
    - Very slow on HDD.

## Development

### Setup

Python 3.6 or later is required.

```
git clone https://github.com/nullpo-t/anime2x.git && cd anime2x
pip install -r requirements.txt
python download_dependencies.py
```

Installing [opencv-python](https://pypi.org/project/opencv-python/) can be complicated, so you can consider using [unofficial precompiled binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv).

### Run

```
python run.py
```

### Build

```
pyinstaller pyinstaller.spec
```

## License

MIT

This project uses:
- [lltcggie/waifu2x-caffe](https://github.com/lltcggie/waifu2x-caffe)
- [OpenCV](https://opencv.org/)
- [FFmpeg](https://www.ffmpeg.org/)

## Changelog

### 0.3.0 / 2018-09-22

Initial release.
