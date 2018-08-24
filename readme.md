# mov-dedup

動画から同一フレームを取り除くツール

## Preparation

1. Python3の環境を用意する
2. `pip install -r requirements.txt`
3. `/bin/`に`ffmpeg.exe`を置く（4.0.0確認済） [FFmpeg](https://ffmpeg.zeranoe.com/builds/)

## Mode1: Divided Images (run.py)

画像を分割して重複排除を行う。

### Usage
環境にあわせて`run.py`を編集してから実行してください。コマンドラインオプションは気が向いたら実装します。

`opencv-python`が必要です。
Windowsでpipがうまく動かない場合は[こちら](https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv)のコンパイル済みバイナリを利用してください。
OpenCV自体のインストールは不要です。

確認済: `opencv_python‑3.4.2‑cp37‑cp37m‑win_amd64.whl`

### Workflow (Example)

1: `./input`を用意

```
input/
  images_00000001.png
  images_00000002.png
  ...
```

2: 4x3分割 (`DIVIDE_W=4` `DIVIDE_W=3`)

`d.MovDivider.divide_images()`

```
input-4_3/
  input_0001/
    images_00000001.png
    images_00000002.png
    ...
  input_0002/
    images_00000001.png
    images_00000002.png
    ...
  ...
```

3: (WIP) コピー

4: 結合

`c.MovCombiner.combine_images()`

```
input-4_3-combined/
  images_00000001.png
  images_00000002.png
  ...
```

5: エンコード

- `./output/`に`audio.aac`を置いとく
- `FRAME_RATE`は`24`or`30`
- 詳細は`run.py`参照
- 特殊な場合は手動でFFmpegコマンドを実行して...

## Mode2: Single Image (single_dedup.py)

画像を分割せずに重複排除を行う。

### Usage

5種類のコマンド `hist` `check` `copy1` `copy2` `enc`

Examples

- `single_dedup.py hist ./similarity.csv`: SSIM 0.90--1.00 の積み上げのヒストグラムを`output/`に出力する
- `single_dedup.py check 0.85 ./similarity.csv`: `similarity.csv`の`SSIM(Whole)`で`0.85`以上の枚数や比率をコンソールに出力する
- `single_dedup.py copy1 0.85 ./similarity.csv`: `input/`のうち重複しないフレーム（SSIM < `0.85`）だけを`tmp/`にコピーする
- `single_dedup.py copy2 0.85 ./similarity.csv`: `input/`のうち重複するフレーム（SSIM > `0.85`）だけ、前の重複しないフレームを __`tmp/` から `tmp/` に__ コピーする
- `single_dedup.py enc ./similarity.csv`: `tmp/`の中身をffmpegで動画に変換して`output/`に出力する（`output/audio.aac`を事前に置くこと）

`enc`はおまけ程度の機能しかない。`enc`では`./similarity.csv`は使わない（引数が2個あれば良い）。

### Workflow

1. 準備
    1. ffmpegで動画を画像と音声に分離する
    1. 分離した`image_%8d.png`の連番画像を`input/`に置く
    1. 分離した音声を`audio.aac`として`output/`に置く
1. 確認
    1. `hist`でヒストグラムを確認する
    1. `check`で重複率などを確認する
1. 画像処理
    1. `copy1`で重複しない画像を`tmp/`にコピーする
    1. `tmp/`内の画像に対して何かしらの処理を行う（ファイル名を変えないこと）
    1. `copy2`で重複する画像を`tmp/`内でコピーする
1. エンコード
    1. `enc`で`tmp/`内を画像と`output/audio.aac`を動画に変換して`output/`に出力する
