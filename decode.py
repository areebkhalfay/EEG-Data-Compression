#!/usr/bin/env python3

import wave
import numpy as np
import os
import sys

input_directory = "data"
output_encode_directory = "encoded/data"
output_decode_directory = "decoded"

class Node:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def decode_data(encoded_bytes, root, size):
    decoded_data = []
    bits = ''.join(format(byte, '08b') for byte in encoded_bytes)
    current = root
    for bit in bits:
        if bit == '0':
            current = current.left
        else:
            current = current.right
        if current.symbol is not None:
            decoded_data.append(current.symbol)
            current = root
        if len(decoded_data) == size:
            break
    return decoded_data

def huffman_decompress(encoded_data, root, size):
    decoded_data = decode_data(encoded_data, root, size)
    return decoded_data

def deserialize_tree(file):
    line = file.readline().strip()
    if line == "N":
        return None
    symbol, freq = line.split(",")
    if symbol != "None":
        node = Node(symbol, int(freq))
    else:
        node = Node(None, int(freq))
    node.left = deserialize_tree(file)
    node.right = deserialize_tree(file)
    return node

def decode(encoded_file_path, decoded_file_path, frame_data_path, huffman_tree_path, signal_type_path):
    with open(encoded_file_path, 'rb') as encoded_file:
        encoded_data = encoded_file.read()
        huffman_tree = 0
        with open(huffman_tree_path, "r") as file:
            huffman_tree = deserialize_tree(file)
        frame_data = 0
        data_str = ""
        with open(frame_data_path, 'r') as file:
            data_str = file.read()
        signalType = ""
        with open(signal_type_path, 'r') as file:
            signalType = file.read()
        frame_data = data_str.split(',')
        frame_data = [int(item) for item in frame_data]
        decoded_data = huffman_decompress(encoded_data, huffman_tree, frame_data[4])
        with wave.open(decoded_file_path, 'wb') as decoded_file:
            decoded_file.setnchannels(frame_data[3])
            decoded_file.setsampwidth(frame_data[2])
            decoded_file.setnframes(frame_data[1])
            decoded_file.setframerate(frame_data[0])
            if signalType == "16":
                decoded_file.writeframes(np.array(decoded_data, dtype=np.int16).tobytes())
            elif signalType == "32":
                decoded_file.writeframes(np.array(decoded_data, dtype=np.int32).tobytes())
            elif signalType == "64":
                decoded_file.writeframes(np.array(decoded_data, dtype=np.int64).tobytes())
            elif signalType == "clongdouble":
                decoded_file.writeframes(np.array(decoded_data, dtype=np.clongdouble).tobytes())

if __name__ == "__main__":
    os.makedirs(output_encode_directory, exist_ok=True)
    os.makedirs(output_decode_directory, exist_ok=True)
    compressed_file_path = sys.argv[1]
    decompressed_file_path = sys.argv[2]
    frame_data_path = os.path.join(output_encode_directory, compressed_file_path.split('data/')[1].split('.wav.brainwire')[0] + "_frame_data.txt")
    huffman_tree_path = os.path.join(output_encode_directory, compressed_file_path.split('data/')[1].split('.wav.brainwire')[0] + "_huffman_tree.txt")
    signal_type_path = os.path.join(output_encode_directory, compressed_file_path.split('data/')[1].split('.wav.brainwire')[0] + "_signal_type.txt")
    decode(compressed_file_path, decompressed_file_path, frame_data_path, huffman_tree_path, signal_type_path)

