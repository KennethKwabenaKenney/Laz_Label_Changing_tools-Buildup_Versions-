import tkinter as tk
from tkinter import filedialog, messagebox
import open3d as o3d
import laspy
import numpy as np
import os

class PointCloudLabelChanger:
    def __init__(self, root):
        self.root = root
        self.root.title("Point Cloud Label Changer")

        # Create a menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # Create a file menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Point Cloud", command=self.open_point_cloud)

        # Initialize variables
        self.point_cloud = None
        self.old_label_var = tk.StringVar()
        self.new_label_var = tk.StringVar()
        self.file_path = None

        # Create label selection frame
        label_frame = tk.Frame(root, padx=10, pady=10)
        label_frame.pack()

        old_label_frame_label = tk.Label(label_frame, text="Select label to change:")
        old_label_frame_label.grid(row=0, column=0, pady=5)

        self.old_label_entry = tk.Entry(label_frame, textvariable=self.old_label_var)
        self.old_label_entry.grid(row=0, column=1, pady=5)

        new_label_frame_label = tk.Label(label_frame, text="Enter new label:")
        new_label_frame_label.grid(row=1, column=0, pady=5)

        self.new_label_entry = tk.Entry(label_frame, textvariable=self.new_label_var)
        self.new_label_entry.grid(row=1, column=1, pady=5)

        change_button = tk.Button(label_frame, text="Change Label", command=self.change_label)
        change_button.grid(row=1, column=2, pady=5)

        # Create label display frame
        label_display_frame = tk.Frame(root, padx=10, pady=10)
        label_display_frame.pack()

        label_display_frame_label = tk.Label(label_display_frame, text="Available Labels:")
        label_display_frame_label.grid(row=0, column=0, pady=5)

        self.available_labels_var = tk.StringVar()
        label_display_frame_data = tk.Label(label_display_frame, textvariable=self.available_labels_var, justify=tk.LEFT)
        label_display_frame_data.grid(row=0, column=1, pady=5)

    def open_point_cloud(self):
        file_path = filedialog.askopenfilename(filetypes=[("Point Cloud Files", "*.las;*.laz")])
        if file_path:
            self.file_path = file_path
            self.point_cloud = self.read_point_cloud(file_path)
            labels = self.get_unique_labels()
            label_str = '\n'.join(map(str, labels))
            self.available_labels_var.set(label_str)
            messagebox.showinfo("Available Labels", f"Available labels:\n{label_str}")

    def read_point_cloud(self, file_path):
        return self.readPtcloud(file_path)

    def readPtcloud(self, file_path):
        L = laspy.read(file_path)

        # Extracting X, Y, Z, Intensity, and Ext_Class
        ptcloud = np.array((L.x, L.y, L.z, L.intensity, L.Ext_Class)).transpose()

        return ptcloud

    def get_unique_labels(self):
        if self.point_cloud is not None:
            return np.unique(self.point_cloud[:, -1])
        else:
            return []

    def change_label(self):
        if self.point_cloud is not None:
            try:
                old_label = int(self.old_label_var.get())
                new_label = int(self.new_label_var.get())

                # Check if the old label exists
                if old_label not in self.get_unique_labels():
                    messagebox.showerror("Error", "Selected label does not exist.")
                    return

                # Modify the Ext_Class field
                self.point_cloud[self.point_cloud[:, -1] == old_label, -1] = new_label

                # Save the updated point cloud
                file_path, _ = os.path.splitext(self.file_path)  # Get the file path without extension
                save_path = filedialog.asksaveasfilename(defaultextension=".las",
                                                           filetypes=[("LAS Files", "*.las")],
                                                           initialfile=f"{file_path}_updated.las")
                if save_path:
                    self.write_las(save_path, self.point_cloud)
                    messagebox.showinfo("Label Change", f"Label successfully changed to {new_label}. Point cloud saved.")
                else:
                    messagebox.showwarning("Warning", "Save operation canceled. Point cloud reverted.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter valid labels.")

    def write_las(self, file_path, point_cloud):
        outfile = laspy.create(point_cloud.shape[0])
        outfile.x = point_cloud[:, 0]
        outfile.y = point_cloud[:, 1]
        outfile.z = point_cloud[:, 2]
        outfile.intensity = point_cloud[:, 3]
        outfile.Ext_Class = point_cloud[:, -1].astype('uint8')
        outfile.write(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = PointCloudLabelChanger(root)
    root.mainloop()
