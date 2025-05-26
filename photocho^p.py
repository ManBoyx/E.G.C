import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, Menu, simpledialog
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageTk, ImageOps
import random

class PhotoPaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoPaint")
        self.root.geometry("1000x700")

        self.image = None
        self.tk_image = None
        self.draw = None
        self.last_x, self.last_y = None, None
        self.undo_stack = []
        self.redo_stack = []

        self.canvas = tk.Canvas(root, bg='white', width=800, height=600)
        self.canvas.pack(side=tk.RIGHT, pady=20, padx=10)

        self.status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.create_menu()
        self.create_controls_frame()

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.color = "black"
        self.fill_color = "white"
        self.current_tool = "pencil"
        self.stroke_style = "solid"

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.load_image)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")

        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)

    def create_controls_frame(self):
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.tool_var = tk.StringVar(value="pencil")
        tools = ["pencil", "line", "rectangle", "circle", "fill", "text", "eraser", "spray"]
        for tool in tools:
            tk.Radiobutton(controls_frame, text=tool.capitalize(), variable=self.tool_var, value=tool, command=self.select_tool).pack(anchor=tk.W)

        self.color_button = tk.Button(controls_frame, text="Choose Color", command=self.choose_color)
        self.color_button.pack(pady=5)

        self.fill_color_button = tk.Button(controls_frame, text="Choose Fill Color", command=self.choose_fill_color)
        self.fill_color_button.pack(pady=5)

        self.brush_size_scale = tk.Scale(controls_frame, from_=1, to=50, orient=tk.HORIZONTAL, label="Brush Size")
        self.brush_size_scale.pack(pady=5)

        self.stroke_style_var = tk.StringVar(value="solid")
        stroke_styles = ["solid", "dashed", "dotted"]
        for style in stroke_styles:
            tk.Radiobutton(controls_frame, text=style.capitalize(), variable=self.stroke_style_var, value=style, command=self.select_stroke_style).pack(anchor=tk.W)

        self.filter_var = tk.StringVar(value="none")
        filters = ["none", "black_white", "contrast", "sharpness", "blur", "contour"]
        for filter_name in filters:
            tk.Radiobutton(controls_frame, text=filter_name.capitalize(), variable=self.filter_var, value=filter_name, command=self.apply_filter).pack(anchor=tk.W)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file_path:
            self.image = Image.open(file_path)
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(400, 300, image=self.tk_image)
            self.draw = ImageDraw.Draw(self.image)
            self.status_bar.config(text=f"Loaded: {file_path}")

    def save_image(self):
        if self.image:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
            if save_path:
                self.image.save(save_path)
                self.status_bar.config(text=f"Saved: {save_path}")
                messagebox.showinfo("Success", f"Image saved: {save_path}")

    def choose_color(self):
        self.color = colorchooser.askcolor()[1]

    def choose_fill_color(self):
        self.fill_color = colorchooser.askcolor()[1]

    def select_tool(self):
        self.current_tool = self.tool_var.get()

    def select_stroke_style(self):
        self.stroke_style = self.stroke_style_var.get()

    def paint(self, event):
        if self.image and self.draw:
            if self.last_x and self.last_y:
                self.undo_stack.append(self.image.copy())
                if self.current_tool == "pencil":
                    self.draw_line(event.x, event.y)
                elif self.current_tool == "line":
                    self.draw_line(event.x, event.y)
                elif self.current_tool == "rectangle":
                    self.draw_rectangle(event.x, event.y)
                elif self.current_tool == "circle":
                    self.draw_circle(event.x, event.y)
                elif self.current_tool == "fill":
                    self.draw_polygon(event.x, event.y)
                elif self.current_tool == "text":
                    self.draw_text(event.x, event.y)
                elif self.current_tool == "eraser":
                    self.draw_eraser(event.x, event.y)
                elif self.current_tool == "spray":
                    self.draw_spray(event.x, event.y)
            self.last_x, self.last_y = event.x, event.y
            self.update_image()

    def reset(self, event):
        self.last_x, self.last_y = None, None

    def apply_filter(self):
        if self.image:
            selected_filter = self.filter_var.get()
            if selected_filter == "black_white":
                self.image = ImageOps.grayscale(self.image)
            elif selected_filter == "contrast":
                enhancer = ImageEnhance.Contrast(self.image)
                self.image = enhancer.enhance(2.0)
            elif selected_filter == "sharpness":
                enhancer = ImageEnhance.Sharpness(self.image)
                self.image = enhancer.enhance(3.0)
            elif selected_filter == "blur":
                self.image = self.image.filter(ImageFilter.BLUR)
            elif selected_filter == "contour":
                self.image = self.image.filter(ImageFilter.CONTOUR)
            self.update_image()

    def update_image(self):
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(400, 300, image=self.tk_image)

    def undo(self, event=None):
        if self.undo_stack:
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop()
            self.update_image()

    def redo(self, event=None):
        if self.redo_stack:
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.update_image()

    def draw_line(self, x, y):
        if self.stroke_style == "solid":
            self.draw.line([self.last_x, self.last_y, x, y], fill=self.color, width=self.brush_size_scale.get())
        elif self.stroke_style == "dashed":
            self.draw_dashed_line(self.last_x, self.last_y, x, y)
        elif self.stroke_style == "dotted":
            self.draw_dotted_line(self.last_x, self.last_y, x, y)

    def draw_dashed_line(self, x1, y1, x2, y2):
        dash_length = 10
        for i in range(0, int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5), dash_length):
            if i % (2 * dash_length) < dash_length:
                continue
            mid_x = x1 + (x2 - x1) * (i / int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5))
            mid_y = y1 + (y2 - y1) * (i / int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5))
            self.draw.line([mid_x, mid_y, mid_x + 5, mid_y + 5], fill=self.color, width=self.brush_size_scale.get())

    def draw_dotted_line(self, x1, y1, x2, y2):
        dot_length = 5
        for i in range(0, int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5), dot_length):
            if i % (2 * dot_length) < dot_length:
                continue
            mid_x = x1 + (x2 - x1) * (i / int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5))
            mid_y = y1 + (y2 - y1) * (i / int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5))
            self.draw.ellipse([mid_x, mid_y, mid_x + 1, mid_y + 1], fill=self.color, outline=self.color)

    def draw_rectangle(self, x, y):
        self.draw.rectangle([self.last_x, self.last_y, x, y], outline=self.color, fill=self.fill_color, width=self.brush_size_scale.get())

    def draw_circle(self, x, y):
        self.draw.ellipse([self.last_x, self.last_y, x, y], outline=self.color, fill=self.fill_color, width=self.brush_size_scale.get())

    def draw_polygon(self, x, y):
        self.draw.polygon([self.last_x, self.last_y, x, y], fill=self.fill_color, outline=self.color)

    def draw_text(self, x, y):
        text = simpledialog.askstring("Input", "Enter text:")
        if text:
            self.draw.text((x, y), text, fill=self.color, font=("Arial", self.brush_size_scale.get()))

    def draw_eraser(self, x, y):
        self.draw.rectangle([x - self.brush_size_scale.get() / 2, y - self.brush_size_scale.get() / 2, x + self.brush_size_scale.get() / 2, y + self.brush_size_scale.get() / 2], fill="white", outline="white")

    def draw_spray(self, x, y):
        for _ in range(10):
            spray_x = x + random.randint(-self.brush_size_scale.get(), self.brush_size_scale.get())
            spray_y = y + random.randint(-self.brush_size_scale.get(), self.brush_size_scale.get())
            self.draw.ellipse([spray_x, spray_y, spray_x + 1, spray_y + 1], fill=self.color, outline=self.color)

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoPaintApp(root)
    root.mainloop()
