import subprocess
from pathlib import Path
import ffmpeg
from logging import getLogger
logger = getLogger(__name__)


class MovieConverter(object):
    # /path/to/project_root/bin/ffmpeg/bin/ffmpeg.exe
    FFMPEG_PATH = Path(__file__+'/../../bin/ffmpeg/bin/ffmpeg.exe').resolve().as_posix()

    @staticmethod
    def probe_file(input_file, ffmpeg_path=FFMPEG_PATH):
        src = Path(input_file).resolve()

        # informationからフレームレートを抽出する
        proc = subprocess.run([ffmpeg_path, '-i', src.as_posix()], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc.stderr.decode("utf8")  # ffmpegはoutputを指定しなければエラーが出るため、stderrを見る
        fps_loc = output.find('fps')  # 文字列'fps'の位置
        fps = float(output[fps_loc-16:fps_loc].split(',')[-1])  # 'fps'より前をカンマでsplitすると最後がフレームレート

        logger.info('FRAME RATE: ' + str(fps))

        return fps

    @staticmethod
    def extract_audio(input_file, output_file, ffmpeg_path=FFMPEG_PATH):
        src = Path(input_file).resolve()
        dst = Path(output_file).resolve()
        logger.info('INPUT: '+src.as_posix())
        logger.info('OUTPUT: '+dst.as_posix())

        (ffmpeg
         .input(src.as_posix())
         .output(dst.as_posix(), acodec='copy', vn=None)
         .run(cmd=ffmpeg_path, overwrite_output=True)
         )

        return dst.as_posix()

    @staticmethod
    def mix(input_video, input_audio, output_file, ffmpeg_path=FFMPEG_PATH):
        video = Path(input_video).resolve()
        audio = Path(input_audio).resolve()
        dst = Path(output_file).resolve()
        logger.info('VIDEO: '+video.as_posix())
        logger.info('AUDIO: '+audio.as_posix())
        logger.info('MIXED: '+dst.as_posix())

        video_stream = ffmpeg.input(video.as_posix())
        audio_stream = ffmpeg.input(audio.as_posix())
        out_stream = ffmpeg.output(video_stream, audio_stream, dst.as_posix(), acodec='copy', vcodec='copy')
        ffmpeg.run(out_stream, cmd=ffmpeg_path, overwrite_output=True)

        return dst.as_posix()

    @staticmethod
    def mov2pic(input_file, output_dir, name='%08d', ext='png', ffmpeg_path=FFMPEG_PATH):
        src = Path(input_file).resolve()
        dst = Path(output_dir)
        if not dst.exists():
            dst.mkdir()
        dst = dst.resolve()
        pic_name = dst.joinpath(name+'.'+ext)
        logger.info('INPUT: '+src.as_posix())
        logger.info('OUTPUT: '+dst.as_posix())
        logger.info('NAME_FMT: '+pic_name.name)
        logger.info('EXT: '+ext)

        (ffmpeg
         .input(src.as_posix())
         .output(pic_name.as_posix())
         .run(cmd=ffmpeg_path, overwrite_output=True)
         )

        return dst.as_posix()

    @staticmethod
    def pic2mov(input_dir, output_file, input_name='%08d', input_ext='png',
                fps=24,  # input frame rate
                vcodec='libx265', preset='slow', tune='ssim', crf='22',  # encoder settings
                resize=False, resize_w=2560, resize_h=1440, resize_algo='lanczos',  # resize settings
                ffmpeg_path=FFMPEG_PATH):
        src = Path(input_dir).resolve()
        dst = Path(output_file).parent.resolve().joinpath(Path(output_file).name)
        pic_name = src.joinpath(input_name+'.'+input_ext)
        logger.info('INPUT: '+src.as_posix())
        logger.info('OUTPUT: '+dst.as_posix())
        logger.info('NAME_FMT: '+pic_name.name)
        logger.info('EXT: '+input_ext)

        stream = ffmpeg.input(pic_name.as_posix(), r=fps)
        if resize:
            stream = ffmpeg.output(stream, dst.as_posix(), vcodec=vcodec, preset=preset, tune=tune, crf=crf,
                                   vf='scale='+str(resize_w)+'x'+str(resize_h)+':flags='+resize_algo)
        else:
            stream = ffmpeg.output(stream, dst.as_posix(), vcodec=vcodec, preset=preset, tune=tune, crf=crf)
        stream.run(cmd=ffmpeg_path, overwrite_output=True)

        return dst.as_posix()
