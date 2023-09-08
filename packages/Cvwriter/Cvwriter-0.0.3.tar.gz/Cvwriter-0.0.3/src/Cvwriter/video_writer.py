import cv2
import os
class VideoWriterWrapper:
    def __init__(self, filename,  fps, frame_size,save=True):
        code = None
        if filename.endswith(".avi"):
            code = "XVID"
        if filename.endswith(".mp4"):
            code = 'MPEG'
        if filename.endswith(".h265"):
            code = "HEVC"
        if save == True:
            self.writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*f'{code}'), fps, frame_size)

    def write_frame(self, frame):
        self.writer.write(frame)

    def save_image(self,frame,name):
        folder = "save_crop"
        if not os.path.exists(folder):
            os.makedirs(folder)
        cv2.imwrite(f"{folder}/{name}.jpg", frame)

    def release(self):
        try: 
            self.writer.release()
        except:
            pass