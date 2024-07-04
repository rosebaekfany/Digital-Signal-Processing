import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
import cv2
import sys
import keyboard

def processing_signal(x):
    return np.copy(x)

p = pyaudio.PyAudio()
cu= 800
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                output=True,
                frames_per_buffer=cu)

fig, ax = plt.subplots()
line, = ax.plot(np.random.randn(cu))
fig.canvas.draw()
plt.show(block=False)
ax.draw_artist(ax.patch)
ax.set_ylim(-2**12, 2**12)
#while time.time()-tstart < 5:
 
four = cv2.VideoWriter_fourcc(*'XVID')
video_out = cv2.VideoWriter("plot_realtime.mkv", four, 44100, (640, 480))
audio = []
video = []
try:
    tstart = time.time()
    while True:

        num_plots = 0
        input_data = stream.read(cu)
        x = np.frombuffer(input_data, dtype=np.int16)
        y = processing_signal(x)
        assert y.dtype==np.int16 
        line.set_ydata(y)
        ax.draw_artist(ax.patch)
        ax.draw_artist(line)
        #fig.canvas.blit(ax.bbox)
        #fig.canvas.update()
        #fig.canvas.flush_events()
        plt.pause(0.0000000000000001)
        num_plots += 1

        fig.canvas.draw()
        frame = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        video_out.write(frame)
        video.append(frame)
        audio.append(y)
        if keyboard.is_pressed("c"):
            break


except KeyboardInterrupt:
    sys.exit(0)

stream.stop_stream()
stream.close()
p.terminate()
video_out.release()