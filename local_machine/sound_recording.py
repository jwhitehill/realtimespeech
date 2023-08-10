# this file manages both sample audio recording and real-time sound-to-tensor conversion
# interface for communication between local and linux machine
import sounddevice as sd
import soundfile as sf
import threading
import client_sb
import numpy as np

# duration of recording
duration = 2
# output audio file name 
output_file = "temp.npy"
# defined sample rate
sample_rate = 16000
# defined number of channels
channels = 1 

# record audio from default microphone and send it to linux machine
def record_sample(duration, output_file):
    def recording_thread():
        # Record audio using sounddevice
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='float64')
        sd.wait()  # Wait for recording to finish
        print(recording)
        print(recording.shape)
        # np.save(output_file, recording)
        client_sb.enroll_process(output_file, recording)

    threading.Thread(target=recording_thread).start()

# record audio and convert it to a tensor
def audio_to_numpy(duration):
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='float64')
    sd.wait()  # Wait for recording to finish
    return recording

# def start_communication():
#     client_socket = client_sb.open_socket()
#     return client_socket

# connect to server and pass the 1 sec recording for processing
# return: name of the speaker
def verify_speaker(audio_np):
    name = client_sb.recognize_process(audio_np)
    return name

# connet to server to load sample audios into instance variables to start recognition
def load_samples():
    client_sb.load_sample_process()
    


# --------------------testing-------------------------#

# # test whether the numpy arrays are the same on linux and local machine
# def nparray_sync_testing():
#     recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='float64')
#     sd.wait()
#     np.save('./testing_stuff/numpy_sync_testing.npy', recording)


# nparray_sync_testing()
# # nparray_sync_testing
# arr = np.load('./testing_stuff/numpy_sync_testing.npy')
# print(arr)
# time.sleep(1)
# client_sb.send_nparray_no_response(arr)
# client_sb.send_string('server_numpy_sync_testing.npy')


# record_sample(3, output_file)

# time.sleep(5)

# # Delete the recorded file
# os.remove(output_file)