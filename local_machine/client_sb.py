# client_sb.py creates client to connect to linux server with speechbrain installed
import socket
from datetime import datetime

server_address = "127.0.0.1" # Localhost
server_port = 12345 # Port used by the server

# Open the socket to connect to server
def open_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))
    return client_socket

# Close the socket connected to server
def close_socket(client_socket):
    client_socket.close()

# send a string to server
def send_string(client_socket, message):
    # Convert the string to bytes using utf-8 encoding
    message_bytes = message.encode('utf-8')
    try:
        # Send the message length before sending the actual message
        client_socket.sendall(len(message_bytes).to_bytes(4, byteorder='big'))
        print("len message byte")
        print(len(message_bytes))
        client_socket.sendall(message_bytes)
        print("String sent successfully.")

    except Exception as e:
        print("Error occurred while sending string.")
        print(e)

# send a numpy array to server
def send_nparray(client_socket, array):
    # Serialize the NumPy array using numpy.tobytes
    serialized_array = array.tobytes()
    total_bytes = len(serialized_array)

    try:
        print("Sending NumPy array")
        client_socket.sendall(total_bytes.to_bytes(4, byteorder='big'))

        # send numpy array by chunks of 16000
        chunk_size = 16000
        offset = 0

        while offset < total_bytes:
            chunk = serialized_array[offset:offset + chunk_size]
            client_socket.sendall(chunk)
            offset += len(chunk)

        print("NumPy array sent successfully.")

    except Exception as e:
        print("Error occurred while sending data.")
        print(e)

# Receive the data in chunks
def receive_data(client_socket):
    # get message length
    L = int.from_bytes(client_socket.recv(4), byteorder='big')  
    data = b""
    # Receives data from server
    while len(data) < L:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        data += chunk
    return data

# Convert the received bytes back to a string using utf-8 decoding
def decode_string(data):
    message = data.decode('utf-8')
    return message

# receive a string from server
def receive_string(client_socket):
    try:
        # Receive the integer response from the server
        response_data = receive_data(client_socket)
        response = decode_string(response_data)
        print("Received response from the server:", response)

    except Exception as e:
        print("Error occurred while receiving string.")
        print(e)

    return response

# process the enrollment command
def enroll_process(path, nparray):
    client_socket = open_socket()
    send_string(client_socket, "enroll")
    send_nparray(client_socket, nparray)
    send_string(client_socket, path)
    receive_string(client_socket)
    close_socket(client_socket)

# process the load_sample command
def load_sample_process():
    client_socket = open_socket()
    send_string(client_socket, "load_samples")
    receive_string(client_socket)
    close_socket(client_socket)

# process the recognize command
def recognize_process(audio_np):
    client_socket = open_socket()
    send_string(client_socket, "recognize")
    send_nparray(client_socket, audio_np)
    name = receive_string(client_socket)
    close_socket(client_socket)
    return name

#--------------------------------testings-----------------------#
# test = np.load("temp.npy")
# client_socket = open_socket()
# send_nparray(client_socket, test)
# close_socket(client_socket)

# empty_array = np.empty((10, 1))
# enroll_process("hello", empty_array)

# a = read("./speaker_voice_sample/z.wav")
# numpy_array_to_send = np.array(a[1],dtype=float)
# send_nparray_no_response(numpy_array_to_send)
# send_string('hello')
# arr = np.load('./testing_stuff/numpy_sync_testing.npy')
# print(arr)
# send_nparray_no_response(arr)
# send_string('./numpy_sync_testing.npy')

