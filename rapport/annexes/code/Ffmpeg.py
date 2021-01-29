import ffmpeg_streaming
video = ffmpeg_streaming.input('https://www.youtube.com/watch?v=J9w-cir5a6U')


hls = video.hls(Formats.h264())
hls.auto_generate_representations()
hls.output('https://www.youtube.com/watch?v=J9w-cir5a6U')