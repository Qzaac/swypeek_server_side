import ffmpeg_streaming

video = ffmpeg_streaming.input('https://www.aminyazdanpanah.com/?"PATH TO A VIDEO FILE" or "PATH TO A LIVE HTTP STREAM"')

from ffmpeg_streaming import Formats


hls = video.hls(Formats.h264())
hls.auto_generate_representations()
hls.output('/var/media/hls.m3u8')


from ffmpeg_streaming import Formats, Bitrate, Representation, Size

_360p  = Representation(Size(640, 360), Bitrate(276 * 1024, 128 * 1024))
_480p  = Representation(Size(854, 480), Bitrate(750 * 1024, 192 * 1024))
_720p  = Representation(Size(1280, 720), Bitrate(2048 * 1024, 320 * 1024))

hls = video.hls(Formats.h264())
hls.representations(_360p, _480p, _720p)
hls.output('/var/media/hls.m3u8')
