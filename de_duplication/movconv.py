from pathlib import Path
import ffmpeg
from logging import getLogger
logger = getLogger(__name__)


class MovieConverter(object):

    FFMPEG_PATH = Path('./bin/ffmpeg.exe').resolve().as_posix()

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
        logger.info('MIXED: ' + dst.as_posix())

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
        logger.info('EXT: ' + ext)

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
                ffmpeg_path=FFMPEG_PATH):
        src = Path(input_dir).resolve()
        dst = Path(output_file).parent.resolve().joinpath(Path(output_file).name)
        pic_name = src.joinpath(input_name+'.'+input_ext)
        logger.info('INPUT: '+src.as_posix())
        logger.info('OUTPUT: '+dst.as_posix())
        logger.info('NAME_FMT: '+pic_name.name)
        logger.info('EXT: ' + input_ext)

        (ffmpeg
         .input(pic_name.as_posix(), r=fps)
         .output(dst.as_posix(), vcodec=vcodec, preset=preset, tune=tune, crf=crf)
         .run(cmd=ffmpeg_path, overwrite_output=True)
         )

        return dst.as_posix()
