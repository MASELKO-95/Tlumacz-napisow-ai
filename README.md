# Tłumacz napisów AI

## Opis
Tłumacz napisów AI oparty o model `facebook/nllb-200-1.3B` to projekt wykorzystujący sztuczną inteligencję do tłumaczenia dialogów z plików `.ass` (napisy w formacie Advanced SubStation Alpha). Model rozpoznaje płeć mówcy na podstawie głosu i poprawnie tłumaczy zaimki na język polski.

**Aktualna wersja** obsługuje tylko pliki `.ass`.

---

## Wymagania

### Wersja Pythona
- **Python 3.11**

Aby sprawdzić aktualną wersję Pythona, uruchom w terminalu:
```sh
python --version
```

### Instalacja bibliotek

1. Upewnij się, że masz zainstalowanego Pythona w wersji 3.11.
2. Przejdź do katalogu `Models` w folderze projektu:

#### Windows:
```sh
cd Dysk:\folder_w_ktorym_zostalo_zapisane\Ai_tlumacz\Models
```

#### Linux:
```sh
cd /home/nazwa_uzytkownika/folder_w_ktorym_zostalo_zapisane/Ai_tlumacz/Models
```

3. Zainstaluj wymagane biblioteki:
```sh
pip install -r requirements.txt
```

---

## Uruchomienie

Struktura plików projektu:
```
.
├── input
│   ├── Example.wav
│   ├── Example.ass
│   ├── Example.mp4
├── Models
│   ├── check_dependencies.py
│   ├── glowny_tlumacz.py
│   ├── is_correct_ass.py
│   ├── main_gui.py
│   ├── requirements.txt
│   ├── rozpoznanie_zaimnkow.py
│   └── wyodrebnienie_dzwieku.py
├── output
│   └── Example_voice_log.txt
└── tempsf
```

Aby uruchomić program, wpisz w terminalu:
```sh
python main_gui.py
```

---

## Użytkowanie

### Uwagi
Aby program poprawnie tłumaczył napisy, zalecane jest przesyłanie plików do folderu `Ai_tlumacz/input`.

### Wygląd i funkcjonalność
Wygląd może się różnić w zależności od systemu operacyjnego.

#### Linux:
- **Wyodrębnianie audio z filmu `.mp4`**
  ![image](https://github.com/user-attachments/assets/c03c6a58-41eb-4ce2-a743-c53c1088ab7c)

- **Rozpoznawanie zaimków z pliku audio `.wav`**
  ![image](https://github.com/user-attachments/assets/8d3c5820-c8d7-4886-ad7e-a50a311c881b)

- **Główna funkcja programu - tłumaczenie plików `.ass`**
  ![image](https://github.com/user-attachments/assets/1f947924-f36f-40ef-9553-820b2df7abdf)

- **Eksperymentalna funkcja rozpoznawania mówcy i podmiany zaimków w pliku `.ass`**
  ![image](https://github.com/user-attachments/assets/b4bf9c7e-b88f-43a9-b578-e5cce13983b0)

**Program wyświetla podgląd procesu tłumaczenia w terminalu:**
![image](https://github.com/user-attachments/assets/4c743e06-a61d-4648-8768-cccf43ca4584)

---

## Edycja kodu pod własne potrzeby
Ten projekt udostępniam za darmo. Możesz go używać, modyfikować oraz udostępniać innym. Będzie mi miło, jeśli dodasz link do oryginalnego repozytorium.

### Edycja słownika zaimków
Zachęcam do edycji pliku `is_correct_ass.py` i dzielenia się swoimi zmianami w celu ulepszenia projektu. Oto przykładowy fragment słownika:

```python
# Funkcja do zamiany zaimków męskich na żeńskie
def adjust_pronouns(text):
    masc_to_fem = {
        "ja kupiłem": "ja kupiłam", "ja byłem": "ja byłam", "ja zrobiłem": "ja zrobiłam", 
        "ty kupiłeś": "ty kupiłaś", "ty byłeś": "ty byłaś", "ty zrobiłeś": "ty zrobiłaś", 
        "on kupił": "ona kupiła", "on był": "ona była", "on zrobił": "ona zrobiła", 
        "my kupiliśmy": "my kupiłyśmy", "my byliśmy": "my byłyśmy", "my zrobiliśmy": "my zrobiłyśmy"
    }
    for masc, fem in masc_to_fem.items():
        text = text.replace(masc, fem)
    return text
```

Każda osoba może dodać własne wyrażenia, aby poprawić tłumaczenie.

---

## Podsumowanie
Projekt **Tłumacz napisów AI** to narzędzie wykorzystujące AI do inteligentnego tłumaczenia napisów w formacie `.ass`. Zachęcam do testowania, zgłaszania błędów oraz dzielenia się swoimi usprawnieniami!

