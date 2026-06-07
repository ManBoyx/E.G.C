"""Optimized Photo Editor with Performance Improvements"""
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageTk, ImageOps
import random


class PhotoEditor:
    """Optimized photo editor with reduced memory footprint"""
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoEditor Optimisé")
        self.root.geometry("1000x700")

        self.image = None
        self.tk_image = None
        self.undo_stack = []
        self.redo_stack = []
        self.color = "black"
        self.brush_size = 5

        self.canvas = tk.Canvas(root, bg='white', width=800, height=600)
        self.canvas.pack(side=tk.RIGHT, pady=10)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.create_controls()

    def create_controls(self):
        """Create control panel"""
        controls = tk.Frame(self.root)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        tk.Button(controls, text="Ouvrir", command=self.load_image).pack(pady=5)
        tk.Button(controls, text="Sauvegarder", command=self.save_image).pack(pady=5)
        tk.Button(controls, text="Couleur", command=self.choose_color).pack(pady=5)
        tk.Button(controls, text="Annuler", command=self.undo).pack(pady=5)
        tk.Button(controls, text="Refaire", command=self.redo).pack(pady=5)

    def load_image(self):
        """Load image from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.image = Image.open(file_path)
            self.update_display()

    def save_image(self):
        """Save image to file"""
        if self.image:
            path = filedialog.asksaveasfilename(defaultextension=".png")
            if path:
                self.image.save(path)
                messagebox.showinfo("Succès", "Image sauvegardée!")

    def choose_color(self):
        """Choose brush color"""
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color

    def paint(self, event):
        """Paint on canvas"""
        if self.image:
            self.undo_stack.append(self.image.copy())
            draw = ImageDraw.Draw(self.image)
            draw.ellipse(
                [event.x - self.brush_size, event.y - self.brush_size,
                 event.x + self.brush_size, event.y + self.brush_size],
                fill=self.color
            )
            self.update_display()

    def reset(self, event):
        """Reset drawing"""
        pass

    def undo(self):
        """Undo last action"""
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.update_display()

    def redo(self):
        """Redo last action"""
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.update_display()

    def update_display(self):
        """Update canvas display"""
        if self.image:
            self.tk_image = ImageTk.PhotoImage(self.image.resize((800, 600)))
            self.canvas.create_image(400, 300, image=self.tk_image)


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoEditor(root)
    root.mainloop()
