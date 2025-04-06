import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import subprocess
import sys
version = "1.0.1a"
# Lista wymaganych bibliotek (usuń standardowe biblioteki Pythona)
REQUIRED_LIBRARIES = [
    "tk", "pydub", "numpy", "sounddevice", "librosa", "transformers", "tensorflow"
]

# Sprawdzanie i instalacja brakujących bibliotek
def check_and_install_dependencies():
    missing_libraries = []
    for lib in REQUIRED_LIBRARIES:
        try:
            __import__(lib)
        except ImportError:
            missing_libraries.append(lib)
    
    if missing_libraries:
        install_command = [sys.executable, "-m", "pip", "install"] + missing_libraries
        subprocess.run(install_command, check=True)
        messagebox.showinfo("Installation", f"Installed missing libraries: {', '.join(missing_libraries)}")

# Funkcja pomocnicza do wyboru pliku
def select_file(entry, title, filetypes):
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

# Funkcje wywołujące odpowiednie moduły przy użyciu subprocess
def run_audio_extraction():
    video_file = entry_video.get().strip()
    if not video_file or not os.path.exists(video_file):
        messagebox.showerror("Error", "Select a valid video file!")
        return
    subprocess.run([sys.executable, "audio_extraction.py", video_file])
    messagebox.showinfo("Success", "Audio extraction module finished.")

def run_audio_recognition():
    audio_file = entry_audio.get().strip()
    if not audio_file or not os.path.exists(audio_file):
        messagebox.showerror("Error", "Select a valid audio file!")
        return
    subprocess.run([sys.executable, "pronoun_recognition.py", audio_file])
    messagebox.showinfo("Success", "Pronoun recognition module finished.")

def run_ass_translation():
    ass_file = entry_ass.get().strip()
    pronoun_file = entry_pronoun.get().strip()
    if not ass_file or not os.path.exists(ass_file):
        messagebox.showerror("Error", "Select a valid ASS subtitle file!")
        return
    if not pronoun_file or not os.path.exists(pronoun_file):
        pronoun_file = os.path.join("..", "tempsf", "temp_data.txt")  # default pronoun file
    subprocess.run([sys.executable, "main_translator.py", ass_file, pronoun_file])
    messagebox.showinfo("Success", "ASS translation module finished.")

def run_ass_correction():
    ass_file = entry_ass.get().strip()
    pronoun_file = entry_pronoun.get().strip()
    if not ass_file or not os.path.exists(ass_file):
        messagebox.showerror("Error", "Select a valid ASS subtitle file!")
        return
    if not pronoun_file or not os.path.exists(pronoun_file):
        pronoun_file = os.path.join("..", "tempsf", "temp_data.txt")  # default pronoun file
    subprocess.run([sys.executable, "validate_ass.py", ass_file, pronoun_file])
    messagebox.showinfo("Success", "ASS correction module finished.")

# Funkcja ładująca plik słownika z folderu Mods i wyświetlająca jego zawartość
def load_custom_dictionary():
    selection = custom_listbox.curselection()
    if not selection:
        messagebox.showerror("Error", "Select a dictionary file from the list!")
        return
    filename = custom_listbox.get(selection[0])
    file_path = os.path.join("Mods", filename)
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "Selected file does not exist!")
        return
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        messagebox.showerror("Error", f"Could not read file: {e}")
        return

    # Otwórz nowe okno i wyświetl zawartość
    dict_window = tk.Toplevel(root)
    dict_window.title(f"Dictionary: {filename}")
    dict_text = scrolledtext.ScrolledText(dict_window, width=80, height=20, wrap=tk.WORD)
    dict_text.pack(padx=10, pady=10)
    dict_text.insert(tk.END, content)
    dict_text.configure(state="disabled")

# Funkcja zmieniająca widoczny moduł
def switch_module(*args):
    module = module_var.get()
    extraction_frame.pack_forget()
    recognition_frame.pack_forget()
    ass_frame.pack_forget()
    custom_frame.pack_forget()
    action_button.pack_forget()  # ukrywamy główny przycisk
    if module == "audio_extraction":
        extraction_frame.pack(padx=10, pady=10, fill=tk.X)
        action_button.config(text="Run Audio Extraction", command=run_audio_extraction)
        action_button.pack(pady=20)
    elif module == "audio_recognition":
        recognition_frame.pack(padx=10, pady=10, fill=tk.X)
        action_button.config(text="Run Pronoun Recognition", command=run_audio_recognition)
        action_button.pack(pady=20)
    elif module == "ass_translation":
        ass_frame.pack(padx=10, pady=10, fill=tk.X)
        action_button.config(text="Run ASS Translation", command=run_ass_translation)
        action_button.pack(pady=20)
    elif module == "ass_correction":
        ass_frame.pack(padx=10, pady=10, fill=tk.X)
        action_button.config(text="Run ASS Correction", command=run_ass_correction)
        action_button.pack(pady=20)
    elif module == "custom_dictionary":
        custom_frame.pack(padx=10, pady=10, fill=tk.BOTH)
        # Lista plików zostanie wczytana przy uruchomieniu modułu
        populate_custom_listbox()

