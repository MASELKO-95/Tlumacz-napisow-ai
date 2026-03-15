# 🌍 AI Tłumacz Napisów ASS (v2.0)

![GitHub all releases](https://img.shields.io/github/downloads/MASELKO-95/Tlumacz-napisow-ai/total?style=flat&color=blue)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=MASELKO-95.Tlumacz-napisow-ai)

Narzędzie hobbystyczne do automatyzacji tłumaczeń napisów z filmów (format `.ass`) przy wykorzystaniu sztucznej inteligencji. Aplikacja nie tylko tłumaczy, ale **najpierw analizuje cały kontekst dialogów**, co zapobiega błędom wynikającym z braku znajomości fabuły. 

Dodatkowo w cenie otrzymujesz wbudowane narzędzia do wyodrębniania audio z mkv/mp4, detekcji płci na podstawie głosu i automatycznej korekty zaimków (np. w języku polskim)!

---

## ✨ Co nowego w wariancie v 2.0?

- **Multi-Provider AI:** Aplikacja nie jest już ograniczona tylko do lokalnej Ollamy. Od teraz obsługuje:
  - 🦙 **Ollama** (Lokalnie, np. `translategemma:27b`, darmowe i prywatne)
  - 🤖 **OpenAI** (Wspiera GPT-4, GPT-4o)
  - 🐋 **DeepSeek** (Bardzo szybki i tani DeepSeek-V3 oraz Reasoner)
  - 🌌 **Google Gemini**
  - 🖥️ **LM Studio** i **Custom API** (np. dla własnych serwerów OpenAI-Compatible).
- **Całościowa Analiza Kontekstu:** Model przed przetłumaczeniem dzieli tysiące linii dialogowych na porcje (po ~150 linii), czyta cały scenariusz i wyciąga notatki (imiona, relacje, płeć postaci). Kontekst ten służy później do idealnego wycelowania tłumaczenia zdanie po zdaniu.
- **Smart UI:** Przeprojektowany, ładny i ciemny interfejs. Automatycznie ukrywa niepotrzebne pola (np. Klucz API) gdy używasz lokalnych modeli.
- **Wbudowane narzędzia:** Zamiast uruchamiać skrypty ręcznie, sekcja "Narzędzia" w oknie głównym pozwala:
  1. Wyciągnąć audio z pliku MP4.
  2. Rozpoznać płeć postaci z dźwięku.
  3. Skorygować zaimki w wygenerowanych plikach `.ass`.

---

## 📥 Pobieranie Aplikacji

Aplikacja docelowo dystrybuowana jest jako samodzielny, gotowy program do kliknięcia na różnego rodzaju platformach (Windows installer / linux binary). Nie ma już potrzeby kompilowania całości z konsoli! Odwiedź zakładkę **Releases** na GitHubie, pobierz wersję wykonywalną dla swojego systemu operacyjnego i po prostu ją uruchom.

---

## 🎮 Użytkowanie (Główne okno)

1. **Wybierz dostawcę AI:** w sekcji "Dostawca AI" wybierz Ollama (jeśli masz silny komputer i chcesz robić to lokalnie i za darmo) lub chmurowego dostawcę (np. OpenAI / DeepSeek - *wymaga wklejenia klucza API z ich platformy*).
2. **Załaduj plik .ass:** W sekcji "Plik wejściowy" wskaż ścieżkę do pobranych napisów.
3. **Plik wyjściowy:** Program sam dopisze `_pl.ass`, ale możesz to zmienić.
4. (Opcjonalnie) Wybierz lub utwórz plik "MOD (*.txt*)", czyli słownik z własnymi podmianami (np. jeśli chcesz żeby imię "John" zamieniało na "Jan").
5. Kliknij **▶ Rozpocznij tłumaczenie**.

### Faza 1: Kontekst
Najpierw AI przeanalizuje twój plik by poznać fabułę, a po minucie wyskoczy dodatkowe, edytowalne okno z notatkami, z którymi zapoznało się AI. Możesz tam dopisać własne uwagi (np. *"Postać X rozmawia z Postacią Y oficjalnie"*). Zapisz.

### Faza 2: Tłumaczenie
AI po linijce będzie przetwarzało cały skrypt napisów z doskonałym zachowaniem czasów (`Timing`) z oryginalnego pliku `.ass` — u dołu ekranu masz dokładnego loga na bieżąco pokazującego zamieniane teksty. Do przerwanej w każdej chwili translacji można załączyć **"⏹ Anuluj"**.

---

## 🛠️ Moduły poboczne (Wbudowane w GUI) 

Na samym dole aplikacji znajdziesz wczesne moduły eksperymentalne znane z wersji V1. Były one pisane pod starsze modele, miewające duże problemy z orientacją w płci mówcy:

1. **Wyodrębnij audio:** Tworzy plik `.wav` ze zwykłego filmu `.mp4` by móc go przeanalizować.
2. **Rozpoznanie Płci:** Analizuje ton wibracji dźwięku mowy, zapisuje log z sygnaturami czasowymi kto mówił i jakiej jest płci.
3. **Korekta zaimków:** Ładuje log, uderza do twojego nowo wygenerowanego zepsutego pliku tłumaczeń `.ass` i sztywnym skryptem wymienia błędne koncówki słów na poprawne w wyznaczonych czasówkach audio.

---

## 👨‍💻 Edycja i Forkowanie
Narzędzie stworzone hobbystycznie jako aplikacja "dla amatorów". Zachęcam do rozwijania kodu na własną rękę, testowania, zgłaszania Issues oraz wystawiania Pull Requestów!

> Skrypt słownika MOD oraz podmieniania w locie (`Ai_tlumacz/Models/validate_ass.py` oraz `is_correct_ass.py`) nie wymaga znajomości AI, to zwykłe mapowanie Python Dictionary — jeśli brakuje ci uodpornień zaimków na słownik — dorzuć je śmiało i pomóż reszcie społeczności uniknąć genderowych wpadek.
