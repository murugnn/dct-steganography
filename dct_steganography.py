import numpy as np
import cv2
from scipy.fft import dct, idct
import argparse
import os
import sys


class DCTSteganography:
    def __init__(self, alpha=0.1):
        """
        Initialize the DCT steganography system
        
        Args:
            alpha: Embedding strength factor (higher values are more robust but more visible)
        """
        self.alpha = alpha
        self.block_size = 8 

    def embed(self, cover_image_path, message, output_path):
        """
        Embed a message into a cover image using DCT steganography
        
        Args:
            cover_image_path: Path to the original image
            message: Text message to hide (will be converted to binary)
            output_path: Path to save the steganographic output image
            
        Returns:
            bool: True if embedding was successful
        """
        try:
            
            image = cv2.imread(cover_image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                print(f"Error: Could not load image from {cover_image_path}")
                return False
            
            # Ensure image dimensions are multiples of block size (pad if necessary)
            h, w = image.shape
            new_h = h - (h % self.block_size) if h % self.block_size != 0 else h
            new_w = w - (w % self.block_size) if w % self.block_size != 0 else w
            
            if new_h != h or new_w != w:
                print(f"Image dimensions adjusted to multiples of {self.block_size}")
                image = image[:new_h, :new_w]
            
            # Convert message to binary
            binary_message = ''.join(format(ord(char), '08b') for char in message)
            binary_message += '00000000'  # Add null terminator
            
            # Check if message can fit in the image
            total_blocks = (image.shape[0] // self.block_size) * (image.shape[1] // self.block_size)
            if len(binary_message) > total_blocks:
                print(f"Error: Message too long to embed in this image. Max length: {total_blocks // 8} characters")
                return False
            
            # Prepare the output image
            stego_image = np.copy(image).astype(np.float32)
            
            # Process each 8×8 block
            bit_index = 0
            for y in range(0, image.shape[0], self.block_size):
                for x in range(0, image.shape[1], self.block_size):
                    if bit_index >= len(binary_message):
                        break
                    
                    # Extract the block
                    block = image[y:y+self.block_size, x:x+self.block_size].astype(np.float32)
                    
                    # Apply DCT
                    dct_block = dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
                    
                    # Modify the mid-frequency coefficient based on the bit to hide
                    # Using (4,5) coefficient which is less visually significant
                    if bit_index < len(binary_message):
                        bit = int(binary_message[bit_index])
                        if bit == 1:
                            dct_block[4, 5] = abs(dct_block[4, 5]) + self.alpha
                        else:
                            dct_block[4, 5] = -abs(dct_block[4, 5]) - self.alpha
                        bit_index += 1
                    
                    # Apply inverse DCT
                    modified_block = idct(idct(dct_block, axis=0, norm='ortho'), axis=1, norm='ortho')
                    
                    # Replace the block in the output image
                    stego_image[y:y+self.block_size, x:x+self.block_size] = modified_block
            
            # Clip values to valid range and convert to uint8
            stego_image = np.clip(stego_image, 0, 255).astype(np.uint8)
            
            # Save the output image
            cv2.imwrite(output_path, stego_image)
            print(f"Message embedded successfully. Output saved to {output_path}")
            print(f"Embedded {bit_index} bits out of {len(binary_message)} bits")
            return True
            
        except Exception as e:
            print(f"Error in embedding process: {e}")
            return False

    def extract(self, stego_image_path, message_length=None):
        """
        Extract a hidden message from a steganographic image
        
        Args:
            stego_image_path: Path to the steganographic image
            message_length: Optional length of the message in bits
            
        Returns:
            str: Extracted message string or None if extraction failed
        """
        try:
            # Load the stego image
            stego_image = cv2.imread(stego_image_path, cv2.IMREAD_GRAYSCALE)
            if stego_image is None:
                print(f"Error: Could not load image from {stego_image_path}")
                return None
            
            # Ensure image dimensions are multiples of block size
            h, w = stego_image.shape
            if h % self.block_size != 0 or w % self.block_size != 0:
                print(f"Warning: Image dimensions are not multiples of {self.block_size}")
                # Adjust dimensions
                new_h = h - (h % self.block_size)
                new_w = w - (w % self.block_size)
                stego_image = stego_image[:new_h, :new_w]
            
            # Extract bits from each 8×8 block
            extracted_bits = []
            for y in range(0, stego_image.shape[0], self.block_size):
                for x in range(0, stego_image.shape[1], self.block_size):
                    if message_length and len(extracted_bits) >= message_length:
                        break
                    
                    # Extract the block
                    block = stego_image[y:y+self.block_size, x:x+self.block_size].astype(np.float32)
                    
                    # Apply DCT
                    dct_block = dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
                    
                    # Extract bit based on the sign of the coefficient
                    bit = 1 if dct_block[4, 5] > 0 else 0
                    extracted_bits.append(str(bit))
                    
                    # Check for null terminator if no message_length specified
                    if not message_length and len(extracted_bits) % 8 == 0:
                        # Check if last byte is null terminator
                        last_byte = ''.join(extracted_bits[-8:])
                        if last_byte == '00000000':
                            extracted_bits = extracted_bits[:-8]  # Remove null terminator
                            break
                
                if (message_length and len(extracted_bits) >= message_length) or \
                   (not message_length and len(extracted_bits) % 8 == 0 and 
                    len(extracted_bits) >= 8 and ''.join(extracted_bits[-8:]) == '00000000'):
                    break
            
            # Convert binary to ASCII
            binary_chunks = [''.join(extracted_bits[i:i+8]) for i in range(0, len(extracted_bits), 8)]
            
            # Filter out invalid bytes and convert to characters
            extracted_message = ""
            for chunk in binary_chunks:
                if len(chunk) == 8:  # Ensure we have a full byte
                    try:
                        char_code = int(chunk, 2)
                        # Only include printable ASCII characters
                        if 32 <= char_code <= 126 or char_code in [9, 10, 13]:  # Basic printable ASCII + tab, newline, carriage return
                            extracted_message += chr(char_code)
                    except ValueError:
                        pass  # Skip invalid binary sequences
            
            return extracted_message
            
        except Exception as e:
            print(f"Error in extraction process: {e}")
            return None


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import numpy
        import cv2
        from scipy.fft import dct
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages: pip install numpy opencv-python scipy")
        return False


def main():
    """Main function to parse arguments and execute commands"""
    if not check_dependencies():
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description='DCT Steganography Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Embed command
    embed_parser = subparsers.add_parser('embed', help='Embed a message in an image')
    embed_parser.add_argument('--image', '-i', required=True, help='Path to cover image')
    embed_parser.add_argument('--message', '-m', required=True, help='Message to hide')
    embed_parser.add_argument('--output', '-o', required=True, help='Output image path')
    embed_parser.add_argument('--alpha', '-a', type=float, default=0.1, help='Embedding strength (default: 0.1)')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract a message from an image')
    extract_parser.add_argument('--image', '-i', required=True, help='Path to stego image')
    extract_parser.add_argument('--length', '-l', type=int, help='Message length in bits (optional)')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == 'embed':
        steganography = DCTSteganography(alpha=args.alpha)
        success = steganography.embed(args.image, args.message, args.output)
        if not success:
            sys.exit(1)
    
    elif args.command == 'extract':
        steganography = DCTSteganography()
        message = steganography.extract(args.image, args.length)
        if message is not None:
            print(f"Extracted message: {message}")
        else:
            print("Message extraction failed")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()