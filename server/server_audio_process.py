# server_audio_process.py receives messages from the client and connect to vad_speaker_verification.py for identificatin
import speechbrain
import socket
import numpy as np
#import speaker_verification
import vad_speaker_verification
import torch
# import speaker_verification
from datetime import datetime

# placeholder for temporary numpy array (voice sample)
temp_numpy_to_save = np.empty([1])
# defined sample rate
sample_rate = 16000
# define run-time duration of sample
run_duration = 1
# list of voice samples from registered user
sample_list = {}

# Receive the data in chunks
def receive_data(client_socket):
    # get message length
    L = int.from_bytes(client_socket.recv(4), byteorder='big')  
    print("number of bytes from client:")
    print(L)
    data = b""
    # receive by 16000 bytes (sample rate)
    while len(data) < L:
        if L-len(data) < 16000:
            chunk = client_socket.recv(L-len(data))
        else:
            chunk = client_socket.recv(16000)
        if not chunk:
            break
        data += chunk

    print("Received data length:", len(data))
    return data

# Convert the received bytes back to a string using utf-8 decoding
def decode_string(data):
    message = data.decode('utf-8')
    return message

# Convert the received bytes back to a numpy array
def decode_numpy(data):
    received_array = np.frombuffer(data, dtype="float64")
    if received_array.size > 0:
        received_array = received_array.reshape((-1,))  # Convert back to the original shape
        #print(received_array)
        return received_array
    
# send the response message back to client
def response_message(client_socket, message):
    message_bytes = message.encode('utf-8')
    client_socket.sendall(len(message_bytes).to_bytes(4, byteorder='big'))
    client_socket.sendall(message_bytes)

# receive and store the numpy array sent by the client
def receive_info(server_socket):
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    # receive data from socket
    data = receive_data(client_socket)
    # interpret the command that is being received
    command = decode_string(data)

    # During enrollment, a numpy array of voice sample and a string is received. Save to local file for later reference
    if command == "enroll":
        print("Got enroll command")
        numpy_data = receive_data(client_socket)
        numpy = decode_numpy(numpy_data)
        print("Got sample numpy data")
        #print(numpy)
        path_data = receive_data(client_socket)
        path = decode_string(path_data)
        print(path)
        np.save(path, numpy)
        response_message(client_socket, "enrollment successful")
    elif command == "load_samples":
        print("Got load sample command")
        global sample_list
        sample_list = vad_speaker_verification.load_samples()
        response_message(client_socket, "sample loading successful")
    elif command == "recognize":
        print("Got recognize command")

        # Get the current datetime with milliseconds
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print("Current time to start receiving numpy array:", current_time)

        numpy_data = receive_data(client_socket)
        numpy = decode_numpy(numpy_data)

        # Get the current datetime with milliseconds
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print("Current time to end receiving numpy array:", current_time)
        
        audio_tensor = torch.from_numpy(numpy)
        name = vad_speaker_verification.compare_recording(audio_tensor)
        response_message(client_socket, name)

        # Get the current datetime with milliseconds
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print("Current time to end processing numpy array:", current_time)

    client_socket.close()
    print("Connection closed.")

def main():
    host = "127.0.0.1"  # Localhost
    port = 12345  # Choose any available port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)  # Listen for only one connection at a time

    print(f"Server listening on {host}:{port}")

    while True:
        receive_info(server_socket)

    server_socket.close()

if __name__ == "__main__":
    main()
