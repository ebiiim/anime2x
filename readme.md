# mov-dedup

動画から同一フレームを取り除くやつ（プロトタイプ）

## Preparation

1. Python3の環境を用意する
2. `pip install -r requirements.txt`
3. `/bin/`に`ffmpeg.exe`を置く（4.0.0確認済） [FFmpeg](https://ffmpeg.zeranoe.com/builds/)

## Usage

5種類のコマンド `hist` `check` `copy1` `copy2` `enc`

Examples

- `run.py hist ./similarity.csv`: SSIM 0.90--1.00 の積み上げのヒストグラムを`output/`に出力する
- `run.py check 0.85 ./similarity.csv`: `similarity.csv`の`SSIM(Whole)`で`0.85`以上の枚数や比率をコンソールに出力する
- `run.py copy1 0.85 ./similarity.csv`: `input/`のうち重複しないフレーム（SSIM < `0.85`）だけを`tmp/`にコピーする
- `run.py copy2 0.85 ./similarity.csv`: `input/`のうち重複するフレーム（SSIM > `0.85`）だけ、前の重複しないフレームを __`tmp/` から `tmp/` に__ コピーする
- `run.py enc ./similarity.csv`: `tmp/`の中身をffmpegで動画に変換して`output/`に出力する（`output/audio.aac`を事前に置くこと）

## Workflow

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

### TODO

いろんなオプションに対応したい...
