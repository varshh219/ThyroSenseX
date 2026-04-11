import pyaudio, wave, os

def record_voice(duration=4, samplerate=22050,
                 output_path='temp_voice.wav'):
    """Records voice and saves as .wav file."""
    CHUNK, FORMAT, CHANNELS = 1024, pyaudio.paInt16, 1
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=samplerate, input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    total  = int(samplerate / CHUNK * duration)
    for i in range(total):
        frames.append(stream.read(CHUNK, exception_on_overflow=False))
    stream.stop_stream(); stream.close(); p.terminate()
    wf = wave.open(output_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(samplerate)
    wf.writeframes(b''.join(frames))
    wf.close()
    return output_path

def cleanup_audio(path='temp_voice.wav'):
    if path and os.path.exists(path):
        os.remove(path)
