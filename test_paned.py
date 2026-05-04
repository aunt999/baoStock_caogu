# Test PanedWindow layout
import tkinter as tk

root = tk.Tk()
root.title("PanedWindow Test")
root.geometry("1200x600")
root.configure(bg="#1a1a2e")

# Create PanedWindow
main_paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg="#1a1a2e")
main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Left panel
left_frame = tk.Frame(main_paned, bg="#0d1117")
left_frame.pack_propagate(False)
main_paned.add(left_frame, stretch="always")

left_label = tk.Label(left_frame, text="LEFT PANEL - Chart Area", bg="#0d1117", fg="white", font=("Microsoft YaHei", 16))
left_label.pack(expand=True)

# Right panel
right_frame = tk.Frame(main_paned, bg="#16213e", width=300)
right_frame.pack_propagate(False)
main_paned.add(right_frame, minsize=300)

right_label = tk.Label(right_frame, text="RIGHT PANEL\nInfo Area", bg="#16213e", fg="#00b4d8", font=("Microsoft YaHei", 14, "bold"))
right_label.pack(expand=True)

# Add some content to right panel
for i in range(5):
    tk.Label(right_frame, text=f"Item {i+1}", bg="#16213e", fg="white").pack(pady=5)

# Set sash position
root.update_idletasks()
main_paned.sash_place(0, 850, 0)

root.mainloop()
