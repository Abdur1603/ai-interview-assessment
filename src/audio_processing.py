import os
import subprocess
import shutil
import librosa

def get_ffmpeg_path():
    ffmpeg_path = shutil.which("ffmpeg")
    
    if not ffmpeg_path:
        raise FileNotFoundError(
            "FFmpeg tidak ditemukan di sistem. "
        )
    
    return ffmpeg_path

def fix_video_for_streaming(input_path, output_path):
    """Memperbaiki metadata video agar seekable di browser."""
    try:
        ffmpeg_binary = get_ffmpeg_path()
        command = [
            ffmpeg_binary,
            "-y",
            "-i", input_path,
            "-c", "copy",
            "-movflags", "+faststart",
            output_path,
        ]
        
        # Menjalankan sebagai Subprocess (System Call)
        subprocess.run(
            command, 
            check=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        return True
    except FileNotFoundError as e:
        print(f"System Error: {e}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error saat fix video: {e}")
        return False
    except Exception as e:
        print(f"Error umum fix video: {e}")
        return False

def extract_audio(video_path, output_audio_path):
    """Ekstrak audio ke WAV 16kHz Mono."""
    try:
        ffmpeg_binary = get_ffmpeg_path()
        command = [
            ffmpeg_binary,
            "-y",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            output_audio_path,
        ]
        
        subprocess.run(
            command, 
            check=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # Verifikasi file output ada dan tidak kosong
        if os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 0:
            return True
        return False
        
    except FileNotFoundError as e:
        print(f"System Error: {e}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error saat extract audio: {e}")
        return False
    except Exception as e:
        print(f"Error extract audio: {e}")
        return False

def get_audio_duration(audio_path):
    try:
        return librosa.get_duration(filename=audio_path)
    except Exception as e:
        print(f"Error duration: {e}")
        return 0.0