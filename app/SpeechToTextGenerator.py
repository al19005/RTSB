from __future__ import division

import re
import sys
import threading
from cv2 import TermCriteria_COUNT

from google.cloud import speech

import pyaudio
from six.moves import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
"""
exitを呼ばないと音声認識が終わらない
"""
class SpeechToTextGenerator():
    def __init__(self):
        self.updating_data = ""
        self.is_Final = False
        self.closed = False
        # Now, put the transcription responses to use.
        t = threading.Thread(target=self._start)
        t.start()

    def _start(self):
        language_code = "ja-JP"  # a BCP-47 language tag

        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True,
        )

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = client.streaming_recognize(streaming_config, requests)
            self._listen_loop(responses)
        print("end MicrophoneStream")
    
    def _listen_loop(self, responses):
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            transcript = result.alternatives[0].transcript
            if not result.is_final:
                self.updating_data = transcript
            else:
                self.updating_data = transcript
                self.is_Final = True
            if self.closed:
                print("closed")
                break
    
    def exit(self):
        self.closed = True

    def get_speech(self):
        if self.is_Final:
            self.is_Final = False
            text = self.updating_data
            self.updating_data = ""
            return True, text
        
        return False, self.updating_data


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,

            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # バッファオブジェクトを満たすためにオーディオストリームを非同期で実行します。
            #これは、呼び出し側のスレッドがネットワーク要求などをしている間に、
            # 入力デバイスのバッファがオーバーフローしないようにするために必要なことです。
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    speechToTextGenerator = SpeechToTextGenerator()

    while(True):
        t = input()
        if t == "exit":
            speechToTextGenerator.exit()
            break
        log, new = speechToTextGenerator.get_speech()
        print(log)
        print(new)

if __name__ == "__main__":
    main()
