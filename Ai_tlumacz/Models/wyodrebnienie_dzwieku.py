import os
from pydub import AudioSegment

def extract_audio_from_video(video_path, output_audio_path):
    """Wyodrębnia dźwięk z pliku wideo i zapisuje go jako plik audio."""
    try:
        audio = AudioSegment.from_file(video_path, format="mp4")
        audio.export(output_audio_path, format="wav")
        print(f"Dźwięk wyodrębniony do: {output_audio_path}")
    except Exception as e:
        print(f"Błąd podczas wyodrębniania dźwięku z pliku {video_path}: {e}")

if __name__ == "__main__":
    input_folder = "../input"  # Ścieżka do folderu z plikami wideo
    output_folder = "../tempsf"  # Ścieżka do folderu, w którym będą zapisywane pliki audio

    # Sprawdź wszystkie pliki w katalogu input
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".mp4"):  # Sprawdź, czy plik jest wideo
            video_path = os.path.join(input_folder, file_name)
            audio_output_file = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.wav")
            extract_audio_from_video(video_path, audio_output_file)
