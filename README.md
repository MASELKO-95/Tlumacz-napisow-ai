# Tłumacz napisów AI

## Opis
Tłumacz napisów AI to projekt oparty na sztucznej inteligencji, który tłumaczy dialogi z plików `.ass` (napisy w formacie Advanced SubStation Alpha). Model rozpoznaje płeć mówcy na podstawie głosu i tłumaczy zaimki na język polski.

**Aktualna wersja** tłumaczy tylko pliki `.ass` i obsługuje automatyczne tłumaczenie zaimków na podstawie płci.

## Wymagania

Aby uruchomić projekt, musisz zainstalować wymagane biblioteki.

### Wymagana wersja Pythona:
- Python 3.11

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
#Uruchomienie
Z grubsza struktura plików wygląda tak 
```Struktura Plików
.
├── input
│   ├── Example.wav
│   ├── Exaple.ass
│   └── Exaple.mp4
├── Models
│   ├── check_dependencies.py
│   ├── czytajto.txt
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
Tyle co do kwesti terminala 
