# Tłumacz napisów AI

![GitHub all releases](https://img.shields.io/github/downloads/MASELKO-95/Tlumacz-napisow-ai/total?style=flat&color=blue)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=MASELKO-95.Tlumacz-napisow-ai)


## 📥 Pobierz AI Tłumacz napisów

Kliknij, aby pobrać najnowszą wersję:  
🔗 **[Pobierz tutaj](https://github.com/MASELKO-95/Tlumacz-napisow-ai/releases/)**  

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
**Gui po aktualizacji do wersji 1.0.1a**

![image](https://github.com/user-attachments/assets/420d6361-025b-4641-98d7-1179a9edbc29)

- **Wyodrębnianie audio z filmu `.mp4`**
- 
  ![image](https://github.com/user-attachments/assets/c03c6a58-41eb-4ce2-a743-c53c1088ab7c)

- **Rozpoznawanie zaimków z pliku audio `.wav`**
- 
  ![image](https://github.com/user-attachments/assets/8d3c5820-c8d7-4886-ad7e-a50a311c881b)

- **Główna funkcja programu - tłumaczenie plików `.ass`**
- 
  ![image](https://github.com/user-attachments/assets/1f947924-f36f-40ef-9553-820b2df7abdf)

- **Eksperymentalna funkcja rozpoznawania mówcy i podmiany zaimków w pliku `.ass`**
- 
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
```

Każda osoba może dodać własne wyrażenia, aby poprawić tłumaczenie.

---
## Edycja Wyjątków aby ulepszyć tłumacznie (Mods)
```
Przetwarzanie poszczególnych sekcji w słowniku:
Sekcja [replace]:
    • Dla każdej linii w tej sekcji, kod rozdziela tekst przed i po dwukropku (:), a następnie dodaje tę parę do listy reguł zastąpienia.
    • Przykład: "Time to dig in!" : "Smacznego" dodaje do mod_rules["replace"] krotkę ('Time to dig in!', 'Smacznego').
Sekcja [Ignore]:
    • Każda linia w tej sekcji jest traktowana jako tekst do usunięcia z tłumaczenia.
    • Przykład: "mao ze dong" dodaje do mod_rules["ignore"] element 'mao ze dong'.
Sekcja [delete]:
    • Każda linia w tej sekcji jest traktowana jako wyraz, który należy usunąć z tłumaczenia.
    • Przykład: "chan", "taiwan" dodaje do mod_rules["delete"] dwa elementy: 'chan' i 'taiwan'.
Ostateczny efekt:
Po załadowaniu pliku słownika z przykładem:
[replace]
" Time to dig in!":"Smacznego",
[Ignore]
"mao ze dong"
[delete]
"chan","taiwan"
Struktura mod_rules będzie wyglądać tak:
mod_rules = {
    "replace": [('Time to dig in!', 'Smacznego')],
    "ignore": ['mao ze dong'],
    "delete": ['chan', 'taiwan']
}

Przykład działania:
Załóżmy, że mamy dialog:
"Time to dig in! Let's go to Taiwan with mao ze dong."
Po tłumaczeniu i zastosowaniu reguł:
    1. "Time to dig in!" zostanie zastąpione przez "Smacznego".
    2. "mao ze dong" zostanie usunięte.
    3. "Taiwan" zostanie usunięte.
Ostateczny wynik:
"Smacznego Let's go to  with ."
Podsumowanie:
Tak, kod prawidłowo odczytuje plik słownika i wykonuje odpowiednie operacje na tłumaczeniu, takie jak zastępowanie, ignorowanie i usuwanie tekstu, zgodnie z definicjami w pliku .txt.
```

## Podsumowanie
Projekt **Tłumacz napisów AI** to narzędzie wykorzystujące AI do inteligentnego tłumaczenia napisów w formacie `.ass`. Zachęcam do testowania, zgłaszania błędów oraz dzielenia się swoimi usprawnieniami!

