import tkinter as tk
import webbrowser

def load_page():
    url = entry.get()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    webbrowser.open(url)

root = tk.Tk()
root.title("Mini Navigateur Web")

entry = tk.Entry(root, width=80)
entry.pack(pady=10)

button = tk.Button(root, text="Go", command=load_page)
button.pack(pady=10)

root.mainloop()