# Funkcja wczytująca listę plików ze folderu Mods
def populate_custom_listbox():
    custom_listbox.delete(0, tk.END)
    mods_folder = "Mods"
    if not os.path.exists(mods_folder):
        messagebox.showerror("Error", "Folder 'Mods' not found!")
        return
    files = os.listdir(mods_folder)
    if not files:
        custom_listbox.insert(tk.END, "No dictionary files found.")
    else:
        for file in files:
            custom_listbox.insert(tk.END, file)

# Sprawdzenie i instalacja zależności przed uruchomieniem GUI
check_and_install_dependencies()

root = tk.Tk()
root.title("AI Translator - Modules")
root.geometry("600x500")

module_var = tk.StringVar(value="audio_extraction")
module_frame = tk.LabelFrame(root, text="Choose Module", padx=10, pady=10)
module_frame.pack(padx=10, pady=10, fill=tk.X)

tk.Radiobutton(module_frame, text="Extract audio from video", variable=module_var,
               value="audio_extraction", command=switch_module).pack(anchor=tk.W)
tk.Radiobutton(module_frame, text="Recognize pronouns from audio file", variable=module_var,
               value="audio_recognition", command=switch_module).pack(anchor=tk.W)
tk.Radiobutton(module_frame, text="Translate ASS", variable=module_var,
               value="ass_translation", command=switch_module).pack(anchor=tk.W)
tk.Radiobutton(module_frame, text="Correct pronouns in ASS", variable=module_var,
               value="ass_correction", command=switch_module).pack(anchor=tk.W)
tk.Radiobutton(module_frame, text="Custom Dictionary", variable=module_var,
               value="custom_dictionary", command=switch_module).pack(anchor=tk.W)

# Frame dla audio extraction
extraction_frame = tk.LabelFrame(root, text="Audio Extraction", padx=10, pady=10)
tk.Label(extraction_frame, text="Video file (MP4):").pack(anchor=tk.W)
entry_video = tk.Entry(extraction_frame, width=50)
entry_video.pack(side=tk.LEFT, padx=5)
tk.Button(extraction_frame, text="Choose", 
          command=lambda: select_file(entry_video, "Choose video file", [("MP4 Files", "*.mp4")])).pack(side=tk.LEFT, padx=5)

# Frame dla audio recognition
recognition_frame = tk.LabelFrame(root, text="Pronoun Recognition from Audio", padx=10, pady=10)
tk.Label(recognition_frame, text="Audio file (WAV):").pack(anchor=tk.W)
entry_audio = tk.Entry(recognition_frame, width=50)
entry_audio.pack(side=tk.LEFT, padx=5)
tk.Button(recognition_frame, text="Choose", 
          command=lambda: select_file(entry_audio, "Choose audio file", [("WAV Files", "*.wav")])).pack(side=tk.LEFT, padx=5)

# Frame dla ASS translation/correction
ass_frame = tk.LabelFrame(root, text="ASS Translation and Correction", padx=10, pady=10)
tk.Label(ass_frame, text="ASS file:").pack(anchor=tk.W)
entry_ass = tk.Entry(ass_frame, width=50)
entry_ass.pack(side=tk.LEFT, padx=5)
tk.Button(ass_frame, text="Choose", 
          command=lambda: select_file(entry_ass, "Choose ASS file", [("ASS Files", "*.ass")])).pack(side=tk.LEFT, padx=5)
tk.Label(ass_frame, text="Pronoun file (optional):").pack(anchor=tk.W, pady=(10,0))
entry_pronoun = tk.Entry(ass_frame, width=50)
entry_pronoun.pack(side=tk.LEFT, padx=5)
tk.Button(ass_frame, text="Choose", 
          command=lambda: select_file(entry_pronoun, "Choose pronoun file", [("TXT Files", "*.txt")])).pack(side=tk.LEFT, padx=5)

# Frame dla Custom Dictionary
custom_frame = tk.LabelFrame(root, text="Custom Dictionary", padx=10, pady=10)
tk.Label(custom_frame, text="Select a dictionary file from 'Mods':").pack(anchor=tk.W)
custom_listbox = tk.Listbox(custom_frame, width=50, height=5)
custom_listbox.pack(padx=5, pady=5)
tk.Button(custom_frame, text="Load Dictionary", command=load_custom_dictionary).pack(pady=10)

# Przyciski
action_button = tk.Button(root, text="Run", width=20)

# Uruchomienie GUI
root.mainloop()
