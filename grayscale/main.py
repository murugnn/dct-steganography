import cv2

def reencode_to_jpeg(input_path, output_path):
    image = cv2.imread(input_path)

    if image is None:
        print("[!] Failed to load the image. Check the path or file format.")
        return

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(output_path, gray)
    print(f"[+] Grayscale JPEG saved to {output_path}")

# Example usage
reencode_to_jpeg("input.jpg", "assets/input.jpg")
