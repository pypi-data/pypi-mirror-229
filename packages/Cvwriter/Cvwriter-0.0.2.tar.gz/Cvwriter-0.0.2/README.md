# Video Writer Package

The Video Writer Package is a simple Python library that provides a wrapper around OpenCV's VideoWriter functionality, allowing you to easily capture frames and save them as video files.

## Installation

To install the Video Writer Package, you can use `pip`:

```bash
pip install videowriter
```

## Parameters

* filename: The name of the output video file.
* fps: Frames per second for the output video.
* frame_size: Tuple representing the dimensions (width, height) of the frames.

## Supported Codecs (FourCC)

* 'XVID': Xvid codec
* 'H264' or 'H265': H.264 (AVC) or H.265 (HEVC) codecs for MP4 videos
* 'MP4': Motion JPEG codec
  
## Uses
```bash

from videowriter.video_writer import VideoWriterWrapper

video_writer = VideoWriterWrapper('output.avi/output.mp4..', fps, size)

video_writer.write_frame(frame)
video_writer.save_image(frame, name)
```
