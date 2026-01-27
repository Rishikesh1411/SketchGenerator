import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import os

# Dictionary to store PIL images
images = {"original": None, "sketch": None}


def open_file():
    filepath = filedialog.askopenfilename(initialdir="Data/Real")
    if not filepath:
        return
    img = cv2.imread(filepath)
    display_image(img, original=True)
    sketch_img = convert_to_sketch(img)
    display_image(sketch_img, original=False)


def convert_to_sketch(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted_img = cv2.bitwise_not(gray_img)
    blurred_img = cv2.GaussianBlur(inverted_img, (21, 21), sigmaX=0, sigmaY=0)
    inverted_blur_img = cv2.bitwise_not(blurred_img)
    sketch_img = cv2.divide(gray_img, inverted_blur_img, scale=256.0)
    return sketch_img


def display_image(img, original):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if original else img
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)

    # Store the PIL image in the dictionary
    if original:
        images["original"] = img_pil
    else:
        images["sketch"] = img_pil

    label = original_image_label if original else sketch_image_label
    label.config(image=img_tk)
    label.image = img_tk


def save_sketch():
    if images["sketch"] is None:
        messagebox.showerror("Error", "No sketch to save.")
        return

    sketch_filepath = filedialog.asksaveasfilename(initialdir="Data/sketch", defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if not sketch_filepath:
        return

    # Save the PIL image (sketch) to the file
    images["sketch"].save(sketch_filepath, "PNG")
    messagebox.showinfo("Saved", "Sketch saved to {}".format(sketch_filepath))


def process_all():
    real_dir = "Data/Real"
    sketch_dir = "Data/sketch"
    if not os.path.exists(real_dir):
        messagebox.showerror("Error", "Data/Real directory not found.")
        return
    if not os.path.exists(sketch_dir):
        os.makedirs(sketch_dir)
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    processed_count = 0
    last_sketch = None
    for filename in os.listdir(real_dir):
        if filename.lower().endswith(image_extensions):
            filepath = os.path.join(real_dir, filename)
            img = cv2.imread(filepath)
            if img is not None:
                sketch_img = convert_to_sketch(img)
                sketch_filename = os.path.splitext(filename)[0] + "_sketch.png"
                sketch_filepath = os.path.join(sketch_dir, sketch_filename)
                cv2.imwrite(sketch_filepath, sketch_img)
                processed_count += 1
                last_sketch = sketch_img
                # Display the original for the last one
                display_image(img, original=True)
            else:
                print(f"Failed to load {filename}")
    
    if last_sketch is not None:
        display_image(last_sketch, original=False)
    
    messagebox.showinfo("Processed", f"Processed {processed_count} images. Sketches saved to {sketch_dir}")


app = tk.Tk()
app.title('Pencil Sketch Converter')

frame = tk.Frame(app)
frame.pack(pady=10, padx=10)

original_image_label = tk.Label(frame)
original_image_label.grid(row=0, column=0, padx=5, pady=5)
sketch_image_label = tk.Label(frame)
sketch_image_label.grid(row=0, column=1, padx=5, pady=5)

btn_frame = tk.Frame(app)
btn_frame.pack(pady=10)

open_button = tk.Button(btn_frame, text="Open Image", command=open_file)
open_button.grid(row=0, column=0, padx=5)

save_button = tk.Button(btn_frame, text="Save Sketch", command=save_sketch)
save_button.grid(row=0, column=1, padx=5)

process_button = tk.Button(btn_frame, text="Process All", command=process_all)
process_button.grid(row=0, column=2, padx=5)

quit_button = tk.Button(btn_frame, text="Quit", command=app.quit)
quit_button.grid(row=0, column=3, padx=5)

app.mainloop()