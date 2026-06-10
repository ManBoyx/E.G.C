"""Éditeur photo optimisé pour Linux"""
import tkinter as tk
import logging
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageTk

from src.common.app import run_tk_app

logger = logging.getLogger(__name__)


class PhotoEditor:
    """Éditeur photo avec optimisations mémoire"""
    def __init__(self, root):
        self.root = root
        self.root.title("EGC Éditeur Photo - Optimisé pour Linux")
        self.root.geometry("1000x700")

        self.image = None
        self.tk_image = None
        self.undo_stack = []
        self.redo_stack = []
        self.color = "black"
        self.brush_size = 5
        self.last_x, self.last_y = None, None

        self.canvas = tk.Canvas(root, bg='white', width=800, height=600)
        self.canvas.pack(side=tk.RIGHT, pady=10)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.create_controls()
        logger.info("Éditeur photo démarré")

    def create_controls(self):
        """Crée le panneau de contrôle"""
        controls = tk.Frame(self.root)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        tk.Label(controls, text="Outils", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(controls, text="📂 Ouvrir", command=self.load_image).pack(pady=5, fill=tk.X)
        tk.Button(controls, text="💾 Sauvegarder", command=self.save_image).pack(pady=5, fill=tk.X)
        tk.Button(controls, text="🎨 Couleur", command=self.choose_color).pack(pady=5, fill=tk.X)
        tk.Button(controls, text="↶ Annuler", command=self.undo).pack(pady=5, fill=tk.X)
        tk.Button(controls, text="↷ Refaire", command=self.redo).pack(pady=5, fill=tk.X)

    def load_image(self):
        """Charge une image"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            try:
                self.image = Image.open(file_path)
                self.update_display()
                logger.info(f"Image chargée: {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger l'image: {e}")
                logger.error(f"Erreur chargement: {e}")

    def save_image(self):
        """Sauvegarde l'image"""
        if not self.image:
            messagebox.showwarning("Attention", "Aucune image à sauvegarder")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            try:
                self.image.save(path)
                messagebox.showinfo("Succès", "Image sauvegardée!")
                logger.info(f"Image sauvegardée: {path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur sauvegarde: {e}")
                logger.error(f"Erreur sauvegarde: {e}")

    def choose_color(self):
        """Choisit la couleur du pinceau"""
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color

    def paint(self, event):
        """Peint sur le canevas"""
        if not self.image:
            return
        self.undo_stack.append(self.image.copy())
        draw = ImageDraw.Draw(self.image)
        draw.ellipse(
            [event.x - self.brush_size, event.y - self.brush_size,
             event.x + self.brush_size, event.y + self.brush_size],
            fill=self.color
        )
        self.update_display()

    def reset(self, event):
        """Réinitialise le dessin"""
        self.last_x, self.last_y = None, None

    def undo(self):
        """Annule la dernière action"""
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.update_display()

    def redo(self):
        """Refait la dernière action"""
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.update_display()

    def update_display(self):
        """Met à jour l'affichage du canevas"""
        if self.image:
            self.tk_image = ImageTk.PhotoImage(self.image.resize((800, 600)))
            self.canvas.create_image(400, 300, image=self.tk_image)


def main():
    """Point d'entrée pour console_scripts."""
    run_tk_app(PhotoEditor)
