import pyaudio
import numpy as np
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
a = True
try:
    while True:
        input_data = stream.read(cu)
        x = np.frombuffer(input_data, dtype=np.int16)
        y = processing_signal(x)
        assert y.dtype==np.int16 
        output_data = y.tobytes()
        stream.write(output_data)
        if keyboard.is_pressed("c"):
            break

except KeyboardInterrupt:
    print(1)
    sys.exit(0)
    
stream.stop_stream()
stream.close()
p.terminate()
