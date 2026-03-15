#!/usr/bin/env python3
"""
Tłumacz Napisów ASS — uniwersalny (Ollama, OpenAI, DeepSeek, Gemini, LM Studio)
Wersja 3.1 - multi-provider, pełna analiza kontekstu, zintegrowane narzędzia
"""

import os
import re
import sys
import time
import math
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import requests

# Moduły projektu
from ai_provider import AIProvider, get_provider_names, get_provider_config, PROVIDERS

try:
    from check_update import check_for_updates, open_releases_page, CURRENT_VERSION
except ImportError:
    CURRENT_VERSION = "2.0.0"
    def check_for_updates(): return {"available": False, "current": CURRENT_VERSION, "error": "Brak modułu check_update"}
    def open_releases_page(): pass

try:
    from audio_extraction import extract_audio_from_video
except ImportError:
    extract_audio_from_video = None

try:
    from pronoun_recognition import RozpoznanieZaimnkow
except ImportError:
    RozpoznanieZaimnkow = None

try:
    from validate_ass import process_ass_file as validate_ass_pronouns, load_gender_intervals
except ImportError:
    validate_ass_pronouns = None
    load_gender_intervals = None

# === KONFIGURACJA DOMYŚLNA ===
DEFAULT_MODEL = "translategemma:27b"
DEFAULT_SOURCE_LANG = "en"
DEFAULT_TARGET_LANG = "pl"
DEFAULT_PROVIDER = "Ollama (lokalny)"

# === KOLORY (ciemny motyw) ===
C_BG       = "#0f0f1a"      # tło główne
C_PANEL    = "#1a1a2e"      # panele / ramki
C_CARD     = "#16213e"      # karty
C_ACCENT   = "#e94560"      # akcent czerwony
C_ACCENT2  = "#0f3460"      # akcent niebieski
C_TEXT     = "#eaeaea"      # tekst główny
C_MUTED    = "#888aaa"      # tekst drugorzędny
C_SUCCESS  = "#4ecca3"      # zielony sukces
C_WARNING  = "#f5a623"      # pomarańczowy
C_ERROR    = "#e94560"      # czerwony błąd
C_BTN      = "#e94560"      # przycisk główny
C_BTN_HOV  = "#c73652"      # przycisk hover
C_ENTRY    = "#0d1117"      # tła pól input
C_BORDER   = "#2a2a4a"      # obramowania

DEFAULT_PROMPT = """\
Jesteś profesjonalnym tłumaczem napisów filmowych.

KONTEKST:
{context}

Przetłumacz poniższy tekst z {source_lang} na {target_lang}.
ZASADY:
- Zwróć TYLKO przetłumaczony tekst, bez żadnych komentarzy ani przedrostków.
- Zachowaj naturalność dialogu i styl postaci.
- Użyj poprawnej gramatyki polskiej (w tym odmianę przez płeć jeśli znana z kontekstu).

Tekst: {text}

Tłumaczenie:"""

CONTEXT_PROMPT = """\
Przeanalizuj poniższe dialogi z pliku z napisami filmowymi (format ASS).
Twoim zadaniem jest rozpoznanie:
1. Lista postaci - imię lub opis postaci, ich płeć (mężczyzna/kobieta/nieznana), ton wypowiedzi
2. Ogólny kontekst fabularny (gatunek, klimat, relacje między postaciami)
3. Wskazówki do tłumaczenia (specyficzny styl, zwroty charakterystyczne)

Dialogi:
{dialogues}

Napisz zwięzłe notatki w języku polskim (max 300 słów)."""


class HoverButton(tk.Button):
    """Przycisk z efektem hover."""
    def __init__(self, master, bg_normal, bg_hover, **kwargs):
        self.bg_normal = bg_normal
        self.bg_hover = bg_hover
        super().__init__(master, bg=bg_normal, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _e):
        self.config(bg=self.bg_hover)

    def _on_leave(self, _e):
        self.config(bg=self.bg_normal)


