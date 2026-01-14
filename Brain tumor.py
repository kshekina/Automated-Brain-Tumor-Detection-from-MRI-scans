import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from PIL import Image, ImageTk, ImageDraw

# ---------- RULE-BASED DETECTION ----------
def detect_tumor(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Simple threshold segmentation
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5, 5), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        tumor_detected = False

        for cnt in contours:
            if cv2.contourArea(cnt) > 500:
                cv2.drawContours(img, [cnt], -1, (255, 0, 255), 2)
                tumor_detected = True

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        return pil_img, ("🧠 Tumor Detected" if tumor_detected else "✅ No Tumor Detected")

    except Exception as e:
        return None, f"Error: {e}"

# ---------- BACKGROUND CREATION ----------
def create_space_bg(width, height):
    """Create a starry background for both splash and main app."""
    img = Image.new("RGB", (width, height), "#0b032d")
    draw = ImageDraw.Draw(img)
    # Gradient + stars
    for i in range(height):
        color = (int(11 + i * 0.05), int(3 + i * 0.1), int(45 + i * 0.3))
        draw.line((0, i, width, i), fill=color)
    for _ in range(250):
        x, y = np.random.randint(0, width), np.random.randint(0, height)
        r = np.random.randint(1, 2)
        draw.ellipse((x - r, y - r, x + r, y + r), fill="white")
    return ImageTk.PhotoImage(img)

# ---------- MAIN APPLICATION ----------
def start_main_app():
    splash.destroy()
    main_app()

def main_app():
    def open_images():
        nonlocal image_paths, current_index
        file_paths = filedialog.askopenfilenames(
            title="Select MRI Image(s)",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_paths:
            image_paths = list(file_paths)
            current_index = 0
            show_image()

    def show_image():
        
        nonlocal current_index
        if not image_paths:
            messagebox.showinfo("Info", "Please upload at least one MRI image.")
            return

        file_path = image_paths[current_index]
        pil_img, result = detect_tumor(file_path)
        if pil_img:
            pil_img = pil_img.resize((400, 400))
            tk_img = ImageTk.PhotoImage(pil_img)
            image_label.config(image=tk_img)
            image_label.image = tk_img
            result_label.config(
                text=f"{result}",
                fg="#39FF14" if "No" in result else "#FF007F"
            )
            filename_label.config(text=f"🖼 {file_path.split('/')[-1]} ({current_index+1}/{len(image_paths)})")

    def next_image():
        nonlocal current_index
        if image_paths:
            if current_index < len(image_paths) - 1:
                current_index += 1
                show_image()
            else:
                messagebox.showinfo("End", "No more images.")
        else:
            messagebox.showinfo("Info", "No image selected yet.")

    def prev_image():
        nonlocal current_index
        if image_paths:
            if current_index > 0:
                current_index -= 1
                show_image()
            else:
                messagebox.showinfo("Info", "This is the first image.")
        else:
            messagebox.showinfo("Info", "No image selected yet.")

    def clear_image():
        nonlocal image_paths, current_index
        if messagebox.askyesno("⚠️ Warning", "Do you want to clear all images?"):
            image_paths = []
            current_index = 0
            image_label.config(image="")
            image_label.image = None
            result_label.config(text="Result: Not Tested Yet", fg="white")
            filename_label.config(text="")

    def exit_app():
        if messagebox.askyesno("Exit", "Are you sure you want to quit?"):
            root.destroy()

    def update_background(event=None):
        width = root.winfo_width()
        height = root.winfo_height()
        bg_img = create_space_bg(width, height)
        bg_label.config(image=bg_img)
        bg_label.image = bg_img

    # Main window setup
    root = tk.Tk()
    root.title("Automated Brain Tumor Detection from MRI Scans")
    root.state("zoomed")

    bg_label = Label(root)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    update_background()
    root.bind("<Configure>", update_background)

    title_label = Label(
        root, text="🧠 Automated Brain Tumor Detection from MRI Scans 🧠",
        font=("Orbitron", 26, "bold"), bg="#0b032d", fg="#00FFFF"
    )
    title_label.pack(pady=25)

    button_frame = tk.Frame(root, bg="#0b032d")
    button_frame.pack(pady=10)

    style = {"font": ("Arial", 13, "bold"), "relief": "raised", "padx": 12, "pady": 6}

    upload_btn = Button(button_frame, text="📂 Upload MRI(s)", command=open_images, bg="#00BFFF", fg="white", **style)
    upload_btn.grid(row=0, column=0, padx=10)

    clear_btn = Button(button_frame, text="❌ Clear", command=clear_image, bg="#FF007F", fg="white", **style)
    clear_btn.grid(row=0, column=1, padx=10)

    exit_btn = Button(button_frame, text="🚪 Exit", command=exit_app, bg="#9370DB", fg="white", **style)
    exit_btn.grid(row=0, column=2, padx=10)

    image_label = Label(root, bg="#1a0033", relief="solid", bd=2, highlightbackground="#00FFFF", highlightthickness=2)
    image_label.pack(pady=25)

    filename_label = Label(root, text="", font=("Consolas", 12, "italic"), bg="#0b032d", fg="#B0E0E6")
    filename_label.pack()

    result_label = Label(root, text="Result: Not Tested Yet", font=("Consolas", 16, "bold"), bg="#0b032d", fg="white")
    result_label.pack(pady=20)

    nav_frame = tk.Frame(root, bg="#0b032d")
    nav_frame.pack(pady=10)

    prev_btn = Button(nav_frame, text="⬅ Previous", command=prev_image, bg="#9400D3", fg="white", **style)
    prev_btn.grid(row=0, column=0, padx=10)

    next_btn = Button(nav_frame, text="Next ➡", command=next_image, bg="#9400D3", fg="white", **style)
    next_btn.grid(row=0, column=1, padx=10)

    footer_label = Label(
        root, text="✨ Made by Shekina & Gani Sri ✨",
        font=("Arial", 11, "italic"), bg="#0b032d", fg="#ADFF2F"
    )
    footer_label.pack(side="bottom", pady=10)

    image_paths = []
    current_index = 0
    root.mainloop()

# ---------- SPLASH / INTRO SCREEN ----------
splash = tk.Tk()
splash.title("Launching App...")
splash.attributes('-fullscreen', True)

width = splash.winfo_screenwidth()
height = splash.winfo_screenheight()
bg_img = create_space_bg(width, height)

bg_label = Label(splash, image=bg_img)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

title = Label(
    splash, text="🧠 Automated Brain Tumor Detection from MRI Scans 🧠",
    font=("Orbitron", 36, "bold"), fg="#00FFFF", bg="#0b032d"
)
title.pack(pady=200)

credit = Label(
    splash, text="✨ Made by Shekina & Gani Sri ✨",
    font=("Arial", 20, "italic"), fg="#ADFF2F", bg="#0b032d"
)
credit.pack(pady=20)

loading = Label(
    splash, text="Initializing System...",
    font=("Consolas", 16, "italic"), fg="white", bg="#0b032d"
)
loading.pack(pady=30)

splash.after(3000, start_main_app)  # Show splash for 3 seconds
splash.mainloop()