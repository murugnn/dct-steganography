import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ImagePreviewWindow:
    def __init__(self, image, title="Image Preview"):
        # Store the original image
        self.original_image = image.copy()
        self.displayed_image = image.copy()

        # Current display parameters
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Result flag
        self.result = False  # False for cancel, True for continue

        # Create main window
        self.root = tk.Tk()
        self.root.title(title)
        self.root.protocol("WM_DELETE_WINDOW", self.on_cancel)

        # Create frame for image
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas for image
        self.canvas = tk.Canvas(self.frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Button frame
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        # Cancel button
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.on_cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # Continue button
        continue_btn = tk.Button(btn_frame, text="Continue", command=self.on_continue)
        continue_btn.pack(side=tk.RIGHT, padx=5)

        # Display the image initially
        self.update_display()

        # Bind events
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux scroll down
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)

        # Set window size
        h, w = self.original_image.shape[:2]
        window_width = min(w, 800)
        window_height = min(h, 600)

        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def update_display(self):
        h, w = self.original_image.shape[:2]
        new_w = int(w * self.scale)
        new_h = int(h * self.scale)

        if self.scale != 1.0:
            resized = cv2.resize(self.original_image, (new_w, new_h), interpolation=cv2.INTER_AREA if self.scale < 1 else cv2.INTER_LINEAR)
        else:
            resized = self.original_image.copy()

        if len(resized.shape) == 2:
            resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)

        display_img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        self.displayed_image = Image.fromarray(display_img)
        self.photo = ImageTk.PhotoImage(image=self.displayed_image)

        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, new_w, new_h))
        self.canvas.create_image(-self.offset_x, -self.offset_y, image=self.photo, anchor=tk.NW)

    def on_mouse_wheel(self, event):
        zoom_in = False
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            zoom_in = True
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            zoom_in = False
        else:
            return

        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        old_scale = self.scale
        real_x = (canvas_x + self.offset_x) / old_scale
        real_y = (canvas_y + self.offset_y) / old_scale

        if zoom_in:
            self.scale *= 1.1
        else:
            self.scale /= 1.1

        self.scale = max(0.1, min(10.0, self.scale))
        self.offset_x = real_x * self.scale - canvas_x
        self.offset_y = real_y * self.scale - canvas_y
        self.clamp_offsets()
        self.update_display()

    def on_mouse_down(self, event):
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_mouse_up(self, event):
        self.dragging = False

    def on_mouse_move(self, event):
        if self.dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.offset_x -= dx
            self.offset_y -= dy
            self.clamp_offsets()
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.update_display()

    def clamp_offsets(self):
        h, w = self.original_image.shape[:2]
        max_offset_x = max(0, w * self.scale - self.canvas.winfo_width())
        max_offset_y = max(0, h * self.scale - self.canvas.winfo_height())
        self.offset_x = max(0, min(self.offset_x, max_offset_x))
        self.offset_y = max(0, min(self.offset_y, max_offset_y))

    def on_cancel(self):
        self.result = False
        self.root.quit()
        self.root.destroy()

    def on_continue(self):
        self.result = True
        self.root.quit()
        self.root.destroy()

    def show(self):
        self.root.mainloop()
        return self.result

def show_image_preview(image, title="DCT Steganography Image Preview"):
    """
    Show an image preview window with zoom/pan functionality and buttons.

    Args:
        image: OpenCV image (numpy array)
        title: Window title

    Returns:
        bool: True if user clicked Continue, False if user clicked Cancel
    """
    preview = ImagePreviewWindow(image, title)
    return preview.show()