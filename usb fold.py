import os
import random
import string
import shutil
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, scrolledtext, ttk
from queue import Queue
import subprocess
import time
import psutil

def random_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def format_drive(drive_path, log_queue=None):
    try:
        for item in os.listdir(drive_path):
            item_path = os.path.join(drive_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        if log_queue:
            log_queue.put(f"[+] Drive {drive_path} formatted.\n")
    except Exception as e:
        if log_queue:
            log_queue.put(f"[!] Error formatting drive: {e}\n")

def create_folders(drive, depth, width, log_queue=None, progress_callback=None):
    folders = []
    total_folders = (width ** (depth + 1) - 1) // (width - 1)
    created_folders = 0
    start_time = time.time()

    def recurse(path, current_depth):
        nonlocal created_folders
        if current_depth > depth:
            return
        for _ in range(width):
            folder_name = random_name()
            new_path = os.path.join(path, folder_name)
            os.makedirs(new_path, exist_ok=True)
            folders.append(new_path)

            created_folders += 1
            if log_queue:
                log_queue.put(f"[+] Created: {new_path}\n")
            if progress_callback:
                elapsed = time.time() - start_time
                folders_per_sec = created_folders / elapsed if elapsed > 0 else 0
                remaining = total_folders - created_folders
                eta = int(remaining / folders_per_sec) if folders_per_sec else 0
                percent_done = (created_folders / total_folders) * 100
                progress_callback(created_folders, total_folders, percent_done, eta)

            recurse(new_path, current_depth + 1)

    recurse(drive, 1)
    return folders

def start_gui():
    global root, drive_combo
    root = tk.Tk()
    root.title("USB Encryptor")
    root.geometry("500x150")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    drive_label = tk.Label(frame, text="Select Drive / Folder:")
    drive_label.grid(row=0, column=0, padx=5)

    drive_combo = ttk.Combobox(frame, width=30)
    drive_combo.grid(row=0, column=1, padx=5)

    browse_button = tk.Button(frame, text="Browse", command=browse_drive)
    browse_button.grid(row=0, column=2, padx=5)

    start_button = tk.Button(root, text="Start", command=start)
    start_button.pack(pady=10)

    update_drive_list()
    root.mainloop()

def browse_drive():
    selected_folder = filedialog.askdirectory()
    if selected_folder:
        drive_combo.set(selected_folder)

def update_drive_list():
    drives = []
    removable_drive = None

    for part in psutil.disk_partitions(all=False):
        if 'removable' in part.opts.lower() or 'cdrom' in part.opts.lower():
            removable_drive = part.device
        drives.append(part.device)

    drive_combo["values"] = drives

    if removable_drive:
        drive_combo.set(removable_drive)
    elif drives:
        drive_combo.set(drives[0])

def start():
    drive_path = drive_combo.get()
    if not drive_path or not os.path.exists(drive_path):
        messagebox.showerror("Error", "Please select a valid drive/folder!")
        return

    password_file = find_file(drive_path, "hawk_tuah.txt")
    folder_file = find_file(drive_path, "krokodildo.txt")

    if password_file and folder_file:
        password = read_file(password_file)
        folder_path = read_file(folder_file)

        input_password = simpledialog.askstring("Password", "Enter password:", show="*")
        if input_password == password:
            normalized_folder_path = folder_path.replace("/", "\\")
            if os.path.exists(normalized_folder_path):
                open_folder(normalized_folder_path)
            else:
                messagebox.showerror("Error", f"Folder path '{normalized_folder_path}' does not exist!")
        else:
            messagebox.showerror("Error", "Wrong password!")
    else:
        setup_password = simpledialog.askstring("Set Password", "No password found. Set a new password:", show="*")
        if not setup_password:
            messagebox.showwarning("Cancelled", "Password setup cancelled.")
            return

        answer = messagebox.askyesno("Format Drive", "Do you want to format and setup encryption?")
        if answer:
            threading.Thread(target=setup_drive, args=(drive_path, setup_password)).start()

def find_file(base_folder, filename):
    for root_dir, dirs, files in os.walk(base_folder):
        if filename in files:
            return os.path.join(root_dir, filename)
    return None

def read_file(path):
    with open(path, "r") as f:
        return f.read().strip()

def setup_drive(drive_path, password):
    global log_window, log_text, progress_bar, progress_label, save_log_button, log_queue
    log_queue = Queue()

    def log_worker():
        while True:
            message = log_queue.get()
            if message is None:
                break
            log_text.insert(tk.END, message)
            log_text.see(tk.END)

    log_window = tk.Toplevel(root)
    log_window.title("Setup Log")
    log_window.state('zoomed')

    top_frame = tk.Frame(log_window)
    top_frame.pack(fill=tk.X)

    progress_bar = ttk.Progressbar(top_frame, orient="horizontal", mode="determinate")
    progress_bar.pack(fill=tk.X, padx=10, pady=10)

    progress_label = tk.Label(top_frame, text="Progress: 0/0 (0%) | ETA: --s")
    progress_label.pack()

    save_log_button = tk.Button(top_frame, text="Save Log", command=save_log)
    save_log_button.pack(pady=5)

    log_text = scrolledtext.ScrolledText(log_window, bg="black", fg="lime", insertbackground="lime")
    log_text.pack(fill=tk.BOTH, expand=True)

    threading.Thread(target=log_worker, daemon=True).start()

    log_queue.put("[*] Formatting drive...\n")
    format_drive(drive_path, log_queue=log_queue)

    log_queue.put("[*] Creating folders...\n")

    def update_progress(current, total, percent, eta):
        progress_bar["maximum"] = total
        progress_bar["value"] = current
        progress_label.config(text=f"Progress: {current}/{total} ({percent:.2f}%) | ETA: {eta}s")

    folders = create_folders(drive_path, depth=5, width=5, log_queue=log_queue, progress_callback=update_progress)

    hidden_folder = random.choice(folders)
    files_folder = random.choice(folders)

    with open(os.path.join(hidden_folder, "hawk_tuah.txt"), "w") as f:
        f.write(password)
    with open(os.path.join(hidden_folder, "krokodildo.txt"), "w") as f:
        f.write(files_folder)

    log_queue.put(f"[+] Password and folder paths saved!\n")
    log_queue.put("[✓] Setup Complete!\n")
    log_queue.put(None)

    save_log()

    messagebox.showinfo("Setup", "Encryption setup complete!")

def save_log():
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = os.path.join(desktop_path, "setup_log.txt")
        with open(filename, "w") as f:
            f.write(log_text.get("1.0", tk.END))
        messagebox.showinfo("Saved", f"Log saved to Desktop as 'setup_log.txt'")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save log: {e}")

def open_folder(path):
    normalized_path = path.replace("/", "\\")
    if os.path.exists(normalized_path):
        subprocess.Popen(f'explorer "{normalized_path}"')
    else:
        messagebox.showerror("Error", f"Folder path '{normalized_path}' not found!")

if __name__ == "__main__":
    start_gui()
