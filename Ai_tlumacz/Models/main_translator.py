import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar
import tensorflow as tf
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import time

# Ładowanie modelu tłumaczeniowego
def load_translation_model():
    model_name = "facebook/nllb-200-1.3B"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return model, tokenizer

# Funkcje do przetwarzania tekstu z ASS
def extract_text_and_styles(text):
    """Zachowuje style ASS i wyodrębnia czysty tekst do tłumaczenia."""
    styles = re.findall(r'(\{[^}]*\})', text)
    clean_text = re.sub(r'\{[^}]*\}', '', text).strip()
    return clean_text, styles

def rebuild_text_with_styles(translated_text, styles):
    """Dodaje zachowane style do przetłumaczonego tekstu."""
    return ''.join(styles) + translated_text

def translate_text(text, model, tokenizer):
    """Tłumaczy tekst, zachowując symbole i style."""
    if not text.strip():
        return text  # Nie tłumaczy pustych linii
    
    clean_text, styles = extract_text_and_styles(text)
    
    source_lang = 'eng_Latn'
    target_lang = 'pol_Latn'
    
    inputs = tokenizer(clean_text, return_tensors="pt", padding=True, truncation=True)
    
    outputs = model.generate(**inputs, forced_bos_token_id=tokenizer.convert_tokens_to_ids(target_lang))
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return rebuild_text_with_styles(translated_text, styles)

# Funkcja do zastosowania reguł słownika
def apply_mod_rules(translated_text, mod_rules):
    for rule in mod_rules.get("replace", []):
        old, new = rule
        translated_text = translated_text.replace(old, new)
    
    for ignore_text in mod_rules.get("ignore", []):
        translated_text = translated_text.replace(ignore_text, "")
    
    for del_text in mod_rules.get("delete", []):
        translated_text = translated_text.replace(del_text, "")
    
    return translated_text

# Wczytywanie reguł z pliku słownika
def load_mod_rules(file_path):
    mod_rules = {"replace": [], "ignore": [], "delete": []}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_section = None
    for line in lines:
        line = line.strip()
        if line.startswith("[replace]"):
            current_section = "replace"
        elif line.startswith("[Ignore]"):
            current_section = "ignore"
        elif line.startswith("[delete]"):  # Zmieniono z [delate] na [delete]
            current_section = "delete"
        elif current_section:
            # Przetwarzanie reguł
            if current_section == "replace":
                parts = line.split(":", 1)
                if len(parts) == 2:
                    mod_rules["replace"].append((parts[0].strip(), parts[1].strip()))
            elif current_section == "ignore":
                mod_rules["ignore"].append(line)
            elif current_section == "delete":
                mod_rules["delete"].append(line)
    
    return mod_rules

# Procesowanie pliku ASS
def process_ass_file(input_ass_path, output_ass_path, model, tokenizer, mod_rules):
    with open(input_ass_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output_lines = []
    total_lines = len(lines)
    translated_lines = 0
    start_time = time.time()
    
    for line in lines:
        if line.startswith("Dialogue:"):
            parts = line.split(',', maxsplit=9)
            if len(parts) >= 10:
                dialogue_text = parts[9]
                translated_text = translate_text(dialogue_text, model, tokenizer)
                # Zastosowanie reguł słownika do przetłumaczonego tekstu
                translated_text = apply_mod_rules(translated_text, mod_rules)
                new_line = ','.join(parts[:9]) + ',' + translated_text + "\n"
                output_lines.append(new_line)
                
                translated_lines += 1
                print(f"{translated_lines}/{total_lines} - {dialogue_text}\n{translated_text}\n")
        else:
            output_lines.append(line)
    
    with open(output_ass_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"Zapisano przetłumaczony plik: {output_ass_path}")

# GUI i interakcja z użytkownikiem
def select_ass_file(entry):
    ass_file = filedialog.askopenfilename(title="Wybierz plik ASS", filetypes=[("Pliki ASS", "*.ass")])
    if ass_file:
        if ass_file.endswith(".ass"):
            entry.delete(0, tk.END)
            entry.insert(0, ass_file)
        else:
            messagebox.showerror("Błąd", "Proszę wybrać plik z rozszerzeniem .ass")

def select_mod_file(entry):
    mod_file = filedialog.askopenfilename(title="Wybierz plik słownika", filetypes=[("Pliki tekstowe", "*.txt")])
    if mod_file:
        if mod_file.endswith(".txt"):
            entry.delete(0, tk.END)
            entry.insert(0, mod_file)
        else:
            messagebox.showerror("Błąd", "Proszę wybrać plik z rozszerzeniem .txt")

def start_translation():
    input_ass_file = entry_ass.get().strip()
    if not input_ass_file or not os.path.exists(input_ass_file):
        messagebox.showerror("Błąd", "Nie wybrano pliku ASS!")
        return
    
    mod_file = entry_mod.get().strip()
    mod_rules = {}
    if mod_file and os.path.exists(mod_file):
        mod_rules = load_mod_rules(mod_file)
    
    model, tokenizer = load_translation_model()
    
    output_ass_file = filedialog.asksaveasfilename(title="Zapisz przetłumaczony plik jako", defaultextension=".ass", filetypes=[("Pliki ASS", "*.ass")])
    if not output_ass_file:
        messagebox.showerror("Błąd", "Nie wybrano ścieżki zapisu!")
        return
    
    process_ass_file(input_ass_file, output_ass_file, model, tokenizer, mod_rules)
    messagebox.showinfo("Sukces", "Plik został przetłumaczony i zapisany!")

# Tworzenie GUI
root = tk.Tk()
root.title("Translate ASS with Mod Dictionary")
root.geometry("600x400")

# Wybór pliku ASS
tk.Label(root, text="Wybierz plik z napisami ASS:").pack(pady=5)
entry_ass = tk.Entry(root, width=50)
entry_ass.pack(padx=10)
tk.Button(root, text="Wybierz plik", command=lambda: select_ass_file(entry_ass)).pack(pady=5)

# Wybór pliku słownika
tk.Label(root, text="Wybierz plik słownika z folderu Mods:").pack(pady=5)
entry_mod = tk.Entry(root, width=50)
entry_mod.pack(padx=10)
tk.Button(root, text="Wybierz plik słownika", command=lambda: select_mod_file(entry_mod)).pack(pady=5)

# Przyciski do rozpoczęcia tłumaczenia
tk.Button(root, text="Rozpocznij tłumaczenie", command=start_translation).pack(pady=20)

root.mainloop()
