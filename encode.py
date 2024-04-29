#!/usr/bin/env python3

import wave
import numpy as np
import os
from heapq import heappush, heappop, heapify
from collections import defaultdict
import sys

input_directory = "data"
output_encode_directory = "encoded"
output_decode_directory = "decoded"

signalType = []

def read_wav_file(file_path):
    with wave.open(file_path, 'rb') as wav:
        framerate = wav.getframerate()
        nframes = wav.getnframes()
        frames = wav.readframes(nframes)
        channels = wav.getnchannels()
        sampwidth = wav.getsampwidth()
        try:
            signal = np.frombuffer(frames, dtype=np.clongdouble)
            if True in list(np.isnan(signal)):
                signal = np.frombuffer(frames, dtype=np.int64)
                signalType.append(64)
            else:
                signalType.append("clongdouble")
        except ValueError:  
            try:
                signal = np.frombuffer(frames, dtype=np.int64)
                signalType.append(64)  
            except ValueError:
                try:
                    signal = np.frombuffer(frames, dtype=np.int32)
                    signalType.append(32)
                    return signal, framerate, nframes, sampwidth, channels
                except ValueError:
                    signal = np.frombuffer(frames, dtype=np.int16)
                    signalType.append(16)
                    return signal, framerate, nframes, sampwidth, channels
    return signal, framerate, nframes, sampwidth, channels

class Node:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(frequencies):
    heap = [Node(symbol, freq) for symbol, freq in frequencies.items()]
    heapify(heap)
    while len(heap) > 1:
        left = heappop(heap)
        right = heappop(heap)
        merged = Node(freq=left.freq + right.freq, left=left, right=right)
        heappush(heap, merged)
    return heap[0]

def build_huffman_codes(root):
    codes = {}

    def traverse(node, code=''):
        if node:
            if node.symbol is not None:
                codes[node.symbol] = code
            traverse(node.left, code + '0')
            traverse(node.right, code + '1')

    traverse(root)
    return codes

def encode_data(data, codes):
    encoded_data = ''.join(codes[char] for char in data)
    padded_encoded_data = encoded_data + '0' * ((8 - len(encoded_data) % 8) % 8)
    encoded_bytes = bytes(int(padded_encoded_data[i:i+8], 2) for i in range(0, len(padded_encoded_data), 8))
    return encoded_bytes

def huffman_compress(data):
    frequencies = defaultdict(int)
    for symbol in data:
        frequencies[symbol] += 1
    root = build_huffman_tree(frequencies)
    codes = build_huffman_codes(root)
    encoded_data = encode_data(data, codes)
    return encoded_data, root, len(data)

frame_data = []
huffman_tree = []
compressed_data_total = []
def compress(file_path, encoded_file_path):
    signal, frameRate, nFrames, sampwidth, channels = read_wav_file(file_path)
    compressed_data, root, original_size = huffman_compress(signal)
    frame_data.append(frameRate)
    frame_data.append(nFrames)
    frame_data.append(sampwidth)
    frame_data.append(channels)
    frame_data.append(original_size)
    huffman_tree.append(root)
    with open(encoded_file_path, 'wb') as encoded_file:
        encoded_file.write(compressed_data)
    compressed_data_total.append(compressed_data)

def serialize_tree(node, file):
    if node is None:
        file.write("N\n")
    else:
        if node.symbol is not None:
            file.write(f"{node.symbol},{node.freq}\n")
        else:
            file.write(f"None,{node.freq}\n")
        serialize_tree(node.left, file)
        serialize_tree(node.right, file)

if __name__ == "__main__":
    os.makedirs(output_encode_directory, exist_ok=True)
    os.makedirs(output_decode_directory, exist_ok=True) 
    os.makedirs(output_encode_directory + "/data", exist_ok=True)
    input_file = sys.argv[1]
    compressed_file_path = sys.argv[2]
    compress(input_file, compressed_file_path)
    data_str = ','.join(map(str, frame_data))
    frame_data_file_path = os.path.join(output_encode_directory, input_file.split('.')[0] + "_frame_data.txt")
    with open(frame_data_file_path, 'w') as file:
        file.write(data_str)
    huffman_tree_file_path = os.path.join(output_encode_directory, input_file.split('.')[0] + "_huffman_tree.txt")
    with open(huffman_tree_file_path, "w") as file:
        serialize_tree(huffman_tree[0], file)
    compressed_data_txt = os.path.join(output_encode_directory, input_file.split('.')[0] + ".txt")
    with open(compressed_data_txt, "wb") as file:
        file.write(compressed_data_total[0])
    signal_type_txt = os.path.join(output_encode_directory, input_file.split('.')[0] + "_signal_type.txt")
    with open(signal_type_txt , "w") as file:
            file.write(str(signalType[0]))