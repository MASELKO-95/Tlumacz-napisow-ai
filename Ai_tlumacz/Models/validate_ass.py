import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os

# Funkcja do konwersji czasu w formacie HH:MM:SS na sekundy
def time_to_seconds(time_str):
    parts = time_str.split(':')
    if len(parts) != 3:
        return 0
    hrs, mins, secs = parts
    return int(hrs) * 3600 + int(mins) * 60 + float(secs)

# Funkcja wczytująca dane o płci z pliku TXT
def load_gender_intervals(txt_file):
    intervals = []
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                gender = parts[0]
                times = parts[1].split('-')
                if len(times) != 2:
                    continue
                start = time_to_seconds(times[0])
                end = time_to_seconds(times[1])
                intervals.append({'gender': gender, 'start': start, 'end': end})
    except FileNotFoundError:
        print(f"Plik {txt_file} nie został znaleziony.")
    return intervals

# Funkcja do zamiany zaimków męskich na żeńskie
def adjust_pronouns(text):
    masc_to_fem = {
        "ja kupiłem": "ja kupiłam", "ja byłem": "ja byłam", "ja zrobiłem": "ja zrobiłam", 
        "ja widziałem": "ja widziałam", "ja powiedziałem": "ja powiedziałam", "ja napisałem": "ja napisałam", 
        "ja poszedłem": "ja poszłam", "ja znalazłem": "ja znalazłam", "ja wziąłem": "ja wzięłam", 
        "ja czekałem": "ja czekałam", "ja zapytałem": "ja zapytałam", "ja dostałem": "ja dostałam", 
        "ja wiedziałem": "ja wiedziałam", "ja myślałem": "ja myślałam", "ja czułem": "ja czułam", 
        "ja słyszałem": "ja słyszałam", "ja rozumiałem": "ja rozumiałam", "ja chciałem": "ja chciałam", 
        "ja mogłem": "ja mogłam", "ja musiałem": "ja musiałam", "ja spałem": "ja spałam", "ja siedziałem": "ja siedziałam", 
        "ja stałem": "ja stałam", "ja chodziłem": "ja chodziłam", "ja jechałem": "ja jechałam", "ja pracowałem": "ja pracowałam", 
        "ja odpoczywałem": "ja odpoczywałam", "ty kupiłeś": "ty kupiłaś", "ty byłeś": "ty byłaś", 
        "ty zrobiłeś": "ty zrobiłaś", "ty widziałeś": "ty widziałaś", "ty powiedziałeś": "ty powiedziałaś", 
        "ty napisałeś": "ty napisałaś", "ty poszedłeś": "ty poszłaś", "ty znalazłeś": "ty znalazłaś", 
        "ty wziąłeś": "ty wzięłaś", "ty czekałeś": "ty czekałaś", "ty zapytałeś": "ty zapytałaś", 
        "ty dostałeś": "ty dostałaś", "ty wiedziałeś": "ty wiedziałaś", "ty myślałeś": "ty myślałaś", 
        "ty czułeś": "ty czułaś", "ty słyszałeś": "ty słyszałaś", "ty rozumiałeś": "ty rozumiałaś", 
        "ty chciałeś": "ty chciałaś", "ty mogłeś": "ty mogłaś", "ty musiałeś": "ty musiałaś", "ty spałeś": "ty spałaś", 
        "ty siedziałeś": "ty siedziałaś", "ty stałeś": "ty stałaś", "ty chodziłeś": "ty chodziłaś", 
        "ty jechałeś": "ty jechałaś", "ty pracowałeś": "ty pracowałaś", "ty odpoczywałeś": "ty odpoczywałaś", 
        "on kupił": "ona kupiła", "on był": "ona była", "on zrobił": "ona zrobiła", "on widział": "ona widziała", 
        "on powiedział": "ona powiedziała", "on napisał": "ona napisała", "on poszedł": "ona poszła", 
        "on znalazł": "ona znalazła", "on wziął": "ona wzięła", "on czekał": "ona czekała", "on zapytał": "ona zapytała", 
        "on dostał": "ona dostała", "on wiedział": "ona wiedziała", "on myślał": "ona myślała", "on czuł": "ona czuła", 
        "on słyszał": "ona słyszała", "on rozumiał": "ona rozumiała", "on chciał": "ona chciała", "on mógł": "ona mogła", 
        "on musiał": "ona musiała", "on spał": "ona spała", "on siedział": "ona siedziała", "on stał": "ona stała", 
        "on chodził": "ona chodziła", "on jechał": "ona jechała", "on pracował": "ona pracowała", 
        "on odpoczywał": "ona odpoczywała", "my kupiliśmy": "my kupiłyśmy", "my byliśmy": "my byłyśmy", 
        "my zrobiliśmy": "my zrobiłyśmy", "my widzieliśmy": "my widziałyśmy", "my powiedzieliśmy": "my powiedziałyśmy", 
        "my napisaliśmy": "my napisałyśmy", "my poszliśmy": "my poszłyśmy", "my znaleźliśmy": "my znalazłyśmy", 
        "my wzięliśmy": "my wzięłyśmy", "my czekaliśmy": "my czekałyśmy", "my zapytaliśmy": "my zapytałyśmy", 
        "my dostaliśmy": "my dostałyśmy", "my wiedzieliśmy": "my wiedziałyśmy", "my myśleliśmy": "my myślałyśmy", 
        "my czuliśmy": "my czułyśmy", "my słyszeliśmy": "my słyszałyśmy", "my rozumieliśmy": "my rozumiałyśmy", 
        "my chcieliśmy": "my chciałyśmy", "my mogliśmy": "my mogłyśmy", "my musieliśmy": "my musiałyśmy", 
        "my spaliśmy": "my spałyśmy", "my siedzieliśmy": "my siedziałyśmy", "my staliśmy": "my stałyśmy", 
        "my chodziliśmy": "my chodziłyśmy", "my jechaliśmy": "my jechałyśmy", "my pracowaliśmy": "my pracowałyśmy", 
        "my odpoczywaliśmy": "my odpoczywałyśmy", 
    }

    for masc, fem in masc_to_fem.items():
        text = re.sub(r'\b' + re.escape(masc) + r'\b', fem, text)
    return text

