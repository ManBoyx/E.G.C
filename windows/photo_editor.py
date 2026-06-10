"""EGC Photo Editor - Version Windows"""
import sys
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, Menu
from pathlib import Path
from PIL import Image, ImageDraw, ImageTk, ImageFilter, ImageEnhance

logger = logging.getLogger(__name__)

BG_COLOR = "#1e1e2e"
FG_COLOR = "#cdd6f4"
ACCENT = "#89b4fa"
SURFACE = "#313244"
BORDER = "#45475a"


class PhotoEditor:
    """Editeur photo pour Windows avec theme sombre"""
    def __init__(self, root):
        self.root = root
        self.root.title("EGC Editeur Photo - Windows")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG_COLOR)

        self.image = None
        self.original_image = None
        self.tk_image = None
        self.undo_stack = []
        self.redo_stack = []
        self.color = "#cdd6f4"
        self.brush_size = 5
        self.last_x = None
        self.last_y = None
        self.current_tool = "pencil"

        self.create_menu()

        main_frame = tk.Frame(root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            main_frame, bg=SURFACE, width=850, height=650,
            highlightbackground=BORDER, highlightthickness=1
        )
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=8, padx=8)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.create_controls(main_frame)

        self.status_bar = tk.Label(
            root, text="Pret - Ouvrez une image ou dessinez",
            bd=1, relief=tk.FLAT, anchor=tk.W,
            bg="#181825", fg="#a6adc8", font=("Segoe UI", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_menu(self):
        menubar = Menu(self.root, bg=SURFACE, fg=FG_COLOR, activebackground=BORDER,
                       activeforeground=FG_COLOR, relief=tk.FLAT)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0, bg=SURFACE, fg=FG_COLOR,
                         activebackground=ACCENT, activeforeground=BG_COLOR)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir", command=self.load_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Sauvegarder", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Nouveau", command=self.new_image, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)

        edit_menu = Menu(menubar, tearoff=0, bg=SURFACE, fg=FG_COLOR,
                         activebackground=ACCENT, activeforeground=BG_COLOR)
        menubar.add_cascade(label="Edition", menu=edit_menu)
        edit_menu.add_command(label="Annuler", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Refaire", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Reinitialiser", command=self.reset_image)

        filter_menu = Menu(menubar, tearoff=0, bg=SURFACE, fg=FG_COLOR,
                           activebackground=ACCENT, activeforeground=BG_COLOR)
        menubar.add_cascade(label="Filtres", menu=filter_menu)
        filter_menu.add_command(label="Noir et Blanc", command=lambda: self.apply_filter("bw"))
        filter_menu.add_command(label="Flou", command=lambda: self.apply_filter("blur"))
        filter_menu.add_command(label="Nettete", command=lambda: self.apply_filter("sharpen"))
        filter_menu.add_command(label="Contour", command=lambda: self.apply_filter("contour"))
        filter_menu.add_command(label="Relief", command=lambda: self.apply_filter("emboss"))
        filter_menu.add_separator()
        filter_menu.add_command(label="+ Luminosite", command=lambda: self.adjust("brightness", 1.3))
        filter_menu.add_command(label="- Luminosite", command=lambda: self.adjust("brightness", 0.7))
        filter_menu.add_command(label="+ Contraste", command=lambda: self.adjust("contrast", 1.3))
        filter_menu.add_command(label="- Contraste", command=lambda: self.adjust("contrast", 0.7))

        self.root.bind("<Control-o>", lambda e: self.load_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-n>", lambda e: self.new_image())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

    def _make_btn(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command,
            bg=SURFACE, fg=FG_COLOR, activebackground=ACCENT,
            activeforeground=BG_COLOR, relief=tk.FLAT,
            font=("Segoe UI", 9), cursor="hand2", bd=0,
            padx=8, pady=4
        )

    def create_controls(self, parent):
        controls = tk.Frame(parent, width=220, bg=BG_COLOR)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        controls.pack_propagate(False)

        tk.Label(controls, text="Outils", font=("Segoe UI", 14, "bold"),
                 bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)

        self._make_btn(controls, "Ouvrir", self.load_image).pack(pady=3, fill=tk.X)
        self._make_btn(controls, "Sauvegarder", self.save_image).pack(pady=3, fill=tk.X)
        self._make_btn(controls, "Nouveau", self.new_image).pack(pady=3, fill=tk.X)

        tk.Frame(controls, height=1, bg=BORDER).pack(fill=tk.X, pady=8)

        tk.Label(controls, text="Dessin", font=("Segoe UI", 11, "bold"),
                 bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)

        self.tool_var = tk.StringVar(value="pencil")
        for label, value in [("Crayon", "pencil"), ("Gomme", "eraser"), ("Ligne", "line")]:
            tk.Radiobutton(
                controls, text=label, variable=self.tool_var,
                value=value, command=self.select_tool,
                bg=BG_COLOR, fg=FG_COLOR, selectcolor=SURFACE,
                activebackground=BG_COLOR, activeforeground=ACCENT,
                font=("Segoe UI", 9)
            ).pack(anchor=tk.W, padx=15)

        tk.Frame(controls, height=1, bg=BORDER).pack(fill=tk.X, pady=8)

        self._make_btn(controls, "Couleur", self.choose_color).pack(pady=3, fill=tk.X)

        tk.Label(controls, text="Taille du pinceau:", bg=BG_COLOR, fg=FG_COLOR,
                 font=("Segoe UI", 9)).pack(pady=3)
        self.size_scale = tk.Scale(
            controls, from_=1, to=50, orient=tk.HORIZONTAL,
            bg=BG_COLOR, fg=FG_COLOR, troughcolor=SURFACE,
            highlightbackground=BG_COLOR, font=("Segoe UI", 8)
        )
        self.size_scale.set(5)
        self.size_scale.pack(fill=tk.X, padx=10)

        tk.Frame(controls, height=1, bg=BORDER).pack(fill=tk.X, pady=8)

        self._make_btn(controls, "Annuler", self.undo).pack(pady=3, fill=tk.X)
        self._make_btn(controls, "Refaire", self.redo).pack(pady=3, fill=tk.X)

    def select_tool(self):
        self.current_tool = self.tool_var.get()

    def new_image(self):
        self.save_state()
        self.image = Image.new("RGB", (850, 650), "#313244")
        self.original_image = self.image.copy()
        self.update_display()
        self.status_bar.config(text="Nouvelle image creee (850x650)")

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")]
        )
        if file_path:
            try:
                self.image = Image.open(file_path).convert("RGB")
                self.original_image = self.image.copy()
                self.undo_stack.clear()
                self.redo_stack.clear()
                self.update_display()
                name = Path(file_path).name
                w, h = self.image.size
                self.status_bar.config(text=f"Image: {name} ({w}x{h})")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger: {e}")

    def save_image(self):
        if not self.image:
            messagebox.showwarning("Attention", "Aucune image")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )
        if path:
            try:
                self.image.save(path)
                self.status_bar.config(text=f"Sauvegarde: {Path(path).name}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {e}")

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color

    def save_state(self):
        if self.image:
            self.undo_stack.append(self.image.copy())
            if len(self.undo_stack) > 30:
                self.undo_stack.pop(0)
            self.redo_stack.clear()

    def paint(self, event):
        if not self.image:
            self.new_image()
        brush = self.size_scale.get()
        draw = ImageDraw.Draw(self.image)
        if self.last_x is not None and self.last_y is not None:
            if self.current_tool == "pencil":
                draw.line([self.last_x, self.last_y, event.x, event.y],
                          fill=self.color, width=brush)
            elif self.current_tool == "eraser":
                draw.line([self.last_x, self.last_y, event.x, event.y],
                          fill="#313244", width=brush * 3)
            elif self.current_tool == "line":
                self.save_state()
                draw.line([self.last_x, self.last_y, event.x, event.y],
                          fill=self.color, width=brush)
        else:
            self.save_state()
        self.last_x = event.x
        self.last_y = event.y
        self.update_display()

    def reset(self, event):
        self.last_x = None
        self.last_y = None

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.update_display()
            self.status_bar.config(text="Action annulee")

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.update_display()
            self.status_bar.config(text="Action retablie")

    def apply_filter(self, filter_type: str):
        if not self.image:
            messagebox.showwarning("Attention", "Aucune image")
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
            self.status_bar.config(text=f"Filtre '{filter_type}' applique")

    def adjust(self, adjustment: str, factor: float):
        if not self.image:
            messagebox.showwarning("Attention", "Aucune image")
            return
        self.save_state()
        enhancers = {
            "brightness": ImageEnhance.Brightness,
            "contrast": ImageEnhance.Contrast,
        }
        if adjustment in enhancers:
            self.image = enhancers[adjustment](self.image).enhance(factor)
            self.update_display()

    def reset_image(self):
        if self.original_image:
            self.save_state()
            self.image = self.original_image.copy()
            self.update_display()
            self.status_bar.config(text="Image reinitialisee")

    def update_display(self):
        if self.image:
            canvas_w = self.canvas.winfo_width() or 850
            canvas_h = self.canvas.winfo_height() or 650
            img_w, img_h = self.image.size
            ratio = min(canvas_w / img_w, canvas_h / img_h, 1.0)
            new_size = (int(img_w * ratio), int(img_h * ratio))
            display_img = self.image.resize(new_size, Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(display_img)
            self.canvas.delete("all")
            self.canvas.create_image(canvas_w // 2, canvas_h // 2, image=self.tk_image)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    root = tk.Tk()
    PhotoEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
