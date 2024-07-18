import cv2
from flask import Flask, render_template, Response


app = Flask(__name__)


class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        #self.video.set(3, 1280)
        self.video.set(4, 720)
        self.video.set(cv2.CAP_PROP_FPS, 120)
        self._last_frame = None # Shared memory

    def __del__(self):
        self.video.release()

    def mirror_frame(self, frame):
        # Mirror the frame horizontally
        mirrored_frame = cv2.flip(frame, 1)
        return mirrored_frame

    def resize_frame(self, frame, target_width, target_height):
        original_height, original_width = frame.shape[:2]

        # Calculate the aspect ratio
        aspect_ratio = original_width / original_height

        # Calculate new dimensions while maintaining aspect ratio
        if target_width / aspect_ratio <= target_height:
            new_width = target_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = target_height
            new_width = int(new_height * aspect_ratio)

        # Resize the frame
        resized_frame = cv2.resize(frame, (new_width, new_height))
        return resized_frame

    def update_frame(self):
        ret, frame = self.video.read()
        
        ## Process the frame
        # Denoise the frame
        # denoised_frame = cv2.fastNlMeansDenoisingColored(frame, None, h=10, hForColor=10, templateWindowSize=7, searchWindowSize=21)
        # denoised_frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
        # Apply sharpening (adjust alpha and beta values as needed)
        # sharpened_frame = cv2.addWeighted(denoised_frame, 1.5, denoised_frame, -0.5, 0)
        resized_frame = self.resize_frame(frame, 640, 480)

        mirrored_frame = self.mirror_frame(resized_frame)
        
        ## Serve the frame
        self._last_frame = mirrored_frame

    def get_frame(self):
        frame = self._last_frame
        
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()


def generate(camera):
    while True:
        camera.update_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + camera.get_frame() + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(debug=True)
