"""
Meta Data Extractor

Made by : Mohammad boorboor
Email : m.boorboor315@gmail.com
github : github.com/mohammadbourbour

"""

# Refrences

import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import datetime


class MetadataExtractorApp(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.meta_canvas = None
        self.made_by_label = None
        self.metadata_label = None
        self.extract_button = None
        self.file_label = None
        self.select_file_button = None
        self.master = master
        self.master.title("Metadata Extractor App")
        self.master.geometry("1000x750")
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):

        # Select File button and label
        self.select_file_button = tk.Button(
            self,
            text="Select File",
            command=self.select_file,
            bg="#607d8b",
            fg="white",
            font=("Arial", 12),
            relief="raised"
        )
        self.select_file_button.pack(pady=20, padx=50)

        self.file_label = tk.Label(
            self,
            text="No file selected",
            font=("Arial", 12),
            bg="#f5f5f5",
            relief="groove",
            padx=10,
            pady=10
        )
        self.file_label.pack(pady=10, padx=50)

        # Extract Metadata button and label
        self.extract_button = tk.Button(
            self,
            text="Extract Metadata",
            command=self.extract_metadata,
            bg="#607d8b",
            fg="white",
            font=("Arial", 12),
            relief="raised"
        )
        self.extract_button.pack(pady=20, padx=50)

        self.metadata_label = tk.Label(
            self,
            text="",
            font=("Arial", 12),
            bg="#f5f5f5",
            padx=10,
            pady=10,
            borderwidth=2,
            relief="groove",
            justify="left"
        )
        self.metadata_label.pack(fill=tk.BOTH, expand=True, padx=50)

        # Image preview canvas and label
        self.meta_canvas = tk.Canvas(
            self,
            width=250,
            height=250,
            bg="#f5f5f5",
            borderwidth=2,
            relief="groove"
        )
        self.meta_canvas.pack(pady=20, padx=50)

        self.image_preview_label = tk.Label(
            self,
            text="Image Preview",
            font=("Arial", 12),
            bg="#f5f5f5",
            padx=10,
            pady=5
        )
        self.image_preview_label.pack(pady=10, padx=50)

        # Made By label
        self.made_by_label = tk.Label(
            self,
            text="Made By: Mohammad Bourbour\nEmail: m.boorboor315@gmail.com",
            font=("Arial", 10),
            fg="gray"
        )
        self.made_by_label.pack(side=tk.BOTTOM, pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_label.config(text=file_path)

        # Create an image from the QR code and save it to a temporary file
        img = Image.open(file_path)
        img = img.resize((self.meta_canvas.winfo_width(), self.meta_canvas.winfo_height()), Image.LANCZOS)
        # Load the image from the temporary file into a PhotoImage object and display it on the canvas
        photo = ImageTk.PhotoImage(img)
        self.meta_canvas.create_image(0, 0, anchor="nw", image=photo)
        self.meta_canvas.image = photo

    def extract_metadata(self):

        file_path = self.file_label.cget("text")
        if not file_path:
            messagebox.showerror("Error", "Please select a file first")
            return

        try:
            with Image.open(file_path) as img:
                if not hasattr(img, '_getexif'):
                    raise ValueError("File format not supported or metadata is missing or corrupted")

                exif_data = img._getexif()

                file_size = os.path.getsize(file_path)
                creation_time = os.path.getctime(file_path)
                creation_time = datetime.datetime.fromtimestamp(creation_time)
                creation_time_str = creation_time.strftime('%Y-%m-%d %H:%M')

                modification_time = os.path.getmtime(file_path)
                modification_time = datetime.datetime.fromtimestamp(modification_time)

                modification_time_str = modification_time.strftime('%Y-%m-%d %H:%M')
                width, height = img.size

                metadata_text = f"Name: {os.path.basename(file_path)}\n"
                metadata_text += f"Size: {file_size} bytes\n"
                metadata_text += f"Creation Time: {creation_time_str}\n"
                metadata_text += f"Modification Time: {modification_time_str}\n"
                metadata_text += f"Width: {width}\n"
                metadata_text += f"Height: {height}\n"

                if exif_data:
                    for tag_id in exif_data:
                        tag = TAGS.get(tag_id, tag_id)
                        data = exif_data.get(tag_id)
                        if isinstance(data, bytes):
                            data = data.decode()
                        if tag == "GPSInfo":
                            gps_info = {}
                            for gps_tag_id in data:
                                gps_tag = TAGS.get(gps_tag_id, gps_tag_id)
                                gps_info[gps_tag] = data[gps_tag_id]
                            if gps_info.get("GPSLatitude") and gps_info.get("GPSLongitude"):
                                latitude = self.get_decimal_from_dms(gps_info.get("GPSLatitude"),
                                                                     gps_info.get("GPSLatitudeRef"))
                                longitude = self.get_decimal_from_dms(gps_info.get("GPSLongitude"),
                                                                      gps_info.get("GPSLongitudeRef"))
                                metadata_text += f"Location: ({latitude}, {longitude})\n"
                            else:
                                metadata_text += "Location: Not available\n"
                        else:
                            metadata_text += f"{tag}: {data}\n"
                else:
                    metadata_text += "Location: Not available\n"
                self.metadata_label.config(text=metadata_text)

                metadata = metadata_text

                if not metadata:
                    messagebox.showwarning("Warning", "No metadata found")
                    return

                file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                         filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
                if not file_path:
                    return

                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Field", "Value"])
                    writer.writerow([metadata_text])

                messagebox.showinfo("Success", f"Metadata exported to {file_path}")

        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_decimal_from_dms(self, dms, ref):
        degrees = dms[0][0] / dms[0][1]
        minutes = dms[1][0] / dms[1][1] / 60
        seconds = dms[2][0] / dms[2][1] / 3600
        decimal = degrees + minutes + seconds
        if ref in ["S", "W"]:
            decimal *= -1
        return decimal


root = tk.Tk()
app = MetadataExtractorApp(master=root)
app.mainloop()
