import customtkinter as ctk
from PIL import Image
import os

class ImageViewer(ctk.CTkFrame):
    def __init__(self, master, image_paths, **kwargs):
        super().__init__(master, **kwargs)
        self._border_color = "gray"
        self._border_width = 3
        self._corner_radius = 8
        self.image_paths = image_paths
        self.thumbnail_images = []  
        self.create_thumbnail_view()

    def create_thumbnail_view(self):
        # Create a grid of thumbnail buttons
        if len(self.image_paths) != 0:
            for idx, path in enumerate(self.image_paths):
                # Check if the file exists before attempting to load it
                if not os.path.exists(path):
                    print(f"Warning: Image path does not exist: {path}")
                    continue

                try:
                    img = Image.open(path)
                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    continue

                # Create a thumbnail using PIL, then wrap it in a CTkImage
                img.thumbnail((120, 150))
                ctk_img = ctk.CTkImage(light_image=img, size=(120, 150))
                self.thumbnail_images.append(ctk_img)  

                # Create a button for the thumbnail
                btn = ctk.CTkButton(
                    self,
                    image=ctk_img,
                    text="",
                    command=lambda idx=idx: self.open_full_view(idx),
                    border_width=3,
                    border_spacing=3,
                    border_color="gray",
                    bg_color="transparent",
                    fg_color="transparent"
                )
                btn.grid(row=idx // 3, column=idx % 3, padx=10, pady=10)
        else:
            print("No images found.")

    def open_full_view(self, index):
        # Create a new window (CTkToplevel) for full image display
        full_view = ctk.CTkToplevel(self)
        full_view.title("Full Image Viewer")
        full_view.current_index = index
        full_view.wm_attributes("-topmost", True)
    
        # Set the window icon with a delayed call
        try:
            from PIL import Image, ImageTk
            icon_img = Image.open(r"geni\geni_ui_src\ui_assets\Icons\geni_logo_png.png")
            icon_img = icon_img.resize((256, 256), Image.Resampling.LANCZOS)
            # Keep a reference to avoid garbage collection
            full_view.icon_photo = ImageTk.PhotoImage(icon_img)
            # Use after() to delay setting the icon and use tk.call for a low-level approach:
            full_view.after(200, lambda: full_view.tk.call('wm', 'iconphoto', full_view._w, full_view.icon_photo))
        except Exception as e:
            print("Failed to set window icon:", e)
    
        # Label for displaying the full image
        image_label = ctk.CTkLabel(full_view)
        image_label.pack(expand=True, fill="both")

        def update_image():
            idx = full_view.current_index
            # Check if the file exists before opening
            if not os.path.exists(self.image_paths[idx]):
                print(f"Warning: Image path does not exist: {self.image_paths[idx]}")
                return
            try:
                img = Image.open(self.image_paths[idx])
            except Exception as e:
                print(f"Error loading {self.image_paths[idx]}: {e}")
                return

            # Get image size and create a CTkImage with adjusted dimensions
            width, height = img.size
            ctk_img = ctk.CTkImage(light_image=img, size=(width - 200, height - 300))
            image_label.configure(image=ctk_img)
            image_label.image = ctk_img  # Keep reference

            # Adjust the window geometry to be a bit larger than the image
            full_view.geometry(f"{width - 100}x{height - 100}")

        def next_image():
            full_view.current_index = (full_view.current_index + 1) % len(self.image_paths)
            update_image()

        def previous_image():
            full_view.current_index = (full_view.current_index - 1) % len(self.image_paths)
            update_image()

        # Navigation frame with "Previous" and "Next" buttons
        nav_frame = ctk.CTkFrame(full_view)
        nav_frame.pack(pady=10)
        prev_btn = ctk.CTkButton(nav_frame, text="Previous", command=previous_image)
        prev_btn.pack(side="left", padx=5)
        next_btn = ctk.CTkButton(nav_frame, text="Next", command=next_image)
        next_btn.pack(side="right", padx=5)

        update_image()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")  
    app = ctk.CTk()
    app.geometry("1024x768")
    

    image_files = [
        "Images\\output_image2.jpg",
        "Images\\output_image5.jpg",
    ]
    
    viewer = ImageViewer(app, image_files)
    viewer.pack(expand=True, fill="both")
    app.mainloop()
