import requests
from tkinter import messagebox

# Twoja obecna wersja
current_version = "1.0.0"

# URL do API GitHub
GITHUB_RELEASES_API_URL = "https://api.github.com/repos/MASELKO-95/Tlumacz-napisow-ai/releases"

def check_for_updates():
    try:
        # Wysyłamy zapytanie GET do GitHub API
        response = requests.get(GITHUB_RELEASES_API_URL)
        response.raise_for_status()  # Sprawdzamy, czy nie ma błędów w odpowiedzi
        
        # Pobieramy najnowszą wersję z odpowiedzi API
        latest_version = response.json()[0]["tag_name"]
        
        # Porównanie wersji
        if latest_version != current_version:
            messagebox.showinfo("Aktualizacja dostępna!", f"Nowa wersja {latest_version} jest dostępna!\nZaktualizuj, aby uzyskać nowe funkcje.")
        else:
            messagebox.showinfo("Brak aktualizacji", "Masz najnowszą wersję programu.")
    
    except requests.exceptions.RequestException as err:
        messagebox.showerror("Błąd połączenia", f"Nie udało się połączyć z GitHub: {err}")
