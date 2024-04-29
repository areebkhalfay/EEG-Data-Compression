#!/bin/bash

# Create symbolic links
ln -s encode.py encode
ln -s decode.py decode

# Set permissions
chmod +x encode.py decode.py

echo "Build complete."