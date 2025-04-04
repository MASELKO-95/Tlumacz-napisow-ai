import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import tensorflow as tf
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import time

def load_translation_model():
    model_name = "facebook/nllb-200-1.3B"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return model, tokenizer

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

def process_ass_file(input_ass_path, output_ass_path, model, tokenizer):
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
                new_line = ','.join(parts[:9]) + ',' + translated_text + "\n"
                output_lines.append(new_line)
                
                translated_lines += 1
                print(f"{translated_lines}/{total_lines} - {dialogue_text}\n{translated_text}\n")
        else:
            output_lines.append(line)
    
    with open(output_ass_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"Zapisano przetłumaczony plik: {output_ass_path}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    input_ass_file = filedialog.askopenfilename(title="Wybierz plik z napisami (ASS)", filetypes=[("Pliki ASS", "*.ass")])
    if not input_ass_file:
        messagebox.showerror("Błąd", "Nie wybrano pliku!")
        exit()
    
    model, tokenizer = load_translation_model()
    
    output_ass_file = filedialog.asksaveasfilename(title="Zapisz przetłumaczony plik jako", defaultextension=".ass", filetypes=[("Pliki ASS", "*.ass")])
    if not output_ass_file:
        messagebox.showerror("Błąd", "Nie wybrano ścieżki zapisu!")
        exit()
    
    process_ass_file(input_ass_file, output_ass_file, model, tokenizer)
    messagebox.showinfo("Sukces", "Plik został przetłumaczony i zapisany!")
