import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import tifffile as tf
import csv
import numpy as np
import cv2

from PIL import Image, ImageTk

# Set dark mode and appearance settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class CentroidAnnotationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Centroid Annotation")
        self.master.geometry("1024x768")  # Set a fixed window size
        self.master.configure(bg="black")

        self.image = None
        self.image_canvas = None
        self.current_slice = 0
        self.green_centroid = None
        self.red_centroid = None
        self.vectors = []
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        # Initialize drag-related attributes
        self.drag_start_x = 0
        self.drag_start_y = 0


        # Main Frame
        self.main_frame = ctk.CTkFrame(master)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Canvas
        self.canvas_frame = ctk.CTkFrame(self.main_frame)
        self.canvas_frame.pack(pady=10, expand=True)
        self.canvas_width = 800
        self.canvas_height = 800
        self.image_canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="black", highlightthickness=1, highlightbackground="white")
        self.image_canvas.pack()

        # Button Frame
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=10)

        # Buttons
        self.load_image_button = ctk.CTkButton(self.button_frame, text="Load Image", command=self.load_image)
        self.load_image_button.grid(row=0, column=0, padx=5, pady=5)
        self.select_centroids_button = ctk.CTkButton(self.button_frame, text="Select Centroids", command=self.select_centroids)
        self.select_centroids_button.grid(row=0, column=1, padx=5, pady=5)
        self.remove_vector_button = ctk.CTkButton(self.button_frame, text="Remove Vector", command=self.remove_vector)
        self.remove_vector_button.grid(row=0, column=2, padx=5, pady=5)
        self.save_centroids_button = ctk.CTkButton(self.button_frame, text="Save Centroids", command=self.save_centroids)
        self.save_centroids_button.grid(row=0, column=3, padx=5, pady=5)
        self.load_centroids_button = ctk.CTkButton(self.button_frame, text="Load Centroids", command=self.load_centroids)
        self.load_centroids_button.grid(row=0, column=4, padx=5, pady=5)

        # Slice Slider
        self.slice_slider = ctk.CTkSlider(self.main_frame, from_=0, to=0, orientation="horizontal", command=self.update_slice)
        self.slice_slider.pack(fill="x", padx=20, pady=10)

        # Quit Button
        self.quit_button = ctk.CTkButton(self.main_frame, text="Quit", fg_color="red", command=self.quit)
        self.quit_button.pack(pady=10, side="bottom")

        # Mouse Bindings
        self.image_canvas.bind("<MouseWheel>", self.zoom)
        self.image_canvas.bind("<Button-1>", self.start_drag)
        self.image_canvas.bind("<B1-Motion>", self.drag)

    def quit(self):
        self.master.destroy()

    def normalization(self, mip_img):
        minval = np.percentile(mip_img, 0.1)
        maxval = np.percentile(mip_img, 99.9)
        mip_img = np.clip(mip_img, minval, maxval)
        mip_img = (((mip_img - minval) / (maxval - minval)) * 255).astype('uint8')
        return mip_img

    def load_image(self):
        filename = filedialog.askopenfilename(filetypes=[("TIFF files", "*.tif")])
        if filename:
            self.image = tf.imread(filename).transpose(2, 0, 1, 3)
            self.image[:, :, :, 0] = self.normalization(self.image[:, :, :, 0])
            self.image[:, :, :, 1] = self.normalization(self.image[:, :, :, 1])
            self.image[:, :, :, 2] = self.normalization(self.image[:, :, :, 2])
            #self.image = self.image[:, :500,:500]
            self.slice_slider.configure(to=self.image.shape[0] - 1)
            self.zoom_factor = 1.0
            self.offset_x = 0
            self.offset_y = 0
            self.update_image()

    def update_image(self):
        self.image_canvas.delete("all")
        current_slice_image = self.image[self.current_slice]
        resized_shape = (int(current_slice_image.shape[1] * self.zoom_factor), int(current_slice_image.shape[0] * self.zoom_factor))
        resized_image = np.zeros((*resized_shape, 3), dtype='uint8')
        resized_image[:, :, 0] = cv2.resize(current_slice_image[:, :, 0], (resized_shape[1], resized_shape[0]))
        resized_image[:, :, 1] = cv2.resize(current_slice_image[:, :, 1], (resized_shape[1], resized_shape[0]))
        resized_image[:, :, 2] = cv2.resize(current_slice_image[:, :, 2], (resized_shape[1], resized_shape[0]))

        pil_image = Image.fromarray(resized_image)
        self.photo = ImageTk.PhotoImage(pil_image)
        self.image_canvas.create_image(self.offset_x, self.offset_y, anchor="nw", image=self.photo)

        for vector in self.vectors:
            self.draw_vector(vector)

    def update_slice(self, value):
        self.current_slice = int(value)
        self.update_image()

    def zoom(self, event):
        # Get cursor position relative to canvas
        cursor_x, cursor_y = event.x, event.y
        canvas_center_x = self.canvas_width / 2
        canvas_center_y = self.canvas_height / 2

        # Adjust zoom factor
        scale_factor = 1.1 if event.delta > 0 else 1 / 1.1
        self.zoom_factor *= scale_factor

        # Adjust offsets to zoom at the cursor position
        self.offset_x = (self.offset_x - cursor_x) * scale_factor + cursor_x
        self.offset_y = (self.offset_y - cursor_y) * scale_factor + cursor_y

        self.update_image()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.offset_x += dx
        self.offset_y += dy
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.update_image()

    def select_centroids(self):
        self.image_canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        x = (event.x - self.offset_x) / self.zoom_factor
        y = (event.y - self.offset_y) / self.zoom_factor
        if not self.green_centroid:
            self.green_centroid = (x, y, self.current_slice)
            self.image_canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, fill="green")
        elif not self.red_centroid:
            self.red_centroid = (x, y, self.current_slice)
            self.image_canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, fill="red")
            self.draw_vector((self.green_centroid, self.red_centroid))
            self.vectors.append((self.green_centroid, self.red_centroid))
            self.green_centroid = None
            self.red_centroid = None
        else:
            messagebox.showwarning("Warning", "Both centroids are already selected. Click 'Remove Vector' to clear.")

    def draw_vector(self, vector):
        (x1, y1, z1), (x2, y2, z2) = vector
        if min(z1, z2) <= self.current_slice <= max(z1, z2):
            x1_canvas = x1 * self.zoom_factor + self.offset_x
            y1_canvas = y1 * self.zoom_factor + self.offset_y
            x2_canvas = x2 * self.zoom_factor + self.offset_x
            y2_canvas = y2 * self.zoom_factor + self.offset_y
            self.image_canvas.create_line(x1_canvas, y1_canvas, x2_canvas, y2_canvas, fill="white", width=4)

    def remove_vector(self):
        self.image_canvas.bind("<Button-1>", self.remove_vector_click)

    def remove_vector_click(self, event):
        # Calculate the click position in the image space
        x = (event.x - self.offset_x) / self.zoom_factor
        y = (event.y - self.offset_y) / self.zoom_factor
        
        # Define a tolerance for clicking near the line
        tolerance = 5  # Adjust this value for more or less sensitivity
        
        # Iterate through all vectors to find the one closest to the click
        for vector in self.vectors:
            (x1, y1, _), (x2, y2, _) = vector
            
            # Calculate the distance from the point (x, y) to the line segment
            distance = self.point_to_line_distance(x, y, x1, y1, x2, y2)
            
            # If the distance is within the tolerance, remove the vector
            if distance <= tolerance:
                self.remove_vector_from_canvas(vector)
                self.vectors.remove(vector)
                break
        
        # Unbind the click event after removing the vector
        self.image_canvas.unbind("<Button-1>")

    def point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Calculate the distance from a point (px, py) to a line segment (x1, y1) - (x2, y2)."""
        # Calculate the length squared of the line segment
        line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        
        if line_length_sq == 0:
            # Line segment is a point
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        
        # Calculate the projection of the point onto the line (clamping to the segment)
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_length_sq))
        projection_x = x1 + t * (x2 - x1)
        projection_y = y1 + t * (y2 - y1)
        
        # Return the distance from the point to the projection
        return ((px - projection_x) ** 2 + (py - projection_y) ** 2) ** 0.5

    def remove_vector_from_canvas(self, vector):
        for item in self.image_canvas.find_all():
            if self.image_canvas.type(item) == "line":
                if self.image_canvas.coords(item)[0:4] == [vector[0][0], vector[0][1], vector[1][0], vector[1][1]]:
                    self.image_canvas.delete(item)
                    break

    def save_centroids(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                #writer.writerow(["Xgreen", "Ygreen", "Zgreen", "Xred", "Yred", "Zred"])
                for vector in self.vectors:
                    (x1, y1, z1), (x2, y2, z2) = vector
                    writer.writerow([x1, y1, x2, y2, z1, z2])

    def load_centroids(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.vectors = []
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                #next(reader)  # skip header
                for row in reader:
                    x1, y1, x2, y2, z1, z2 = map(float, row)
                    self.vectors.append(((x1, y1, z1), (x2, y2, z2)))
            self.update_image()

def main():
    root = ctk.CTk()
    app = CentroidAnnotationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
