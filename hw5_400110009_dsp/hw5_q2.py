import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import keyboard
import parselmouth
from parselmouth.praat import call
from IPython.display import Audio

def change_pitch(sound, factor):

    manipulation = call(sound, "To Manipulation", 0.01, 75, 600)

    pitch_tier = call(manipulation, "Extract pitch tier")

    call(pitch_tier, "Multiply frequencies", sound.xmin, sound.xmax, factor)

    call([pitch_tier, manipulation], "Replace pitch tier")

    return call(manipulation, "Get resynthesis (overlap-add)")


p = pyaudio.PyAudio()
cu = 1024
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=9000,
                input=True,
                output=True,
                frames_per_buffer=cu)

plt.switch_backend('TkAgg')
fig, ax = plt.subplots()
line, = ax.plot(np.random.randn(cu))
#fig.canvas.draw()
# plt.show(block=False)
ax.set_ylim(-2**12, 2**12)

try:
    while True:
        input_data = stream.read(cu)
        x = np.frombuffer(input_data, dtype=np.int16)
        x = x.astype(np.float64)
        sound = parselmouth.Sound(x,9000)
        y_sound = change_pitch(sound, 2)
        y =  y_sound.values.reshape(-1) 
        # y =Audio(data=y_sound.values, rate=y_sound.sampling_frequency)
        
        y = y.astype(np.int16) 
        line.set_ydata(y)
        plt.pause(0.0000000000000001)
        fig.canvas.draw()
        plt.show(block=False)

        # listen
        output_data = y.tobytes()
        stream.write(output_data)

        if keyboard.is_pressed("c"):
            break

except KeyboardInterrupt:
    sys.exit(0)

stream.stop_stream()
stream.close()
p.terminate()