import subprocess
import sys
import platform

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Brak pakietu: {package}. Pobierz go ręcznie lub zainstaluj automatycznie.")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Pakiet {package} został pomyślnie zainstalowany.")
        except subprocess.CalledProcessError:
            print(f"Nie udało się zainstalować pakietu: {package}. Pobierz go ręcznie.")

# Sprawdzenie systemu operacyjnego
oS_name = platform.system()
print(f"Uruchamianie na systemie: {oS_name}")

# Lista wymaganych bibliotek
REQUIRED_LIBRARIES = [
    "tk", "pydub", "numpy", "sounddevice", "librosa", "transformers", "tensorflow",
    "re", "os", "collections", "time"
]

# Instalacja brakujących pakietów
for package in REQUIRED_LIBRARIES:
    install_package(package)

print("Wszystkie wymagane pakiety zostały sprawdzone!")