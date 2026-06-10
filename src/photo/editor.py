"""Éditeur photo optimisé pour Linux"""
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, Menu
from pathlib import Path
from PIL import Image, ImageDraw, ImageTk, ImageFilter, ImageEnhance

from src.common.app import run_tk_app

logger = logging.getLogger(__name__)


class PhotoEditor:
    """Éditeur photo avec optimisations mémoire et outils avancés"""
    def __init__(self, root):
        self.root = root
        self.root.title("EGC Éditeur Photo - Optimisé pour Linux")
        self.root.geometry("1100x750")

        self.image = None
        self.original_image = None
        self.tk_image = None
        self.undo_stack = []
        self.redo_stack = []
        self.color = "black"
        self.brush_size = 5
        self.last_x = None
        self.last_y = None
        self.current_tool = "pencil"

        self.create_menu()

        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_frame, bg='white', width=800, height=600)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5, padx=5)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.create_controls(main_frame)

        self.status_bar = tk.Label(
            root, text="Prêt - Ouvrez une image ou dessinez",
            bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        logger.info("Éditeur photo démarré")

    def create_menu(self):
        """Crée la barre de menus"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir", command=self.load_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Sauvegarder", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Nouveau", command=self.new_image, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)

        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Édition", menu=edit_menu)
        edit_menu.add_command(label="Annuler", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Refaire", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Réinitialiser", command=self.reset_image)

        filter_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Filtres", menu=filter_menu)
        filter_menu.add_command(label="Noir et Blanc", command=lambda: self.apply_filter("bw"))
        filter_menu.add_command(label="Flou", command=lambda: self.apply_filter("blur"))
        filter_menu.add_command(label="Netteté", command=lambda: self.apply_filter("sharpen"))
        filter_menu.add_command(label="Contour", command=lambda: self.apply_filter("contour"))
        filter_menu.add_command(label="Relief", command=lambda: self.apply_filter("emboss"))
        filter_menu.add_separator()
        filter_menu.add_command(label="+ Luminosité", command=lambda: self.adjust("brightness", 1.3))
        filter_menu.add_command(label="- Luminosité", command=lambda: self.adjust("brightness", 0.7))
        filter_menu.add_command(label="+ Contraste", command=lambda: self.adjust("contrast", 1.3))
        filter_menu.add_command(label="- Contraste", command=lambda: self.adjust("contrast", 0.7))

        self.root.bind("<Control-o>", lambda e: self.load_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-n>", lambda e: self.new_image())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

    def create_controls(self, parent):
        """Crée le panneau de contrôle"""
        controls = tk.Frame(parent, width=200)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        controls.pack_propagate(False)

        tk.Label(controls, text="Outils", font=("Arial", 14, "bold")).pack(pady=10)

        # Boutons fichier
        tk.Button(controls, text="📂Ouvrir", command=self.load_image).pack(pady=3, fill=tk.X)
        tk.Button(controls, text="💾Sauvegarder", command=self.save_image).pack(pady=3, fill=tk.X)
        tk.Button(controls, text="📄Nouveau", command=self.new_image).pack(pady=3, fill=tk.X)

        tk.Label(controls, text="─" * 25).pack(pady=5)

        # Outils de dessin
        tk.Label(controls, text="Dessin", font=("Arial", 11, "bold")).pack(pady=5)

        self.tool_var = tk.StringVar(value="pencil")
        tools = [("Crayon", "pencil"), ("Gomme", "eraser"), ("Ligne", "line")]
        for label, value in tools:
            tk.Radiobutton(
                controls, text=label, variable=self.tool_var,
                value=value, command=self.select_tool
            ).pack(anchor=tk.W, padx=10)

        tk.Label(controls, text="─" * 25).pack(pady=5)

        tk.Button(controls, text="🎨Couleur", command=self.choose_color).pack(pady=3, fill=tk.X)

        tk.Label(controls, text="Taille du pinceau:").pack(pady=3)
        self.size_scale = tk.Scale(controls, from_=1, to=50, orient=tk.HORIZONTAL)
        self.size_scale.set(5)
        self.size_scale.pack(fill=tk.X, padx=5)

        tk.Label(controls, text="─" * 25).pack(pady=5)

        # Annuler / Refaire
        tk.Button(controls, text="↶ Annuler", command=self.undo).pack(pady=3, fill=tk.X)
        tk.Button(controls, text="↷ Refaire", command=self.redo).pack(pady=3, fill=tk.X)

    def select_tool(self):
        """Sélectionne l'outil courant"""
        self.current_tool = self.tool_var.get()

    def new_image(self):
        """Crée une nouvelle image blanche"""
        self.save_state()
        self.image = Image.new("RGB", (800, 600), "white")
        self.original_image = self.image.copy()
        self.update_display()
        self.status_bar.config(text="Nouvelle image créée (800x600)")

    def load_image(self):
        """Charge une image"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            try:
                self.image = Image.open(file_path).convert("RGB")
                self.original_image = self.image.copy()
                self.undo_stack.clear()
                self.redo_stack.clear()
                self.update_display()
                self.status_bar.config(
                    text=f"Image chargée: {Path(file_path).name} "
                    f"({self.image.width}x{self.image.height})"
                )
                logger.info(f"Image chargée: {file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger l'image: {e}")
                logger.error(f"Erreur chargement: {e}")

    def save_image(self):
        """Sauvegarde l'image"""
        if not self.image:
            messagebox.showwarning("Attention", "Aucune image à sauvegarder")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if path:
            try:
                self.image.save(path)
                self.status_bar.config(text=f"Image sauvegardée: {Path(path).name}")
                logger.info(f"Image sauvegardée: {path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur sauvegarde: {e}")
                logger.error(f"Erreur sauvegarde: {e}")

    def choose_color(self):
        """Choisit la couleur du pinceau"""
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color

    def save_state(self):
        """Sauvegarde l'état courant pour undo"""
        if self.image:
            self.undo_stack.append(self.image.copy())
            if len(self.undo_stack) > 30:
                self.undo_stack.pop(0)
            self.redo_stack.clear()

    def paint(self, event):
        """Peint sur le canevas"""
        if not self.image:
            self.new_image()

        brush = self.size_scale.get()
        draw = ImageDraw.Draw(self.image)

        if self.last_x is not None and self.last_y is not None:
            if self.current_tool == "pencil":
                draw.line(
                    [self.last_x, self.last_y, event.x, event.y],
                    fill=self.color, width=brush
                )
            elif self.current_tool == "eraser":
                draw.line(
                    [self.last_x, self.last_y, event.x, event.y],
                    fill="white", width=brush * 3
                )
            elif self.current_tool == "line":
                self.save_state()
                draw.line(
                    [self.last_x, self.last_y, event.x, event.y],
                    fill=self.color, width=brush
                )
        else:
            self.save_state()

        self.last_x = event.x
        self.last_y = event.y
        self.update_display()

    def reset(self, event):
        """Réinitialise la position de dessin"""
        self.last_x = None
        self.last_y = None

    def undo(self):
        """Annule la dernière action"""
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.update_display()
            self.status_bar.config(text="Action annulée")

    def redo(self):
        """Refait la dernière action"""
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.update_display()
            self.status_bar.config(text="Action rétablie")

    def apply_filter(self, filter_type: str):
        """Applique un filtre à l'image"""
        if not self.image:
            messagebox.showwarning("Attention", "Aucune image chargée")
            return

        self.save_state()
        filters = {
            "bw": lambda img: img.convert("L").convert("RGB"),
            "blur": lambda img: img.filter(ImageFilter.GaussianBlur(radius=3)),
            "sharpen": lambda img: img.filter(ImageFilter.SHARPEN),
            "contour": lambda img: img.filter(ImageFilter.CONTOUR),
            "emboss": lambda img: img.filter(ImageFilter.EMBOSS),
        }
        if filter_type in filters:
            self.image = filters[filter_type](self.image)
            self.update_display()
            self.status_bar.config(text=f"Filtre '{filter_type}' appliqué")

    def adjust(self, adjustment: str, factor: float):
        """Ajuste la luminosité ou le contraste"""
        if not self.image:
            messagebox.showwarning("Attention", "Aucune image chargée")
            return

        self.save_state()
        enhancers = {
            "brightness": ImageEnhance.Brightness,
            "contrast": ImageEnhance.Contrast,
        }
        if adjustment in enhancers:
            self.image = enhancers[adjustment](self.image).enhance(factor)
            self.update_display()
            direction = "+" if factor > 1 else "-"
            self.status_bar.config(text=f"{direction} {adjustment}")

    def reset_image(self):
        """Réinitialise l'image à l'original"""
        if self.original_image:
            self.save_state()
            self.image = self.original_image.copy()
            self.update_display()
            self.status_bar.config(text="Image réinitialisée")

    def update_display(self):
        """Met à jour l'affichage du canevas"""
        if self.image:
            canvas_w = self.canvas.winfo_width() or 800
            canvas_h = self.canvas.winfo_height() or 600
            img_w, img_h = self.image.size
            ratio = min(canvas_w / img_w, canvas_h / img_h, 1.0)
            new_size = (int(img_w * ratio), int(img_h * ratio))
            display_img = self.image.resize(new_size, Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(display_img)
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_w // 2, canvas_h // 2, image=self.tk_image
            )


def main():
    """Point d'entrée pour console_scripts."""
    run_tk_app(PhotoEditor)
