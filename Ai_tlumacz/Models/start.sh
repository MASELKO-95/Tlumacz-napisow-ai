#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/Ai_tlumacz/Models"
VENV_DIR="$SCRIPT_DIR/.venv"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   🌍  AI Tłumacz Napisów ASS  v3.0       ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# --- Sprawdź Python ---
if ! command -v python3 &>/dev/null; then
    echo "❌ Nie znaleziono Python3!"
    echo "   Zainstaluj go: sudo apt install python3 python3-pip python3-venv"
    read -p "Naciśnij Enter, aby wyjść..."
    exit 1
fi

echo "✔ Python3: $(python3 --version)"

# --- Utwórz wirtualne środowisko (jeśli nie istnieje) ---
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "🔧 Tworzenie wirtualnego środowiska Python w .venv ..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Nie udało się utworzyć venv!"
        echo "   Zainstaluj: sudo apt install python3-venv"
        read -p "Naciśnij Enter, aby wyjść..."
        exit 1
    fi
    echo "✔ Środowisko wirtualne utworzone: $VENV_DIR"
    FRESH_VENV=1
else
    echo "✔ Środowisko wirtualne: .venv (istnieje)"
    FRESH_VENV=0
fi

# --- Aktywuj venv ---
source "$VENV_DIR/bin/activate"
echo "✔ venv aktywowane: $(which python3)"

# --- Zainstaluj zależności (jeśli nowy venv lub brak modułów) ---
if [ "$FRESH_VENV" -eq 1 ] || ! python3 -c "import requests" 2>/dev/null; then
    echo ""
    echo "🔄 Instalowanie zależności Python..."
    pip3 install --upgrade pip -q
    pip3 install -q -r "$APP_DIR/requirements.txt"
    echo "✔ Wszystkie zależności zainstalowane w .venv"
else
    echo "✔ Zależności OK (w .venv)"
fi

# --- Sprawdź/uruchom Ollamę ---
echo ""
if ! command -v ollama &>/dev/null; then
    echo "⚠  Ollama nie jest zainstalowana!"
    echo "   Pobierz ze strony: https://ollama.com"
    echo ""
    read -p "Kontynuować mimo to? (t/N): " ans
    [[ "$ans" =~ ^[tTyY]$ ]] || exit 0
else
    echo "✔ Ollama: $(ollama --version 2>/dev/null || echo 'zainstalowana')"
    # Sprawdź czy ollama serve działa
    if ! curl -s http://localhost:11434 &>/dev/null; then
        echo "🔄 Uruchamianie serwera Ollama..."
        ollama serve &>/dev/null &
        OLLAMA_PID=$!
        sleep 3
        echo "✔ Ollama uruchomiona (PID: $OLLAMA_PID)"
    else
        echo "✔ Ollama już działa"
    fi

    # Sprawdź dostępność modeli tłumaczeniowych
    echo ""
    echo "── Modele translategemma ──────────────────────"
    for MODEL in "translategemma:27b" "translategemma:12b"; do
        if ollama list 2>/dev/null | grep -q "$MODEL"; then
            echo "✔ $MODEL — dostępny"
        else
            echo "✖ $MODEL — NIE pobrany"
            read -p "   Pobrać $MODEL teraz? (może zająć kilka minut) (t/N): " pull_ans
            if [[ "$pull_ans" =~ ^[tTyY]$ ]]; then
                echo "🔄 Pobieranie $MODEL..."
                ollama pull "$MODEL"
                echo "✔ $MODEL pobrany."
            fi
        fi
    done
    echo "───────────────────────────────────────────────"
fi

# --- Uruchom aplikację ---
echo ""
echo "🚀 Uruchamianie AI Tłumacza..."
echo ""
cd "$APP_DIR"
python3 main_translator.py

# Jeśli uruchomiliśmy Ollamę sami, zatrzymaj ją po zamknięciu apki
if [ -n "$OLLAMA_PID" ]; then
    echo ""
    echo "🛑 Zatrzymywanie serwera Ollama..."
    kill "$OLLAMA_PID" 2>/dev/null
fi

# Deaktywacja venv
deactivate 2>/dev/null

echo ""
echo "Do widzenia! 👋"