# Funkcja do przetwarzania pliku .ass
def process_ass_file(input_ass_path, output_ass_path, gender_intervals):
    try:
        with open(input_ass_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Plik {input_ass_path} nie został znaleziony.")
        return

    output_lines = []
    start_translation = False
    
    for line in lines:
        if not start_translation and line.strip() == "[Events]":
            start_translation = True
            output_lines.append(line)
            continue
        
        if not start_translation:
            output_lines.append(line)
            continue
        
        if line.startswith("Dialogue:"):
            parts = line.split(',', maxsplit=9)
            if len(parts) >= 10:
                start_time_str = parts[1].strip()
                start_time_sec = time_to_seconds(start_time_str)
                is_female = False
                for interval in gender_intervals:
                    if interval['start'] <= start_time_sec <= interval['end'] and interval['gender'] == '0':
                        is_female = True
                        break
                dialogue_text = parts[9].strip()
                tags = re.findall(r'(\\{[^}]+\\})', dialogue_text)
                clean_text = re.sub(r'(\\{[^}]+\\})', '', dialogue_text).strip()
                translated = clean_text  
                if is_female:
                    translated = adjust_pronouns(translated)
                final_text = ''.join(tags) + translated if tags else translated
                new_line = ','.join(parts[:9]) + ',' + final_text + "\n"
                output_lines.append(new_line)
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)

    with open(output_ass_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    print(f"Przetłumaczony plik zapisany jako: {output_ass_path}")

# Funkcja do wyświetlania okna dialogowego i uruchomienia aplikacji
def run_gui():
    root = tk.Tk()
    root.withdraw()  # Ukrycie głównego okna, bo nie chcemy go wyświetlać

    # Okno wyboru pliku .ass
    input_ass_file = filedialog.askopenfilename(title="Wybierz plik .ass", filetypes=[("Pliki ASS", "*.ass")])
    if not input_ass_file:
        messagebox.showerror("Błąd", "Nie wybrano pliku .ass.")
        return

    # Okno wyboru pliku .txt
    gender_txt_file = filedialog.askopenfilename(title="Wybierz plik z danymi o płci", filetypes=[("Pliki TXT", "*.txt")])
    if not gender_txt_file:
        messagebox.showerror("Błąd", "Nie wybrano pliku z danymi o płci.")
        return

    # Wczytanie interwałów płci z pliku
    gender_intervals = load_gender_intervals(gender_txt_file)
    if not gender_intervals:
        messagebox.showerror("Błąd", "Plik z danymi o płci jest pusty lub niepoprawny.")
        return

    # Okno wyboru ścieżki dla pliku wynikowego
    output_ass_file = filedialog.asksaveasfilename(defaultextension=".ass", filetypes=[("Pliki ASS", "*.ass")])
    if not output_ass_file:
        messagebox.showerror("Błąd", "Nie wybrano pliku wynikowego.")
        return

    # Procesowanie pliku .ass
    process_ass_file(input_ass_file, output_ass_file, gender_intervals)
    messagebox.showinfo("Sukces", "Plik został przetworzony i zapisany.")

# Uruchomienie aplikacji GUI
run_gui()
