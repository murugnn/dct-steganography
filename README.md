# DCT Steganography

A Python tool for hiding and extracting messages in images using DCT (Discrete Cosine Transform) steganography. My implementation modifies DCT coefficients in the frequency domain to embed data with minimal visual impact on the image.

## What is DCT Steganography?

DCT (Discrete Cosine Transform) steganography is a technique that hides information within the frequency components of an image rather than directly manipulating pixel values.

## Features

- **Secure Message Hiding**: Embed text messages within images with minimal visual changes
- **Extraction**: Recover hidden messages from steganographic images
- **Configurable Strength**: Adjust embedding strength to balance between robustness and visual quality
- **Command-Line Interface**: Easy-to-use CLI for both embedding and extraction operations
- **Grayscale Image Support**: Works with grayscale images (can be extended to color)
- **Null Termination**: Messages are automatically null-terminated for reliable extraction

## Requirements

- Python 3.6+
- NumPy
- OpenCV (cv2)
- SciPy

## Installation

1. Clone this repository:
```bash
git clone https://github.com/murugnn/dct-steganography.git
cd dct-steganography
```

2. Install the required dependencies:
```bash
pip install numpy opencv-python scipy
```

## Usage

### Embedding a Message

To hide a message in an image:

```bash
python dct_steganography.py embed --image path/to/cover.png --message "Your secret message or flag{hidden_data}" --output path/to/output.png
```

Optional parameters:
- `--alpha` or `-a`: Embedding strength (default: 0.1). Higher values make the embedding more robust but potentially more visible.

### Extracting a Message

To extract a hidden message from an image:

```bash
python dct_steganography.py extract --image path/to/stego.png
```

Optional parameters:
- `--length` or `-l`: Specify the message length in bits if known (usually not needed as messages are null-terminated)

## Applications

- **CTF Challenges**: Hide flags within images for capture-the-flag competitions
- **Digital Watermarking**: Embed copyright information in images
- **Covert Communication**: Exchange hidden messages within innocuous-looking images
- **Data Authentication**: Verify the integrity of images

## Future Improvements

- Color image support (applying DCT to each color channel)
- Adaptive embedding strength based on image content
- Error correction codes for more robust recovery
- Encryption of the message before embedding
- Spread spectrum techniques for increased security

## License

This project is licensed under the MIT License 
