#!/usr/bin/env python3
"""
Moduł dostawców AI — abstrakcja nad różnymi API (Ollama, OpenAI, DeepSeek, Custom).
"""

import requests
import json

# ============================================================
# KONFIGURACJA DOSTAWCÓW
# ============================================================

PROVIDERS = {
    "Ollama (lokalny)": {
        "type": "ollama",
        "base_url": "http://localhost:11434",
        "api_key_required": False,
        "description": "Lokalne modele przez Ollama",
    },
    "OpenAI (GPT)": {
        "type": "openai",
        "base_url": "https://api.openai.com/v1",
        "api_key_required": True,
        "description": "GPT-4o, GPT-4o-mini, itp.",
        "default_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "DeepSeek": {
        "type": "openai",  # DeepSeek używa formatu OpenAI
        "base_url": "https://api.deepseek.com/v1",
        "api_key_required": True,
        "description": "DeepSeek-V3, DeepSeek-Chat",
        "default_models": ["deepseek-chat", "deepseek-reasoner"],
    },
    "Google Gemini": {
        "type": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "api_key_required": True,
        "description": "Gemini 2.0 Flash, Pro, itp.",
        "default_models": ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-pro"],
    },
    "LM Studio (lokalny)": {
        "type": "openai",  # LM Studio udaje OpenAI API
        "base_url": "http://localhost:1234/v1",
        "api_key_required": False,
        "description": "Lokalne modele przez LM Studio",
    },
    "Niestandardowy (Custom API)": {
        "type": "openai",
        "base_url": "",
        "api_key_required": True,
        "description": "Dowolne API kompatybilne z OpenAI",
    },
}


def get_provider_names() -> list:
    return list(PROVIDERS.keys())


def get_provider_config(name: str) -> dict:
    return PROVIDERS.get(name, PROVIDERS["Ollama (lokalny)"])


# ============================================================
# KLASA DOSTAWCY
# ============================================================

class AIProvider:
    """Uniwersalny interfejs do komunikacji z różnymi API AI."""

    def __init__(self, provider_name: str, api_key: str = "", custom_url: str = ""):
        self.provider_name = provider_name
        self.config = get_provider_config(provider_name)
        self.api_key = api_key
        self.provider_type = self.config["type"]

        # Custom URL nadpisuje bazowy
        if custom_url.strip():
            self.base_url = custom_url.rstrip("/")
        else:
            self.base_url = self.config["base_url"].rstrip("/")

    # ---- SPRAWDZANIE POŁĄCZENIA ----

    def check_connection(self) -> tuple:
        """Sprawdza połączenie z API. Zwraca (bool, str_message)."""
        try:
            if self.provider_type == "ollama":
                resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if resp.status_code == 200:
                    return True, "Ollama działa poprawnie."
                return False, f"Ollama: HTTP {resp.status_code}"

            elif self.provider_type == "openai":
                resp = requests.get(
                    f"{self.base_url}/models",
                    headers=self._openai_headers(),
                    timeout=10)
                if resp.status_code == 200:
                    return True, f"{self.provider_name}: połączono."
                elif resp.status_code == 401:
                    return False, "Błędny klucz API!"
                return False, f"HTTP {resp.status_code}"

            elif self.provider_type == "gemini":
                resp = requests.get(
                    f"{self.base_url}/models?key={self.api_key}",
                    timeout=10)
                if resp.status_code == 200:
                    return True, "Google Gemini: połączono."
                elif resp.status_code == 400 or resp.status_code == 403:
                    return False, "Błędny klucz API Gemini!"
                return False, f"HTTP {resp.status_code}"

        except requests.exceptions.ConnectionError:
            return False, "Brak połączenia z serwerem."
        except requests.exceptions.Timeout:
            return False, "Timeout — serwer nie odpowiada."
        except Exception as e:
            return False, str(e)

        return False, "Nieznany typ dostawcy."

    # ---- LISTA MODELI ----

    def list_models(self) -> list:
        """Pobiera listę dostępnych modeli."""
        try:
            if self.provider_type == "ollama":
                resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
                resp.raise_for_status()
                return [m["name"] for m in resp.json().get("models", [])]

            elif self.provider_type == "openai":
                resp = requests.get(
                    f"{self.base_url}/models",
                    headers=self._openai_headers(),
                    timeout=10)
                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    models = [m["id"] for m in data if "id" in m]
                    # Filtruj — pokaż tylko modele chat/completion
                    chat_models = [m for m in models if any(
                        k in m for k in ["gpt", "chat", "deepseek", "llama", "mistral",
                                         "claude", "gemma", "phi", "qwen"])]
                    return chat_models if chat_models else models[:20]
                # Fallback do domyślnych
                return self.config.get("default_models", [])

            elif self.provider_type == "gemini":
                resp = requests.get(
                    f"{self.base_url}/models?key={self.api_key}",
                    timeout=10)
                if resp.status_code == 200:
                    models_data = resp.json().get("models", [])
                    return [m["name"].replace("models/", "") for m in models_data
                            if "generateContent" in str(m.get("supportedGenerationMethods", []))]
                return self.config.get("default_models", [])

        except Exception:
            pass

        return self.config.get("default_models", [])

    # ---- GENEROWANIE TEKSTU (PROMPT) ----

    def generate(self, model: str, prompt: str,
                 temperature: float = 0.3, max_tokens: int = 512,
                 timeout: int = 120) -> str:
        """
        Wysyła prompt do modelu i zwraca odpowiedź tekstową.
        Universalny interfejs dla wszystkich dostawców.
        """
        if self.provider_type == "ollama":
            return self._generate_ollama(model, prompt, temperature, max_tokens, timeout)
        elif self.provider_type == "openai":
            return self._generate_openai(model, prompt, temperature, max_tokens, timeout)
        elif self.provider_type == "gemini":
            return self._generate_gemini(model, prompt, temperature, max_tokens, timeout)
        else:
            raise ValueError(f"Nieznany typ dostawcy: {self.provider_type}")

    # ---- IMPLEMENTACJE WEWNĘTRZNE ----

    def _openai_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _generate_ollama(self, model, prompt, temperature, max_tokens, timeout) -> str:
        resp = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens}
            },
            timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()

    def _generate_openai(self, model, prompt, temperature, max_tokens, timeout) -> str:
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self._openai_headers(),
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "").strip()
        return ""

    def _generate_gemini(self, model, prompt, temperature, max_tokens, timeout) -> str:
        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                }
            },
            timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "").strip()
        return ""

    # ---- SPRAWDZANIE/POBIERANIE MODELU (Ollama only) ----

    def check_model_available(self, model_name: str) -> tuple:
        """Sprawdza czy model jest dostępny. Zwraca (bool_available, str_message)."""
        models = self.list_models()
        if model_name in models:
            return True, f"Model '{model_name}' jest dostępny."
        return False, f"Model '{model_name}' nie jest dostępny."

    def pull_model(self, model_name: str) -> bool:
        """Pobiera model (tylko Ollama). Zwraca True jeśli sukces."""
        if self.provider_type != "ollama":
            return False
        try:
            resp = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=600)
            return resp.status_code == 200
        except Exception:
            return False

    @property
    def is_ollama(self) -> bool:
        return self.provider_type == "ollama"

    @property
    def supports_pull(self) -> bool:
        return self.provider_type == "ollama"
