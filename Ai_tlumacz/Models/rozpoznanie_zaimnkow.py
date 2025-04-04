import sounddevice as sd
import numpy as np
import librosa
import os
from collections import Counter

def format_time(seconds):
    """Konwertuje liczbę sekund na format HH:MM:SS."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

class RozpoznanieZaimnkow:
    def __init__(self, input_dir="../input", output_dir="../output", temp_dir="../tempsf",
                 duration_threshold=1.0, sample_rate=22050, frame_duration=1.0):
        """
        input_dir: Katalog z plikami audio (np. WAV).
        output_dir: Katalog do zapisywania logów.
        temp_dir: Katalog dla pliku tymczasowego z danymi zaimków.
        duration_threshold: Minimalny czas trwania segmentu (w sekundach) uznawanego za mowę.
        sample_rate: Częstotliwość próbkowania.
        frame_duration: Czas trwania pojedynczego segmentu (w sekundach).
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration  # w sekundach
        self.is_running = False
        self.log_file = os.path.join(output_dir, "voice_log.txt")
        self.temp_file = os.path.join(temp_dir, "temp_data.txt")
        
        # Tworzenie katalogów, jeśli nie istnieją
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _log_voice(self, gender, start_sec, end_sec):
        """
        Zapisuje do pliku log informację o wykrytym głosie w formacie:
        <gender_code> <start_time>-<end_time>
        Gdzie 1 = Mężczyzna, 0 = Kobieta.
        """
        # Przypisanie kodu płci
        code = "1" if gender == "Mężczyzna" else "0"
        start_formatted = format_time(start_sec)
        end_formatted = format_time(end_sec)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{code} {start_formatted}-{end_formatted}\n")
    
    def _detect_gender(self, audio):
        """
        Wykrywa płeć na podstawie analizy częstotliwości fundamentalnej.
        Zwraca "Mężczyzna", jeśli median f0 < 165 Hz, w przeciwnym razie "Kobieta".
        """
        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(audio, fmin=50, fmax=300)
            if f0 is None:
                return None
            valid_f0 = f0[~np.isnan(f0)]
            if len(valid_f0) == 0:
                return None
            median_f0 = np.median(valid_f0)
            return "Mężczyzna" if median_f0 < 165 else "Kobieta"
        except Exception as e:
            print(f"Błąd detekcji: {e}")
            return None

    def _compute_rms(self, audio_segment):
        """Oblicza wartość RMS dla danego segmentu audio."""
        return np.sqrt(np.mean(audio_segment**2))
    
    def _detect_voice_activity(self, audio):
        """Wykrywa obszary aktywności głosowej w pliku audio."""
        intervals = librosa.effects.split(audio, top_db=20)  # Dopasuj próg 'top_db' w zależności od hałasu
        return intervals

    def _process_audio_file(self, file_path, gender_list):
        """Przetwarza pojedynczy plik audio, wykrywając płeć dla poszczególnych segmentów."""
        print(f"Przetwarzam plik: {file_path}")
        try:
            audio, sr = librosa.load(file_path, sr=self.sample_rate)
        except Exception as e:
            print(f"Błąd wczytywania pliku {file_path}: {e}")
            return
        num_samples = len(audio)

        for i in range(0, num_samples, int(self.frame_duration * self.sample_rate)):
            audio_segment = audio[i: i + int(self.frame_duration * self.sample_rate)]
            
            # Obliczanie RMS segmentu
            rms = self._compute_rms(audio_segment)
            print(f"RMS dla segmentu {i}: {rms}")

            if rms < 0.01:  # Można dostosować próg
                print(f"Segment {i} jest poniżej progu głośności. Ignorowanie...")
                continue

            gender = self._detect_gender(audio_segment)
            if gender is None:
                continue
            start_sec = i / self.sample_rate
            end_sec = (i + len(audio_segment)) / self.sample_rate
            self._log_voice(gender, start_sec, end_sec)
            gender_list.append(gender)
            print(f"Wykryto: {gender} od {format_time(start_sec)} do {format_time(end_sec)}.")

    def start(self):
        """
        Uruchamia przetwarzanie wszystkich plików audio w katalogu input.
        Po przetworzeniu oblicza wynik większościowy i zapisuje go do pliku tymczasowego.
        """
        print("Rozpoczęto przetwarzanie plików audio...")
        gender_list = []
        try:
            for file_name in os.listdir(self.input_dir):
                file_path = os.path.join(self.input_dir, file_name)
                if file_path.lower().endswith(".wav"):
                    print(f"Przetwarzanie pliku: {file_path}")
                    audio, sr = librosa.load(file_path, sr=self.sample_rate)
                    voice_activity = self._detect_voice_activity(audio)

                    for start, end in voice_activity:
                        audio_segment = audio[start:end]
                        gender = self._detect_gender(audio_segment)
                        if gender:
                            start_sec = start / self.sample_rate
                            end_sec = end / self.sample_rate
                            self._log_voice(gender, start_sec, end_sec)
                            gender_list.append(gender)
                            print(f"Wykryto: {gender} od {format_time(start_sec)} do {format_time(end_sec)}.")
        except KeyboardInterrupt:
            print("Zakończono przetwarzanie plików.")

        if gender_list:
            overall_gender, count = Counter(gender_list).most_common(1)[0]
            with open(self.temp_file, "w", encoding="utf-8") as f:
                f.write("1" if overall_gender == "Mężczyzna" else "0")
            print(f"Ogólna wykryta płeć: {overall_gender}")
        else:
            print("Nie wykryto żadnych danych.")
        
if __name__ == "__main__":
    rz = RozpoznanieZaimnkow(input_dir="../input", output_dir="../output", temp_dir="../tempsf")
    rz.start()
