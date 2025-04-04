import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import sys

REQUIRED_LIBRARIES = [
    "tk", "pydub", "numpy", "sounddevice", "librosa", "transformers", "tensorflow",
    "re", "os", "collections", "time"
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
        messagebox.showinfo("Instalacja", f"Zainstalowano brakujące biblioteki: {', '.join(missing_libraries)}")

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
        messagebox.showerror("Błąd", "Wybierz poprawny plik wideo!")
        return
    subprocess.run(["python3", "wyodrebnienie_dzwieku.py", video_file])
    messagebox.showinfo("Sukces", "Moduł wyodrębniania audio zakończył pracę.")

def run_audio_recognition():
    audio_file = entry_audio.get().strip()
    if not audio_file or not os.path.exists(audio_file):
        messagebox.showerror("Błąd", "Wybierz poprawny plik audio!")
        return
    subprocess.run(["python3", "rozpoznanie_zaimnkow.py", audio_file])
    messagebox.showinfo("Sukces", "Moduł rozpoznania zaimków zakończył pracę.")

def run_ass_translation():
    ass_file = entry_ass.get().strip()
    pronoun_file = entry_pronoun.get().strip()
    if not ass_file or not os.path.exists(ass_file):
        messagebox.showerror("Błąd", "Wybierz poprawny plik napisów ASS!")
        return
    if not pronoun_file or not os.path.exists(pronoun_file):
        pronoun_file = os.path.join("..", "tempsf", "temp_data.txt")  # domyślny plik zaimków
    subprocess.run(["python3", "glowny_tlumacz.py", ass_file, pronoun_file])
    messagebox.showinfo("Sukces", "Moduł tłumaczenia ASS zakończył pracę.")

def run_ass_correction():
    ass_file = entry_ass.get().strip()
    pronoun_file = entry_pronoun.get().strip()
    if not ass_file or not os.path.exists(ass_file):
        messagebox.showerror("Błąd", "Wybierz poprawny plik napisów ASS!")
        return
    if not pronoun_file or not os.path.exists(pronoun_file):
        pronoun_file = os.path.join("..", "tempsf", "temp_data.txt")  # domyślny plik zaimków
    subprocess.run(["python3", "is_correct_ass.py", ass_file, pronoun_file])
    messagebox.showinfo("Sukces", "Moduł poprawy zaimków w ASS zakończył pracę.")

def switch_module(*args):
    module = module_var.get()
    extraction_frame.pack_forget()
    recognition_frame.pack_forget()
    ass_frame.pack_forget()
    action_button.config(command=lambda: None)
    if module == "audio_extraction":
        extraction_frame.pack(padx=10, pady=10, fill=tk.X)
        action_button.config(text="Uruchom wyodrębnianie audio", command=run_audio_extraction)
    elif module == "audio_recognition":
        recognition_frame.pack(padx=10, pady=10, fill=tk.X)
        action_button.config(text="Uruchom rozpoznanie zaimków", command=run_audio_recognition)
    elif module == "ass_translation":
        ass_frame.pack(padx=10, pady=10, fill=tk.X)
        action_button.config(text="Uruchom tłumaczenie ASS", command=run_ass_translation)
    elif module == "ass_correction":
        ass_frame.pack(padx=10, pady=10, fill=tk.X)
        action_button.config(text="Uruchom korektę zaimków w ASS", command=run_ass_correction)

# Sprawdzenie i instalacja zależności przed uruchomieniem GUI
check_and_install_dependencies()

root = tk.Tk()
root.title("AI Tłumacz - Moduły")
root.geometry("500x400")

module_var = tk.StringVar(value="audio_extraction")
module_frame = tk.LabelFrame(root, text="Wybierz moduł", padx=10, pady=10)
module_frame.pack(padx=10, pady=10, fill=tk.X)

tk.Radiobutton(module_frame, text="Wyodrębnij audio z wideo", variable=module_var,
               value="audio_extraction", command=switch_module).pack(anchor=tk.W)
tk.Radiobutton(module_frame, text="Rozpoznaj zaimki z pliku audio", variable=module_var,
               value="audio_recognition", command=switch_module).pack(anchor=tk.W)
tk.Radiobutton(module_frame, text="Tłumacz ASS", variable=module_var,
               value="ass_translation", command=switch_module).pack(anchor=tk.W)
tk.Radiobutton(module_frame, text="Popraw zaimki w ASS", variable=module_var,
               value="ass_correction", command=switch_module).pack(anchor=tk.W)

extraction_frame = tk.LabelFrame(root, text="Wyodrębnianie audio", padx=10, pady=10)
tk.Label(extraction_frame, text="Plik wideo (MP4):").pack(anchor=tk.W)
entry_video = tk.Entry(extraction_frame, width=50)
entry_video.pack(side=tk.LEFT, padx=5)
tk.Button(extraction_frame, text="Wybierz", 
          command=lambda: select_file(entry_video, "Wybierz plik wideo", [("Pliki MP4", "*.mp4")])).pack(side=tk.LEFT, padx=5)

recognition_frame = tk.LabelFrame(root, text="Rozpoznanie z pliku audio", padx=10, pady=10)
tk.Label(recognition_frame, text="Plik audio (WAV):").pack(anchor=tk.W)
entry_audio = tk.Entry(recognition_frame, width=50)
entry_audio.pack(side=tk.LEFT, padx=5)
tk.Button(recognition_frame, text="Wybierz", 
          command=lambda: select_file(entry_audio, "Wybierz plik audio", [("Pliki WAV", "*.wav")])).pack(side=tk.LEFT, padx=5)

ass_frame = tk.LabelFrame(root, text="Tłumaczenie i poprawa ASS", padx=10, pady=10)
tk.Label(ass_frame, text="Plik ASS:").pack(anchor=tk.W)
entry_ass = tk.Entry(ass_frame, width=50)
entry_ass.pack(side=tk.LEFT, padx=5)
tk.Button(ass_frame, text="Wybierz", 
          command=lambda: select_file(entry_ass, "Wybierz plik ASS", [("Pliki ASS", "*.ass")])).pack(side=tk.LEFT, padx=5)
tk.Label(ass_frame, text="Plik zaimków (opcjonalnie):").pack(anchor=tk.W, pady=(10,0))
entry_pronoun = tk.Entry(ass_frame, width=50)
entry_pronoun.pack(side=tk.LEFT, padx=5)
tk.Button(ass_frame, text="Wybierz", 
          command=lambda: select_file(entry_pronoun, "Wybierz plik zaimków", [("Pliki TXT", "*.txt")])).pack(side=tk.LEFT, padx=5)

action_button = tk.Button(root, text="", font=("Arial", 12, "bold"))
action_button.pack(pady=20)

switch_module()

root.mainloop()
