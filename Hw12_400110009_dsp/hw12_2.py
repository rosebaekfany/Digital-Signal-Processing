import numpy as np
from scipy import signal
import pyaudio
import keyboard

SAMPLE_RATE = 44100
DETECTION_THRESHOLD = 0.7

FREQUENCIES = {
    '1': (697, 1209),
    '2': (697, 1336),
    '3': (697, 1477),
    '4': (770, 1209),
    '5': (770, 1336),
    '6': (770, 1477),
    '7': (852, 1209),
    '8': (852, 1336),
    '9': (852, 1477),
    '0': (941, 1336),
    '#': (941, 1477),
    '*': (941, 1209)
}

def design_bandpass_filters():
    filters = []
    
    for freq in FREQUENCIES.values():
        f1, f2 = freq
       
        b1, a1 = signal.butter(4, [f1-50, f1+50], btype='bandpass', fs=SAMPLE_RATE)
        b2, a2 = signal.butter(4, [f2-50, f2+50], btype='bandpass', fs=SAMPLE_RATE)

        filters.append((b1, a1))
        filters.append((b2, a2))
    
    return filters

def apply_filters(chunk, filters):
    energies = []
    for idx in range(0, len(filters), 2):
        b1, a1 = filters[idx]
        b2, a2 = filters[idx + 1]

        output1 = signal.lfilter(b1, a1, chunk)
        power1 = np.sum(output1 ** 2)

        output2 = signal.lfilter(b2, a2, chunk)
        power2 = np.sum(output2 ** 2)

        energies.append(power1 + power2)

    return energies

def detect_number(energies):
    max_energy = max(energies)

    if max_energy >= DETECTION_THRESHOLD:
        max_energy_idx = np.argmax(energies)
        detected_number = list(FREQUENCIES.keys())[max_energy_idx]
        return detected_number

    return None

filters = design_bandpass_filters()

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=1024)

prev_chunk = np.zeros((1024,), dtype=np.int16)

while True:

    input_data = stream.read(1024)
    chunk = np.frombuffer(input_data, dtype=np.int16)

    full_chunk = np.concatenate((prev_chunk, chunk))

    block_size = int(SAMPLE_RATE / 50) 
    num_blocks = len(full_chunk) // block_size
    blocks = np.array_split(full_chunk[:num_blocks * block_size], num_blocks)

    prev_chunk = full_chunk[num_blocks * block_size:]

    for block in blocks:
       
        energies = apply_filters(block, filters)
        detected_number = detect_number(energies)

        if detected_number:
            print("Detected number:", detected_number)

        if keyboard.is_pressed("c"):
            break

stream.stop_stream()
stream.close()
p.terminate()