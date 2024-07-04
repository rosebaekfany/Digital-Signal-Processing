import wave
import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.io import savemat

SAMPLE_RATE = 8192
MIN_KEY_LENGTH = 0.3
MIN_SILENCE_LENGTH = 0.2

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

def find_block_size(audio_array, sample_rate):
    min_key_samples = int(MIN_KEY_LENGTH * sample_rate)
    min_silence_samples = int(MIN_SILENCE_LENGTH * sample_rate)
    block_samples = min_key_samples + min_silence_samples
    
    max_block_samples = len(audio_array) // len(FREQUENCIES)
    
    while block_samples <= max_block_samples:
        silence_samples = block_samples - min_key_samples
        num_blocks = len(audio_array) // block_samples
        
        total_silence = num_blocks * silence_samples
        actual_silence_ratio = total_silence / len(audio_array)
        
        if actual_silence_ratio >= MIN_SILENCE_LENGTH:
            return block_samples
        
        block_samples += silence_samples
    
    return max_block_samples

def split_signal(audio_array, block_samples):
    blocks = []
    num_blocks = len(audio_array) // block_samples
    
    for i in range(num_blocks):
        start = i * block_samples
        end = start + block_samples
        block = audio_array[start:end]
        blocks.append(block)
    
    return blocks

def design_bandpass_filters():
    filters = []
    
    # ff = [697, 770,852,941,1209,1336,1477,1633]
    
    for freq in FREQUENCIES.values():
        f1, f2 = freq
       
        b1, a1 = signal.butter(4, [f1-50, f1+50], btype='bandpass', fs=SAMPLE_RATE)
        b2, a2 = signal.butter(4, [f2-50, f2+50], btype='bandpass', fs=SAMPLE_RATE)

        # b = b1 + b2
        # a = a1 + a2
        
        filters.append((b1, a1))
        filters.append((b2, a2))
    
    return filters

def apply_filters(blocks, filters):
    energies = []
    for block in blocks:
        block_energies = []
        idx = 0

        while idx < len(filters):
            b1, a1 = filters[idx]
            b2, a2 = filters[idx + 1]

           
            output1 = signal.lfilter(b1, a1, block)
            power1 = np.sum(output1 ** 2)

           
            output2 = signal.lfilter(b2, a2, block)
            power2 = np.sum(output2 ** 2)

        
            block_energies.append(power1 + power2)

            idx += 2

        energies.append(block_energies)

    return energies


def apply_lpf(energies):
    lpf_fc = 200
    lpf_cutoff = 500  
    b, a = signal.butter(4, [lpf_fc, lpf_cutoff], btype='bandpass', fs=SAMPLE_RATE)
    
    filtered_energies = []
    for block_energies in energies:
        output = signal.lfilter(b, a, block_energies)
        filtered_energies.append(output)
    
    return filtered_energies

def detect_number(energies):
    detected_numbers = []
    for block_energies in energies:
        max_energy_idx = np.argmax(block_energies)
        detected_number = list(FREQUENCIES.keys())[max_energy_idx]
        detected_numbers.append(detected_number)
    
    return detected_numbers

with wave.open("D:\\electrical eng\\term 6\\dsp\\Wav_Files\\DialedSequence_SNR30dB.wav", 'rb') as wav_file:
    num_channels = wav_file.getnchannels()
    sample_width = wav_file.getsampwidth()
    frame_rate = wav_file.getframerate()
    num_frames = wav_file.getnframes()
    audio_data = wav_file.readframes(num_frames)

# fs_audio, audio_data = wavfile.read('DialedSequence_NoNoise.wav')
# audio_data = audio_data.astype(np.float32) / np.max(np.abs(audio_data))

    
audio_array = np.frombuffer(audio_data, dtype=np.int16)
audio_array = audio_array.astype(np.float32) / 32767.0  

block_samples = find_block_size(audio_array,8192)
blocks = split_signal(audio_array, block_samples)
filters = design_bandpass_filters()
filter_data = {'filters': filters}

savemat('D:\\electrical eng\\term 6\\dsp\\Wav_Files\\filters.mat', filter_data)

energies = apply_filters(blocks, filters)

# filtered_energies = apply_lpf(energies)
detected_numbers = detect_number(energies)

print('Detected numbers:', detected_numbers)

# dtmf_blocks = [
#     np.sin(2 * np.pi * 770 * np.linspace(0, 0.1, int(SAMPLE_RATE * 0.1))),
#     np.sin(2 * np.pi * 1336 * np.linspace(0, 0.1, int(SAMPLE_RATE * 0.1))),
# ]

# # Design bandpass filters
# filters = design_bandpass_filters()

# # Apply filters to the signal blocks
# energies = apply_filters(dtmf_blocks, filters)

# # Apply a low-pass filter to the energies
# filtered_energies = apply_lpf(energies)

# # Detect the number based on the energies
# detected_numbers = detect_number(filtered_energies)

# # Print the detected numbers
# print(detected_numbers)