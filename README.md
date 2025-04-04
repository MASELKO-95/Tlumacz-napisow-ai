# Tłumacz napisów AI

## Opis
Tłumacz napisów AI oparty o model `facebook/nllb-200-1.3B` to projekt oparty na sztucznej inteligencji, który tłumaczy dialogi z plików `.ass` (napisy w formacie Advanced SubStation Alpha). Model rozpoznaje płeć mówcy na podstawie głosu i tłumaczy zaimki na język polski.

**Aktualna wersja** tłumaczy tylko pliki `.ass`.

## Wymagania

Aby uruchomić projekt, musisz zainstalować wymagane biblioteki.

### Wymagana wersja Pythona:
`- Python 3.11`
Jak sprawdzić aktulaną wersje 
```Terminal
python --version
```

### Instalacja bibliotek:

1. Upewnij się, że masz zainstalowanego Pythona w wersji 3.11.
2. Zainstaluj wymagane biblioteki, wykonując następującą komendę:


```Termnial windows 🪟
CD Dysk:folder_w_ktorym_zostalo_zapisne/Ai_tlumacz/models
```

Dla linuxa
```Termnial linux 
cd /home/nazwa_urzytkownika/folder_w_ktorym_zostalo_zapisne/Ai_tlumacz/models
```

Natepnie nalezy w termninalu wpisać 
```Termnial
pip install -r requirements.txt
```


### Uruchomienie
Z grubsza struktura plików wygląda tak 
```Struktura Plików
.
├── input
│   ├── Example.wav
│   ├── Exaple.ass
│   └── Exaple.mp4
├── Models
│   ├── check_dependencies.py
│   ├── glowny_tlumacz.py
│   ├── is_correct_ass.py
│   ├── main_gui.py
│   ├── __pycache__
│   │   └── rozpoznanie_zaimnkow.cpython-311.pyc
│   ├── requirements.txt
│   ├── rozpoznanie_zaimnkow.py
│   └── wyodrebnienie_dzwieku.py
├── output
│   └── Exaple_voice_log.txt
└── tempsf


```
Uruchomienie
```Termnial
python main_gui.py
```


### Użytkownie 
**Uwagi**
Aby program poprawnie tłumaczył napisy zlecane jest przesyłanie plików do folderu `Ai_tlumacz/input`
**Wygląd i Funkcionalność**
`wyglad moze sie róznić ozaleznie od systemu operacyjnego`
**Linux:**
Wyodrebnianie audio z filmu `.mp4`
![image](https://github.com/user-attachments/assets/c03c6a58-41eb-4ce2-a743-c53c1088ab7c)

Funkacja rozpoznwania zaimków z pliku audio `.wav `

![image](https://github.com/user-attachments/assets/8d3c5820-c8d7-4886-ad7e-a50a311c881b)\

Główna funkacja programu czyli tłumacznie plików `.ass`
![image](https://github.com/user-attachments/assets/1f947924-f36f-40ef-9553-820b2df7abdf)

Funkcja torche Eksperymentalna , bedzie aktualizowna , rozpoznaje oraz podmienia jeśli wykryje mówica kobiete z logów zaimków `.txt` i podmienia w piliku `.ass`
![image](https://github.com/user-attachments/assets/b4bf9c7e-b88f-43a9-b578-e5cce13983b0)






