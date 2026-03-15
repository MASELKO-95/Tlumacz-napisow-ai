#!/usr/bin/env python3
"""
Moduł sprawdzania aktualizacji z GitHub.
Porównuje lokalną wersję z najnowszym release na GitHub.
"""

import requests
import webbrowser

GITHUB_API_URL = "https://api.github.com/repos/MASELKO-95/Tlumacz-napisow-ai/releases/latest"
CURRENT_VERSION = "3.0.0"
REPO_URL = "https://github.com/MASELKO-95/Tlumacz-napisow-ai"


def check_for_updates() -> dict:
    """
    Sprawdza czy jest dostępna nowa wersja na GitHub.
    Zwraca dict: {"available": bool, "latest": str, "current": str, "url": str, "notes": str}
    """
    result = {
        "available": False,
        "latest": CURRENT_VERSION,
        "current": CURRENT_VERSION,
        "url": REPO_URL,
        "notes": "",
        "error": None
    }

    try:
        resp = requests.get(GITHUB_API_URL, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            latest_tag = data.get("tag_name", "").lstrip("vV")
            result["latest"] = latest_tag
            result["url"] = data.get("html_url", REPO_URL)
            result["notes"] = data.get("body", "")

            # Porównanie wersji (proste porównanie stringów)
            if latest_tag and latest_tag != CURRENT_VERSION:
                try:
                    latest_parts = [int(x) for x in latest_tag.split(".")]
                    current_parts = [int(x) for x in CURRENT_VERSION.split(".")]
                    if latest_parts > current_parts:
                        result["available"] = True
                except ValueError:
                    # Jeśli nie da się sparsować, porównaj jako string
                    if latest_tag > CURRENT_VERSION:
                        result["available"] = True
        elif resp.status_code == 404:
            result["error"] = "Brak releases na GitHub."
        else:
            result["error"] = f"HTTP {resp.status_code}"
    except requests.exceptions.Timeout:
        result["error"] = "Timeout — brak połączenia z GitHub."
    except requests.exceptions.ConnectionError:
        result["error"] = "Brak połączenia z internetem."
    except Exception as e:
        result["error"] = str(e)

    return result


def open_releases_page():
    """Otwiera stronę releases w przeglądarce."""
    webbrowser.open(f"{REPO_URL}/releases")


if __name__ == "__main__":
    info = check_for_updates()
    if info["error"]:
        print(f"❌ Błąd: {info['error']}")
    elif info["available"]:
        print(f"🔄 Nowa wersja dostępna: {info['latest']} (aktualna: {info['current']})")
        print(f"   Pobierz: {info['url']}")
    else:
        print(f"✔ Masz najnowszą wersję: {info['current']}")
