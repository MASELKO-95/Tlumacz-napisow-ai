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

```bash
pip install -r requirements.txt
Uruchomienie modelu
Uruchom terminal i przejdź do folderu, w którym znajduje się projekt:

bash
Kopiuj
Edytuj
cd ai_tlumacz/Models
Uruchom model za pomocą poniższej komendy:

bash
Kopiuj
Edytuj
python main_guy.py
Struktura projektu
graphql
Kopiuj
Edytuj
Ai_tlumacz/
│
├── Html/             # Interfejs web
├── input/            # Pliki wejściowe
├── Models/           # Moduły i skrypty AI
│   ├── check_dependencies.py
│   ├── rozpoznanie_zaimnkow.py
│   └── main_guy.py
├── output/           # Pliki wyjściowe
└── tempsf/           # Tymczasowe pliki
