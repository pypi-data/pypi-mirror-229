import cv2
# from videowriter.video_writer import VideoWriterWrapper
from src.Cvwriter.video_writer import VideoWriterWrapper
# Create a VideoWriterWrapper instance
video_writer = VideoWriterWrapper('output.avi', 30, (640, 480))

# Capture video from webcam and save
capture = cv2.VideoCapture(0)
i = 0
while True:
    i += 1
    ret, frame = capture.read()
    if not ret:
        break
    
    # Process frame if needed
    
    # Write frame to video
    video_writer.write_frame(frame)
    video_writer.save_image(frame, i)
    
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
capture.release()
video_writer.release()
cv2.destroyAllWindows()