class OllamaASSTranslator:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"🌍 AI Tłumacz Napisów v{CURRENT_VERSION}")
        self.root.geometry("1000x900")
        self.root.minsize(900, 750)
        self.root.configure(bg=C_BG)

        self.is_translating = False
        self.cancel_flag = False
        self.context_notes = ""
        self.provider = AIProvider(DEFAULT_PROVIDER)

        self._set_icon()
        self._apply_theme()
        self._build_ui()
        self._check_ollama_async()

    def _set_icon(self):
        """Ustawia ikonę okna aplikacji."""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
                self._app_icon = icon  # zapobiegaj garbage collection
        except Exception:
            pass  # ikona opcjonalna

    # =========================================================
    # MOTYW / STYLE
    # =========================================================
    def _apply_theme(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(".",
                        background=C_BG, foreground=C_TEXT,
                        fieldbackground=C_ENTRY, bordercolor=C_BORDER,
                        troughcolor=C_PANEL, selectbackground=C_ACCENT2,
                        selectforeground=C_TEXT, font=("Segoe UI", 10))

        style.configure("TFrame", background=C_BG)
        style.configure("Card.TFrame", background=C_PANEL, relief="flat")

        style.configure("TLabel", background=C_BG, foreground=C_TEXT)
        style.configure("Muted.TLabel", background=C_PANEL, foreground=C_MUTED)
        style.configure("Header.TLabel", background=C_BG, foreground=C_TEXT,
                        font=("Segoe UI", 11, "bold"))
        style.configure("Title.TLabel", background=C_BG, foreground=C_ACCENT,
                        font=("Segoe UI", 14, "bold"))

        style.configure("TLabelframe",
                        background=C_PANEL, foreground=C_ACCENT,
                        bordercolor=C_BORDER, relief="solid",
                        labelmargins=(8, 4, 8, 4))
        style.configure("TLabelframe.Label",
                        background=C_PANEL, foreground=C_ACCENT,
                        font=("Segoe UI", 10, "bold"))

        style.configure("TEntry",
                        fieldbackground=C_ENTRY, foreground=C_TEXT,
                        insertcolor=C_TEXT, bordercolor=C_BORDER,
                        padding=5)

        style.configure("TCombobox",
                        fieldbackground=C_ENTRY, foreground=C_TEXT,
                        background=C_PANEL, selectbackground=C_ACCENT2,
                        arrowcolor=C_ACCENT, bordercolor=C_BORDER)
        style.map("TCombobox",
                  fieldbackground=[("readonly", C_ENTRY)],
                  foreground=[("readonly", C_TEXT)])

        style.configure("TButton",
                        background=C_ACCENT2, foreground=C_TEXT,
                        bordercolor=C_BORDER, padding=(10, 6),
                        font=("Segoe UI", 9))
        style.map("TButton",
                  background=[("active", C_ACCENT), ("pressed", C_ACCENT)])

        style.configure("Accent.TButton",
                        background=C_ACCENT, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=(14, 8))
        style.map("Accent.TButton",
                  background=[("active", C_BTN_HOV), ("pressed", C_BTN_HOV),
                               ("disabled", "#555")])

        style.configure("Small.TButton",
                        background=C_CARD, foreground=C_TEXT,
                        padding=(6, 4), font=("Segoe UI", 9))
        style.map("Small.TButton",
                  background=[("active", C_ACCENT2)])

        style.configure("TCheckbutton",
                        background=C_PANEL, foreground=C_TEXT)
        style.map("TCheckbutton",
                  background=[("active", C_PANEL)])

        style.configure("Horizontal.TProgressbar",
                        troughcolor=C_CARD, background=C_ACCENT,
                        bordercolor=C_BORDER, thickness=8)

        style.configure("TSeparator", background=C_BORDER)

    # =========================================================
    # BUDOWANIE UI
    # =========================================================
    def _build_ui(self):
        # --- Pasek tytułowy ---
        title_bar = tk.Frame(self.root, bg=C_PANEL, height=56)
        title_bar.pack(fill=tk.X, side=tk.TOP)
        tk.Label(title_bar, text="🌍  AI Tłumacz Napisów", bg=C_PANEL,
                 fg=C_ACCENT, font=("Segoe UI", 15, "bold")).pack(side=tk.LEFT, padx=18, pady=12)
        self.status_dot = tk.Label(title_bar, text="⬤", bg=C_PANEL, fg=C_WARNING,
                                   font=("Segoe UI", 10))
        self.status_dot.pack(side=tk.RIGHT, padx=6)
        self.status_lbl = tk.Label(title_bar, text="Sprawdzam Ollamę...", bg=C_PANEL,
                                   fg=C_MUTED, font=("Segoe UI", 9))
        self.status_lbl.pack(side=tk.RIGHT, padx=4, pady=12)

        # --- Scrollowalny canvas ---
        outer = tk.Frame(self.root, bg=C_BG)
        outer.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(outer, bg=C_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_frame = ttk.Frame(canvas, style="TFrame")
        canvas_window = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        self.scroll_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        # --- Zawartość ---
        content = self.scroll_frame
        PAD = {"padx": 14, "pady": 6}

        self._build_files_section(content, PAD)
        self._build_model_section(content, PAD)
        self._build_prompt_section(content, PAD)
        self._build_options_section(content, PAD)
        self._build_tools_section(content, PAD)
        self._build_log_section(content, PAD)
        self._build_buttons_section(content)

    def _card(self, parent, title, **kwargs):
        frame = ttk.LabelFrame(parent, text=title, style="TLabelframe", **kwargs)
        frame.pack(fill=tk.X, padx=14, pady=5)
        return frame

    def _row(self, parent, label_text, row):
        ttk.Label(parent, text=label_text, style="Muted.TLabel").grid(
            row=row, column=0, sticky=tk.W, padx=(10, 6), pady=6)

    def _build_files_section(self, parent, PAD):
        card = self._card(parent, "📂  Pliki")
        card.columnconfigure(1, weight=1)

        for r, (lbl, attr, title, ftype) in enumerate([
            ("Plik wejściowy (.ass):", "input_entry",
             "Wybierz plik ASS", [("Pliki ASS", "*.ass"), ("Wszystkie", "*.*")]),
            ("Plik wyjściowy (.ass):", "output_entry",
             "Zapisz jako", [("Pliki ASS", "*.ass"), ("Wszystkie", "*.*")]),
            ("Słownik MOD (.txt):", "mod_entry",
             "Wybierz słownik MOD", [("Pliki tekstowe", "*.txt"), ("Wszystkie", "*.*")]),
        ]):
            ttk.Label(card, text=lbl, style="Muted.TLabel").grid(
                row=r, column=0, sticky=tk.W, padx=(10, 6), pady=6)
            entry = ttk.Entry(card)
            entry.grid(row=r, column=1, padx=5, pady=5, sticky=tk.EW)
            setattr(self, attr, entry)

            is_save = (r == 1)
            cmd = (lambda a=attr, t=title, f=ftype: self._save_file_dialog(a, t, f)
                   if is_save else self._open_file_dialog(a, t, f))
            # Re-bind correctly
            btn_text = "Zapisz jako..." if is_save else "Wybierz..."
            ttk.Button(card, text=btn_text, style="Small.TButton",
                       command=cmd).grid(row=r, column=2, padx=(5, 10), pady=5)

        # Fix lambda binding issue
        self.input_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.mod_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        # Re-bind buttons properly
        for widget in card.winfo_children():
            widget.destroy()

        entries_cfg = [
            ("Plik wejściowy (.ass):", "input_entry", False,
             "Wybierz plik ASS", [("Pliki ASS", "*.ass"), ("Wszystkie", "*.*")]),
            ("Plik wyjściowy (.ass):", "output_entry", True,
             "Zapisz przetłumaczony plik", [("Pliki ASS", "*.ass"), ("Wszystkie", "*.*")]),
            ("Słownik MOD (.txt):", "mod_entry", False,
             "Wybierz słownik MOD", [("Pliki tekstowe", "*.txt"), ("Wszystkie", "*.*")]),
        ]
        for r, (lbl, attr, is_save, title, ftype) in enumerate(entries_cfg):
            ttk.Label(card, text=lbl, style="Muted.TLabel").grid(
                row=r, column=0, sticky=tk.W, padx=(10, 6), pady=6)
            entry = ttk.Entry(card)
            entry.grid(row=r, column=1, padx=5, pady=6, sticky=tk.EW)
            setattr(self, attr, entry)

            if is_save:
                cmd = lambda a=attr, t=title, f=ftype: self._save_file_dialog(a, t, f)
                btn_text = "Zapisz jako..."
            else:
                cmd = lambda a=attr, t=title, f=ftype: self._open_file_dialog(a, t, f)
                btn_text = "Wybierz..."
            ttk.Button(card, text=btn_text, style="Small.TButton",
                       command=cmd).grid(row=r, column=2, padx=(5, 10), pady=5)

        card.columnconfigure(1, weight=1)

    def _build_model_section(self, parent, PAD):
        card = self._card(parent, "🤖  Dostawca AI / Model / Języki")
        card.columnconfigure(1, weight=1)

        # --- Dostawca AI ---
        ttk.Label(card, text="Dostawca AI:", style="Muted.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(10, 6), pady=6)
        self.provider_combo = ttk.Combobox(card, values=get_provider_names(), state="readonly")
        self.provider_combo.set(DEFAULT_PROVIDER)
        self.provider_combo.grid(row=0, column=1, padx=5, pady=6, sticky=tk.EW)
        self.provider_combo.bind("<<ComboboxSelected>>", self._on_provider_changed)

        self.provider_desc_lbl = ttk.Label(card, text="Lokalne modele przez Ollama",
                                           style="Muted.TLabel")
        self.provider_desc_lbl.grid(row=0, column=2, sticky=tk.W, padx=(5, 10))

        # --- Klucz API ---
        self.api_key_lbl = ttk.Label(card, text="Klucz API:", style="Muted.TLabel")
        self.api_key_lbl.grid(row=1, column=0, sticky=tk.W, padx=(10, 6), pady=6)
        self.api_key_entry = ttk.Entry(card, show="•")
        self.api_key_entry.grid(row=1, column=1, padx=5, pady=6, sticky=tk.EW)
        self.api_key_show_btn = ttk.Button(card, text="👁", style="Small.TButton",
                                           command=self._toggle_api_key_visibility, width=3)
        self.api_key_show_btn.grid(row=1, column=2, padx=(5, 10), pady=5, sticky=tk.W)

        # --- Custom URL (widoczne dla Custom/Lokalnych) ---
        self.url_lbl = ttk.Label(card, text="URL serwera:", style="Muted.TLabel")
        self.url_lbl.grid(row=2, column=0, sticky=tk.W, padx=(10, 6), pady=6)
        self.custom_url_entry = ttk.Entry(card)
        self.custom_url_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=6, sticky=tk.EW)
        self.custom_url_entry.insert(0, "http://localhost:11434")

        # --- Model tłumaczenia ---
        ttk.Label(card, text="Model tłumaczenia:", style="Muted.TLabel").grid(
            row=3, column=0, sticky=tk.W, padx=(10, 6), pady=6)
        self.model_combo = ttk.Combobox(card, values=[DEFAULT_MODEL], state="readonly")
        self.model_combo.set(DEFAULT_MODEL)
        self.model_combo.grid(row=3, column=1, padx=5, pady=6, sticky=tk.EW)

        btn_frame_model = ttk.Frame(card, style="TFrame")
        btn_frame_model.grid(row=3, column=2, padx=(5, 10), pady=5)
        ttk.Button(btn_frame_model, text="🔄 Odśwież", style="Small.TButton",
                   command=self.load_available_models).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame_model, text="✔ Sprawdź", style="Small.TButton",
                   command=self.check_model).pack(side=tk.LEFT, padx=2)

        # --- Model analizy kontekstu ---
        ttk.Label(card, text="Model analizy kontekstu:", style="Muted.TLabel").grid(
            row=4, column=0, sticky=tk.W, padx=(10, 6), pady=6)
        self.context_model_combo = ttk.Combobox(card, values=[DEFAULT_MODEL], state="readonly")
        self.context_model_combo.set(DEFAULT_MODEL)
        self.context_model_combo.grid(row=4, column=1, padx=5, pady=6, sticky=tk.EW)
        ttk.Label(card, text="(lżejszy = szybsza analiza)",
                  style="Muted.TLabel").grid(row=4, column=2, sticky=tk.W, padx=(5, 10))

        # --- Języki ---
        lang_frame = ttk.Frame(card, style="TFrame")
        lang_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W, padx=10, pady=6)

        ttk.Label(lang_frame, text="Język źródłowy:", style="Muted.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.source_lang_entry = ttk.Entry(lang_frame, width=6)
        self.source_lang_entry.insert(0, DEFAULT_SOURCE_LANG)
        self.source_lang_entry.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(lang_frame, text="Język docelowy:", style="Muted.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.target_lang_entry = ttk.Entry(lang_frame, width=6)
        self.target_lang_entry.insert(0, DEFAULT_TARGET_LANG)
        self.target_lang_entry.pack(side=tk.LEFT)

        # Początkowy stan UI (ukryj API key dla Ollama)
        self._on_provider_changed(None)

    def _toggle_api_key_visibility(self):
        current = self.api_key_entry.cget("show")
        self.api_key_entry.config(show="" if current == "•" else "•")

    def _on_provider_changed(self, _event):
        """Aktualizuje UI gdy zmienia się dostawca."""
        name = self.provider_combo.get()
        cfg = get_provider_config(name)

        # Opis dostawcy
        self.provider_desc_lbl.config(text=cfg.get("description", ""))

        # Pokaż/ukryj klucz API całkowicie z UI
        needs_key = cfg.get("api_key_required", False)
        if needs_key:
            self.api_key_lbl.grid()
            self.api_key_entry.grid()
            self.api_key_show_btn.grid()
        else:
            self.api_key_entry.delete(0, tk.END)
            self.api_key_lbl.grid_remove()
            self.api_key_entry.grid_remove()
            self.api_key_show_btn.grid_remove()

        # URL — pokaż bazowy URL dostawcy
        self.custom_url_entry.delete(0, tk.END)
        self.custom_url_entry.insert(0, cfg.get("base_url", ""))
        
        # Opcjonalnie ukryj pole URL dla znanych dostawców chmurowych (np. OpenAI, Gemini) aby nie śmiecić UI
        if cfg.get("type") in ["openai", "gemini"] and name not in ["LM Studio (lokalny)", "Niestandardowy (Custom API)"]:
            self.url_lbl.grid_remove()
            self.custom_url_entry.grid_remove()
        else:
            self.url_lbl.grid()
            self.custom_url_entry.grid()

        # Ustaw domyślne modele jeśli nie-Ollama
        defaults = cfg.get("default_models", [])
        if defaults:
            self.model_combo["values"] = defaults
            self.model_combo.config(state="normal")
            self.model_combo.set(defaults[0])
            self.context_model_combo["values"] = defaults
            self.context_model_combo.set(defaults[0])
        else:
            self.model_combo["values"] = [DEFAULT_MODEL]
            self.model_combo.set(DEFAULT_MODEL)
            self.context_model_combo["values"] = [DEFAULT_MODEL]
            self.context_model_combo.set(DEFAULT_MODEL)

        # Odbuduj provider
        self._rebuild_provider()

    def _build_prompt_section(self, parent, PAD):
        card = self._card(parent, "✏️  Prompt tłumaczenia (edytowalny)")

        info = ttk.Label(card,
                         text="Użyj {text}, {source_lang}, {target_lang}, {context} jako placeholder'ów.",
                         style="Muted.TLabel", wraplength=860)
        info.pack(anchor=tk.W, padx=10, pady=(6, 2))

        self.prompt_text = scrolledtext.ScrolledText(
            card, height=7, wrap=tk.WORD, font=("Consolas", 9),
            bg=C_ENTRY, fg=C_TEXT, insertbackground=C_TEXT,
            selectbackground=C_ACCENT2, relief="flat",
            borderwidth=1, highlightthickness=1,
            highlightbackground=C_BORDER, highlightcolor=C_ACCENT)
        self.prompt_text.pack(fill=tk.X, padx=10, pady=(2, 4))
        self.prompt_text.insert("1.0", DEFAULT_PROMPT)

        ttk.Button(card, text="↺ Resetuj do domyślnego", style="Small.TButton",
                   command=self._reset_prompt).pack(anchor=tk.E, padx=10, pady=(0, 8))

    def _build_options_section(self, parent, PAD):
        card = self._card(parent, "⚙️  Opcje zaawansowane")
        opts_frame = ttk.Frame(card, style="TFrame")
        opts_frame.pack(fill=tk.X, padx=10, pady=8)

        self.debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts_frame, text="Tryb debugowania (pokaż surowe zapytania AI)",
                        variable=self.debug_var).pack(side=tk.LEFT, padx=(0, 20))

        self.strict_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts_frame, text="Tryb ścisły (wymuś czyste tłumaczenie)",
                        variable=self.strict_var).pack(side=tk.LEFT)

    def _build_log_section(self, parent, PAD):
        card = self._card(parent, "📋  Postęp tłumaczenia")

        self.log_text = scrolledtext.ScrolledText(
            card, height=13, wrap=tk.WORD, font=("Consolas", 9),
            bg="#080810", fg=C_TEXT, insertbackground=C_TEXT,
            selectbackground=C_ACCENT2, relief="flat", state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, padx=10, pady=(6, 4))

        # Kolory logów
        self.log_text.tag_configure("INFO",    foreground=C_TEXT)
        self.log_text.tag_configure("DEBUG",   foreground=C_MUTED)
        self.log_text.tag_configure("WARNING", foreground=C_WARNING)
        self.log_text.tag_configure("ERROR",   foreground=C_ERROR)
        self.log_text.tag_configure("SUCCESS", foreground=C_SUCCESS)

        self.progress = ttk.Progressbar(card, orient=tk.HORIZONTAL, mode="determinate")
        self.progress.pack(fill=tk.X, padx=10, pady=(0, 8))

    def _build_buttons_section(self, parent):
        btn_bar = tk.Frame(parent, bg=C_PANEL, height=60)
        btn_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(6, 0))

        self.start_btn = HoverButton(
            btn_bar, bg_normal=C_ACCENT, bg_hover=C_BTN_HOV,
            text="▶   Rozpocznij tłumaczenie",
            fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", cursor="hand2", padx=20, pady=10,
            command=self.start_translation)
        self.start_btn.pack(side=tk.LEFT, padx=14, pady=10)

        self.cancel_btn = HoverButton(
            btn_bar, bg_normal=C_CARD, bg_hover="#2a2a4a",
            text="⏹   Anuluj",
            fg=C_MUTED, font=("Segoe UI", 10),
            relief="flat", cursor="hand2", padx=14, pady=10,
            state=tk.DISABLED,
            command=self.cancel_translation)
        self.cancel_btn.pack(side=tk.LEFT, padx=4, pady=10)

        HoverButton(btn_bar, bg_normal=C_CARD, bg_hover="#2a2a4a",
                    text="🔄 Aktualizacje", fg=C_MUTED,
                    font=("Segoe UI", 9), relief="flat", cursor="hand2",
                    padx=10, pady=10,
                    command=self._check_updates_gui).pack(side=tk.RIGHT, padx=4, pady=10)

        HoverButton(btn_bar, bg_normal=C_CARD, bg_hover="#2a2a4a",
                    text="❓ Pomoc", fg=C_MUTED,
                    font=("Segoe UI", 9), relief="flat", cursor="hand2",
                    padx=10, pady=10,
                    command=self.show_help).pack(side=tk.RIGHT, padx=14, pady=10)

    # =========================================================
    # NARZĘDZIA (przywrócone z v1.0)
    # =========================================================
    def _build_tools_section(self, parent, PAD):
        card = self._card(parent, "🛠️  Narzędzia (z poprzednich wersji)")
        tools_frame = ttk.Frame(card, style="TFrame")
        tools_frame.pack(fill=tk.X, padx=10, pady=8)

        tools = [
            ("🎬 Wyodrębnij audio z MP4", self._tool_extract_audio,
             extract_audio_from_video is not None),
            ("🎤 Rozpoznaj płeć z audio", self._tool_pronoun_recognition,
             RozpoznanieZaimnkow is not None),
            ("♀♂ Podmień zaimki w ASS", self._tool_validate_ass,
             validate_ass_pronouns is not None),
        ]

        for i, (text, cmd, available) in enumerate(tools):
            btn = ttk.Button(tools_frame, text=text, style="Small.TButton",
                             command=cmd, state=tk.NORMAL if available else tk.DISABLED)
            btn.pack(side=tk.LEFT, padx=4, pady=4)

        if not all(t[2] for t in tools):
            ttk.Label(tools_frame,
                      text="⚠ Brak modułów: pip install pydub librosa sounddevice numpy",
                      style="Muted.TLabel").pack(side=tk.LEFT, padx=10)

    def _tool_extract_audio(self):
        """Wyodrębnia audio z pliku MP4."""
        video_path = filedialog.askopenfilename(
            title="Wybierz plik wideo",
            filetypes=[("Pliki wideo", "*.mp4 *.mkv *.avi"), ("Wszystkie", "*.*")])
        if not video_path:
            return
        base = os.path.splitext(video_path)[0]
        output_path = f"{base}.wav"
        save_path = filedialog.asksaveasfilename(
            title="Zapisz audio jako",
            initialfile=os.path.basename(output_path),
            defaultextension=".wav",
            filetypes=[("Pliki WAV", "*.wav")])
        if not save_path:
            return

        self.log(f"🎬 Wyodrębnianie audio: {os.path.basename(video_path)}...", "INFO")

        def _extract():
            try:
                extract_audio_from_video(video_path, save_path)
                self.log(f"✔ Audio zapisane: {save_path}", "SUCCESS")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Gotowe", f"Audio wyodrębnione!\n{save_path}"))
            except Exception as e:
                self.log(f"✖ Błąd ekstrakcji audio: {e}", "ERROR")
                self.root.after(0, lambda: messagebox.showerror("Błąd", str(e)))

        threading.Thread(target=_extract, daemon=True).start()

    def _tool_pronoun_recognition(self):
        """Rozpoznaje płeć z pliku audio."""
        audio_dir = filedialog.askdirectory(title="Wybierz katalog z plikami WAV")
        if not audio_dir:
            return
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "..", "output")
        temp_dir = os.path.join(script_dir, "..", "tempsf")

        self.log(f"🎤 Rozpoznawanie płci z audio w: {audio_dir}...", "INFO")

        def _recognize():
            try:
                rz = RozpoznanieZaimnkow(
                    input_dir=audio_dir, output_dir=output_dir, temp_dir=temp_dir)
                rz.start()
                log_path = os.path.join(output_dir, "voice_log.txt")
                self.log(f"✔ Rozpoznawanie zakończone. Log: {log_path}", "SUCCESS")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Gotowe", f"Rozpoznawanie płci zakończone!\nLog: {log_path}"))
            except Exception as e:
                self.log(f"✖ Błąd rozpoznawania: {e}", "ERROR")
                self.root.after(0, lambda: messagebox.showerror("Błąd", str(e)))

        threading.Thread(target=_recognize, daemon=True).start()

    def _tool_validate_ass(self):
        """Podmienia zaimki w pliku ASS na podstawie danych o płci."""
        ass_path = filedialog.askopenfilename(
            title="Wybierz plik ASS do korekty zaimków",
            filetypes=[("Pliki ASS", "*.ass"), ("Wszystkie", "*.*")])
        if not ass_path:
            return
        gender_path = filedialog.askopenfilename(
            title="Wybierz plik z danymi o płci (voice_log.txt)",
            filetypes=[("Pliki TXT", "*.txt"), ("Wszystkie", "*.*")])
        if not gender_path:
            return
        output_path = filedialog.asksaveasfilename(
            title="Zapisz skorygowany plik ASS",
            defaultextension=".ass",
            filetypes=[("Pliki ASS", "*.ass")])
        if not output_path:
            return

        self.log(f"♀♂ Korekta zaimków w: {os.path.basename(ass_path)}...", "INFO")
        try:
            intervals = load_gender_intervals(gender_path)
            validate_ass_pronouns(ass_path, output_path, intervals)
            self.log(f"✔ Skorygowany plik: {output_path}", "SUCCESS")
            messagebox.showinfo("Gotowe", f"Zaimki podmienione!\n{output_path}")
        except Exception as e:
            self.log(f"✖ Błąd korekty zaimków: {e}", "ERROR")
            messagebox.showerror("Błąd", str(e))

    def _check_updates_gui(self):
        """Sprawdza aktualizacje z GitHub."""
        self.log("🔄 Sprawdzanie aktualizacji...", "INFO")

        def _check():
            info = check_for_updates()
            if info.get("error"):
                self.log(f"⚠ Aktualizacje: {info['error']}", "WARNING")
                self.root.after(0, lambda: messagebox.showwarning(
                    "Aktualizacje", f"Nie można sprawdzić:\n{info['error']}"))
            elif info.get("available"):
                self.log(f"🔄 Nowa wersja: {info['latest']} (aktualna: {info['current']})", "INFO")
                self.root.after(0, lambda: self._show_update_dialog(info))
            else:
                self.log(f"✔ Masz najnowszą wersję: {info['current']}", "SUCCESS")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Aktualizacje", f"Masz najnowszą wersję: {info['current']}"))

        threading.Thread(target=_check, daemon=True).start()

    def _show_update_dialog(self, info):
        if messagebox.askyesno(
            "Nowa wersja!",
            f"Dostępna nowa wersja: {info['latest']}\n"
            f"Twoja wersja: {info['current']}\n\n"
            f"Otworzyć stronę pobierania?"):
            open_releases_page()

    # =========================================================
    # LOGOWANIE
    # =========================================================
    def log(self, message: str, level: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        icons = {"INFO": "ℹ", "DEBUG": "🐞", "WARNING": "⚠", "ERROR": "✖", "SUCCESS": "✔"}
        icon = icons.get(level, "ℹ")
        formatted = f"[{timestamp}] {icon}  {message}\n"

        def _write():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, formatted, level)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, _write)

    def _set_status(self, text: str, color: str = C_MUTED):
        def _upd():
            self.status_lbl.config(text=text)
            self.status_dot.config(fg=color)
        self.root.after(0, _upd)

    # =========================================================
    # DOSTAWCA AI / MODEL
    # =========================================================
    def _rebuild_provider(self):
        """Tworzy nowy obiekt AIProvider na podstawie aktualnych ustawień UI."""
        name = self.provider_combo.get()
        api_key = self.api_key_entry.get().strip()
        custom_url = self.custom_url_entry.get().strip()
        self.provider = AIProvider(name, api_key=api_key, custom_url=custom_url)

    def _check_ollama_async(self):
        """Sprawdza połączenie z dostawcą AI i ładuje modele."""
        def _init():
            self._rebuild_provider()
            ok = self.check_connection()
            if ok:
                self.load_available_models()
        threading.Thread(target=_init, daemon=True).start()

    def check_connection(self) -> bool:
        self._rebuild_provider()
        ok, msg = self.provider.check_connection()
        if ok:
            self.log(msg, "SUCCESS")
            self._set_status(f"{self.provider_combo.get()}: OK", C_SUCCESS)
        else:
            self.log(msg, "ERROR")
            self._set_status(msg, C_ERROR)
        return ok

    def check_model(self):
        model_name = self.model_combo.get().strip()
        if not model_name:
            messagebox.showwarning("Uwaga", "Wpisz/wybierz model!")
            return
        self._rebuild_provider()
        available, msg = self.provider.check_model_available(model_name)
        if available:
            self.log(msg, "SUCCESS")
            messagebox.showinfo("Model OK", msg)
        else:
            self.log(msg, "WARNING")
            if self.provider.supports_pull:
                if messagebox.askyesno("Pobierz model?",
                                       f"{msg}\nCzy pobrać go teraz? (tylko Ollama)"):
                    self.log(f"Pobieranie '{model_name}'...", "INFO")
                    if self.provider.pull_model(model_name):
                        self.log(f"Model '{model_name}' pobrany.", "SUCCESS")
                    else:
                        self.log("Błąd pobierania modelu.", "ERROR")
            else:
                messagebox.showwarning("Model", msg)

    def load_available_models(self):
        """Pobiera listę modeli od aktualnego dostawcy."""
        self._rebuild_provider()
        try:
            models = self.provider.list_models()
            if models:
                if self.provider.is_ollama:
                    preferred = [m for m in models if "translategemma" in m]
                    others = [m for m in models if "translategemma" not in m]
                    sorted_models = preferred + others
                    light_first = sorted(models, key=lambda m: (
                        0 if any(x in m for x in [":3b", ":7b", ":8b", "phi", "gemma", "mistral"])
                        else 1))
                else:
                    sorted_models = models
                    light_first = models

                def _update_combos():
                    self.model_combo["values"] = sorted_models
                    self.model_combo.config(state="normal")
                    if self.provider.is_ollama:
                        self.model_combo.config(state="readonly")
                    if sorted_models:
                        # Zachowaj obecny wybór jeśli jest na liście
                        current = self.model_combo.get()
                        if current not in sorted_models:
                            self.model_combo.set(sorted_models[0])

                    self.context_model_combo["values"] = light_first
                    if self.provider.is_ollama:
                        self.context_model_combo.config(state="readonly")
                    else:
                        self.context_model_combo.config(state="normal")
                    current_ctx = self.context_model_combo.get()
                    if current_ctx not in light_first:
                        self.context_model_combo.set(light_first[0] if light_first else "")

                self.root.after(0, _update_combos)
                self.log(f"Dostępne modele ({len(models)}): {', '.join(sorted_models[:8])}{'...' if len(sorted_models)>8 else ''}", "SUCCESS")
            else:
                self.log("Brak modeli. Sprawdź połączenie lub klucz API.", "WARNING")
        except Exception as e:
            self.log(f"Błąd ładowania modeli: {e}", "ERROR")

    # =========================================================
    # POMOCNICZE
    # =========================================================
    def extract_text_and_styles(self, text: str):
        styles = re.findall(r"(\{\\[^}]*\})", text)
        clean_text = re.sub(r"\{\\[^}]*\}", "", text).strip()
        return clean_text, styles

    def rebuild_text_with_styles(self, translated: str, styles: list) -> str:
        if not translated.strip():
            return translated
        return "".join(styles) + translated

    def load_mod_rules(self, file_path: str) -> dict:
        if not file_path or not os.path.exists(file_path):
            return {"replace": [], "ignore": [], "delete": []}
        mod_rules = {"replace": [], "ignore": [], "delete": []}
        current_section = None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.lower() in ("[replace]", "[replacements]"):
                        current_section = "replace"
                    elif line.lower() in ("[ignore]", "[ignores]"):
                        current_section = "ignore"
                    elif line.lower() in ("[delete]", "[deletes]", "[delate]"):
                        current_section = "delete"
                    elif current_section == "replace" and ":" in line:
                        parts = line.split(":", 1)
                        mod_rules["replace"].append((parts[0].strip(), parts[1].strip()))
                    elif current_section:
                        mod_rules[current_section].append(line)
            self.log(
                f"Słownik MOD: {len(mod_rules['replace'])} zamian, "
                f"{len(mod_rules['ignore'])} ignorowanych, {len(mod_rules['delete'])} usunięć",
                "INFO")
        except Exception as e:
            self.log(f"Błąd ładowania słownika MOD: {e}", "ERROR")
        return mod_rules

    def apply_mod_rules(self, text: str, mod_rules: dict) -> str:
        for old, new in mod_rules.get("replace", []):
            text = text.replace(old, new)
        for item in mod_rules.get("ignore", []):
            text = text.replace(item, "")
        for item in mod_rules.get("delete", []):
            text = text.replace(item, "")
        return text.strip()

    def _reset_prompt(self):
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", DEFAULT_PROMPT)
        self.log("Prompt zresetowany do domyślnego.", "INFO")

    def _current_context_model(self) -> str:
        return self.context_model_combo.get().strip() or DEFAULT_MODEL

    def _current_model(self) -> str:
        return self.model_combo.get().strip() or DEFAULT_MODEL

    def _current_source_lang(self) -> str:
        return self.source_lang_entry.get().strip() or DEFAULT_SOURCE_LANG

    def _current_target_lang(self) -> str:
        return self.target_lang_entry.get().strip() or DEFAULT_TARGET_LANG

    # =========================================================
    # FAZA 1 — ANALIZA KONTEKSTU
    # =========================================================
    def analyze_context(self, ass_lines: list) -> str:
        """Wysyła WSZYSTKIE dialogi do Ollamy (w porcjach), prosi o analizę kontekstu."""
        dialogue_texts = []
        for line in ass_lines:
            if line.startswith("Dialogue:"):
                parts = line.split(",", maxsplit=9)
                if len(parts) >= 10:
                    clean, _ = self.extract_text_and_styles(parts[9])
                    if clean.strip():
                        dialogue_texts.append(clean.strip())

        if not dialogue_texts:
            return "(Brak dialogów w pliku)"

        # Podziel na porcje po ~150 linii
        CHUNK_SIZE = 150
        num_chunks = math.ceil(len(dialogue_texts) / CHUNK_SIZE)
        all_notes = []

        self.log(f"Analizuję kontekst z {len(dialogue_texts)} linii dialogowych "
                 f"({num_chunks} porcji) — model: {self._current_context_model()}", "INFO")

        for i in range(num_chunks):
            if self.cancel_flag:
                return "(Anulowano analizę kontekstu)"

            start = i * CHUNK_SIZE
            end = min(start + CHUNK_SIZE, len(dialogue_texts))
            chunk = dialogue_texts[start:end]

            chunk_label = f"[{i+1}/{num_chunks}]" if num_chunks > 1 else ""
            self.log(f"  Porcja {chunk_label} linie {start+1}–{end}...", "INFO")

            prompt = CONTEXT_PROMPT.format(dialogues="\n".join(chunk))

            try:
                self._rebuild_provider()
                notes = self.provider.generate(
                    model=self._current_context_model(),
                    prompt=prompt,
                    temperature=0.4,
                    max_tokens=600,
                    timeout=180
                )
                if notes:
                    all_notes.append(notes)
            except Exception as e:
                self.log(f"Błąd analizy porcji {i+1}: {e}", "WARNING")
                all_notes.append(f"(Błąd porcji {i+1}: {e})")

        # Scal notatki z wszystkich porcji
        if len(all_notes) == 1:
            merged = all_notes[0]
        elif len(all_notes) > 1:
            merged = "\n\n--- Notatki z porcji ---\n\n".join(
                [f"📋 Porcja {i+1}:\n{n}" for i, n in enumerate(all_notes)]
            )
        else:
            merged = "(Brak wyników analizy kontekstu)"

        self.log(f"Analiza kontekstu zakończona ({len(all_notes)} porcji).", "SUCCESS")
        return merged

    def show_context_dialog(self, context_notes: str) -> str | None:
        """
        Pokazuje okno dialogowe z notatkami kontekstu.
        Zwraca ostateczny tekst notatek (po ewentualnej edycji) lub None jeśli anulowano.
        """
        result = {"value": None}
        dialog = tk.Toplevel(self.root)
        dialog.title("📋 Analiza kontekstu — potwierdź")
        dialog.geometry("780x560")
        dialog.configure(bg=C_BG)
        dialog.grab_set()
        dialog.resizable(True, True)

        tk.Label(dialog, text="🎭 Analiza kontekstu pliku napisów",
                 bg=C_BG, fg=C_ACCENT, font=("Segoe UI", 13, "bold")).pack(pady=(16, 4))

        tk.Label(dialog,
                 text="AI przeanalizował dialogi i stworzył poniższe notatki.\n"
                      "Możesz je edytować przed zatwierdzeniem.",
                 bg=C_BG, fg=C_MUTED, font=("Segoe UI", 9), justify=tk.CENTER).pack(pady=(0, 8))

        text_frame = tk.Frame(dialog, bg=C_BORDER, padx=1, pady=1)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=4)

        notes_text = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, font=("Segoe UI", 10),
            bg=C_PANEL, fg=C_TEXT, insertbackground=C_TEXT,
            selectbackground=C_ACCENT2, relief="flat")
        notes_text.pack(fill=tk.BOTH, expand=True)
        notes_text.insert("1.0", context_notes)

        # Przyciski
        btn_row = tk.Frame(dialog, bg=C_BG)
        btn_row.pack(fill=tk.X, padx=20, pady=12)

        def on_confirm():
            result["value"] = notes_text.get("1.0", tk.END).strip()
            dialog.destroy()

        def on_cancel():
            result["value"] = None
            dialog.destroy()

        HoverButton(btn_row, bg_normal=C_ACCENT, bg_hover=C_BTN_HOV,
                    text="✔   Zatwierdź i tłumacz",
                    fg="white", font=("Segoe UI", 11, "bold"),
                    relief="flat", cursor="hand2", padx=18, pady=8,
                    command=on_confirm).pack(side=tk.LEFT)

        HoverButton(btn_row, bg_normal=C_CARD, bg_hover="#2a2a4a",
                    text="✖  Anuluj",
                    fg=C_MUTED, font=("Segoe UI", 10),
                    relief="flat", cursor="hand2", padx=14, pady=8,
                    command=on_cancel).pack(side=tk.LEFT, padx=10)

        self.root.wait_window(dialog)
        return result["value"]

    # =========================================================
    # FAZA 2 — TŁUMACZENIE
    # =========================================================
    def translate_text(self, text: str, context: str = "") -> str:
        """Tłumaczy pojedynczy tekst przez Ollamę."""
        if not text.strip():
            return text

        user_prompt = self.prompt_text.get("1.0", tk.END).strip() or DEFAULT_PROMPT
        prompt = user_prompt.format(
            source_lang=self._current_source_lang(),
            target_lang=self._current_target_lang(),
            context=context or "Brak dodatkowego kontekstu.",
            text=text
        )

        if self.debug_var.get():
            self.log(f"📤 Zapytanie:\n{prompt}\n{'─'*40}", "DEBUG")

        try:
            self._rebuild_provider()
            raw = self.provider.generate(
                model=self._current_model(),
                prompt=prompt,
                temperature=0.1,
                max_tokens=256,
                timeout=90
            )

            if self.debug_var.get():
                self.log(f"📥 Odpowiedź:\n{raw}\n{'─'*40}", "DEBUG")

            translation = raw
            # Czyść typowe prefliksy
            for prefix in ["Translation:", "Tłumaczenie:", f"{self._current_target_lang().capitalize()}:",
                           "Output:", "Here is", "Here's", "```", '"""']:
                if translation.lower().startswith(prefix.lower()):
                    translation = translation[len(prefix):].strip()

            # Usuń otaczające cudzysłowy
            if len(translation) > 2 and (
                (translation.startswith('"') and translation.endswith('"')) or
                (translation.startswith("'") and translation.endswith("'"))
            ):
                translation = translation[1:-1].strip()

            # Fallback: jeśli odpowiedź zawiera oryginalny tekst, weź ostatnią linię
            src = self._current_source_lang().lower()
            if src in ['en', 'eng']:
                orig_words = text.lower().split()[:3]
                if orig_words and any(w in translation.lower() for w in orig_words):
                    lines = [l.strip() for l in translation.split('\n') if l.strip()]
                    if lines:
                        translation = lines[-1]

            return translation.strip() or text

        except Exception as e:
            self.log(f"Błąd tłumaczenia '{text[:30]}...': {e}", "WARNING")
            return text

    def process_ass_file(self, input_path: str, output_path: str, mod_rules: dict, context: str):
        """Przetwarza cały plik ASS — tłumaczy linię po linii."""
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            total = sum(1 for l in lines if l.startswith("Dialogue:"))
            processed = 0

            with open(output_path, "w", encoding="utf-8") as out:
                for line in lines:
                    if self.cancel_flag:
                        raise InterruptedError("Anulowano przez użytkownika")

                    if line.startswith("Dialogue:"):
                        parts = line.split(",", maxsplit=9)
                        if len(parts) >= 10:
                            raw_text = parts[9]
                            # Zachowaj znak nowej linii z końca oryginału
                            line_ending = "\n" if raw_text.endswith("\n") else ""
                            raw_text_stripped = raw_text.rstrip("\n")
                            clean, styles = self.extract_text_and_styles(raw_text_stripped)

                            if clean.strip():
                                translated = self.translate_text(clean, context)
                                translated = self.apply_mod_rules(translated, mod_rules)
                                # Upewnij się że tłumaczenie nie zawiera wieloliniowych śmieci
                                translated = translated.split("\n")[0].strip()
                                final = self.rebuild_text_with_styles(translated, styles)
                            else:
                                final = raw_text_stripped

                            out.write(",".join(parts[:9]) + "," + final + line_ending)

                            processed += 1
                            pct = (processed / total * 100) if total else 0
                            self.root.after(0, lambda v=pct: self.progress.configure(value=v))
                            src_short = clean[:35] + ("..." if len(clean) > 35 else "")
                            trans_short = translated[:35] + ("..." if len(translated) > 35 else "")  # type: ignore[possibly-undefined]
                            self.log(f"[{processed}/{total}] {src_short}  →  {trans_short}", "INFO")
                        else:
                            out.write(line)
                    else:
                        out.write(line)

                    time.sleep(0.05)

            return True, processed
        except InterruptedError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

    # =========================================================
    # KONTROLA WĄTKÓW / PRZYCISKÓW
    # =========================================================
    def start_translation(self):
        if self.is_translating:
            messagebox.showwarning("Uwaga", "Tłumaczenie już trwa!")
            return

        input_path = self.input_entry.get().strip()
        output_path = self.output_entry.get().strip()

        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Błąd", "Nie wybrano poprawnego pliku wejściowego!")
            return
        if not output_path:
            messagebox.showerror("Błąd", "Nie wybrano ścieżki zapisu!")
            return
        if not self.check_connection():
            if not messagebox.askyesno("Brak połączenia", "Dostawca AI nie odpowiada. Kontynuować mimo to?"):
                return

        mod_rules = self.load_mod_rules(self.mod_entry.get().strip())
        self.context_notes = ""

        # Zablokuj UI
        self.is_translating = True
        self.cancel_flag = False
        self.start_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress.configure(value=0)
        self.log("\n" + "=" * 55, "INFO")
        self.log(f"Plik: {os.path.basename(input_path)}", "INFO")
        self.log(f"Model: {self._current_model()} | {self._current_source_lang()} → {self._current_target_lang()}", "INFO")
        self.log("=" * 55 + "\n", "INFO")

        # Faza 1: analiza kontekstu (w głównym wątku bo otwiera dialog)
        threading.Thread(target=self._phase1_context,
                         args=(input_path, output_path, mod_rules), daemon=True).start()

    def _phase1_context(self, input_path: str, output_path: str, mod_rules: dict):
        """Wątek: analizuje kontekst, pyta użytkownika, uruchamia fazę 2."""
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            context_raw = self.analyze_context(lines)

            # Wróć do głównego wątku by pokazać dialog
            def _show_dialog():
                confirmed_context = self.show_context_dialog(context_raw)
                if confirmed_context is None:
                    # Anulowano
                    self.log("Tłumaczenie anulowane przez użytkownika (etap analizy).", "WARNING")
                    self.root.after(0, self._reset_ui)
                    return
                self.context_notes = confirmed_context
                # Uruchom fazę 2 w osobnym wątku
                threading.Thread(
                    target=self._phase2_translate,
                    args=(input_path, output_path, mod_rules, confirmed_context),
                    daemon=True
                ).start()

            self.root.after(0, _show_dialog)

        except Exception as e:
            self.log(f"Nieoczekiwany błąd w fazie analizy: {e}", "ERROR")
            self.root.after(0, self._reset_ui)

    def _phase2_translate(self, input_path: str, output_path: str, mod_rules: dict, context: str):
        """Wątek: właściwe tłumaczenie zdanie po zdaniu."""
        try:
            success, result = self.process_ass_file(input_path, output_path, mod_rules, context)

            if self.cancel_flag:
                self.log("\n✖ Tłumaczenie anulowane!", "ERROR")
            elif success:
                self.log(f"\n✔ Sukces! Przetłumaczono {result} napisów.", "SUCCESS")
                self.log(f"Zapisano: {output_path}", "SUCCESS")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Gotowe!", f"Pomyślnie przetłumaczono {result} napisów!\n{output_path}"))
            else:
                self.log(f"\n✖ Błąd tłumaczenia: {result}", "ERROR")
                self.root.after(0, lambda: messagebox.showerror("Błąd", f"Nie udało się:\n{result}"))

        except Exception as e:
            self.log(f"\n✖ Nieoczekiwany błąd: {e}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror("Błąd", str(e)))
        finally:
            self.root.after(0, self._reset_ui)

    def _reset_ui(self):
        self.is_translating = False
        self.cancel_flag = False
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress.configure(value=0)

    def cancel_translation(self):
        if self.is_translating:
            self.cancel_flag = True
            self.log("Żądanie anulowania...", "WARNING")

    # =========================================================
    # DIALOGI PLIKÓW
    # =========================================================
    def _open_file_dialog(self, attr: str, title: str, filetypes: list):
        path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if path:
            entry = getattr(self, attr)
            entry.delete(0, tk.END)
            entry.insert(0, path)
            # Jeśli to plik wejściowy, zaproponuj plik wyjściowy
            if attr == "input_entry" and not self.output_entry.get().strip():
                base, _ = os.path.splitext(path)
                lang = self._current_target_lang()
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, f"{base}_{lang}.ass")

    def _save_file_dialog(self, attr: str, title: str, filetypes: list):
        path = filedialog.asksaveasfilename(
            title=title, defaultextension=".ass", filetypes=filetypes)
        if path:
            entry = getattr(self, attr)
            entry.delete(0, tk.END)
            entry.insert(0, path)

    # =========================================================
    # POMOC
    # =========================================================
    def show_help(self):
        messagebox.showinfo("Pomoc", """\
🔧 INSTRUKCJA UŻYTKOWANIA

1. FAZA: ANALIZA KONTEKSTU
   Przed tłumaczeniem AI automatycznie przeanalizuje plik
   i wykryje postacie, ich płeć, ton i kontekst fabularny.
   Możesz edytować te notatki przed zatwierdzeniem.

2. PLIKI
   - Wybierz plik .ass z napisami
   - Ustaw ścieżkę wyjściową (domyślnie: *_pl.ass)
   - (Opcjonalnie) Dodaj słownik MOD (.txt)

3. MODEL
   - Kliknij "🔄 Odśwież" by pobrać listę modeli z Ollamy
   - Domyślny: translategemma:27b
   - Wymagane: ollama serve

4. PROMPT
   - Edytuj prompt tłumaczenia wg potrzeb
   - Dostępne zmienne: {text}, {source_lang}, {target_lang}, {context}
   - "↺ Resetuj" przywraca domyślny prompt

5. SŁOWNIK MOD (format .txt):
   [replace]
   Hello: Cześć
   sword: miecz

   [ignore]
   {\\an8}

   [delete]
   (sound effect)

💡 WSKAZÓWKI
- Większe modele (27b+) = lepsze tłumaczenia
- Kontekst postaci znacznie poprawia jakość
- Tryb debug pokazuje surowe zapytania do AI
""")


# =========================================================
# URUCHOMIENIE
# =========================================================
if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ Brak biblioteki 'requests'. Zainstaluj: pip install requests")
        sys.exit(1)

    root = tk.Tk()
    app = OllamaASSTranslator(root)
    root.mainloop()
