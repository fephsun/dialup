"""
Take in a .wav file, do speech recognition, return some text.

See examples/wav_transcribe.py in https://github.com/Uberi/speech_recognition.

For example:
    from recognize import wav_to_text
    print wav_to_text("/path/to/filename.wav")
"""


import secrets
import speech_recognition


def wav_to_text(filename):
    """
    Arguments:
        filename: a path to some file, .wav

    Returns:
        None if nothing was recognized.
        Otherwise, a string for the thing that was recognized.
    """
    # # obtain path to "test.wav" in the same folder as this script
    # from os import path
    # filename = path.join(path.dirname(path.realpath(__file__)), filename)

    r = speech_recognition.Recognizer()
    with speech_recognition.WavFile(filename) as source:
        audio = r.record(source)

    try:
        result = r.recognize_wit(audio, key=secrets.witai_api_key)
        return result
    except:
        pass

    return None
