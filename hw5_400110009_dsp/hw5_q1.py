import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import keyboard

def chunk_prossesing(x,incPercent):

    length = len(x)
    chunk = int(length* (1 - incPercent / 100))

    alpha = np.linspace(1, 0, length - chunk)

    y = np.zeros(chunk)

    y[:chunk-(length - chunk)] = x[:chunk-(length - chunk)] 
 
    y[chunk-(length - chunk):chunk] = alpha * x[chunk-(length - chunk):chunk] + (1 - alpha) * x[chunk:]

    y_resized = np.interp(np.linspace(0, 1, length), np.linspace(0, 1, chunk), y)
    #y[chunk:] = x[chunk:]




    return y_resized.astype(np.int16)
    # return np.copy(x)

p = pyaudio.PyAudio()
cu = 800
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
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
        chunk = len(x)
        y = chunk_prossesing(x,30)
        assert y.dtype == np.int16 
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