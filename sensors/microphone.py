import pyaudio
import wave
import os


def record_voice(duration=4, samplerate=22050, output_path="temp_voice.wav"):
    """
    Records voice from microphone and saves as .wav file.
    Returns: path to saved .wav file, or None if failed.

    duration    : seconds to record (default 4)
    samplerate  : audio sample rate (default 22050)
    output_path : where to save the .wav file
    """

    CHUNK    = 1024
    FORMAT   = pyaudio.paInt16
    CHANNELS = 1

    p = pyaudio.PyAudio()

    print(f"Recording voice for {duration} seconds — speak now...")

    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=samplerate,
            input=True,
            frames_per_buffer=CHUNK
        )

        frames = []
        total_chunks = int(samplerate / CHUNK * duration)

        for i in range(total_chunks):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            # Print progress
            progress = int((i / total_chunks) * 20)
            bar = "█" * progress + "░" * (20 - progress)
            print(f"\r  [{bar}] {int(i/total_chunks*100)}%", end="")

        print("\nRecording complete ✓")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save to .wav file
        wf = wave.open(output_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(samplerate)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"Voice saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"ERROR recording voice: {e}")
        p.terminate()
        return None


def cleanup_audio(path="temp_voice.wav"):
    """Delete temp audio file after feature extraction."""
    if path and os.path.exists(path):
        os.remove(path)
        print(f"Cleaned up {path}")