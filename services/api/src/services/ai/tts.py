import abc

class TextToSpeechAdapter(abc.ABC):
    @abc.abstractmethod
    def synthesize(self, text: str, language: str = "ta") -> dict:
        """Returns audio URL or base64 audio response for approved templated status messages"""
        pass

class MockTextToSpeechAdapter(TextToSpeechAdapter):
    def synthesize(self, text: str, language: str = "ta") -> dict:
        return {
            "audio_url": "/static/audio_placeholders/status_update.mp3",
            "language": language,
            "provider": "mock_sarvam_bulbul_v3",
            "status": "success"
        }

class SarvamBulbulAdapter(TextToSpeechAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def synthesize(self, text: str, language: str = "ta") -> dict:
        if not self.api_key:
            return MockTextToSpeechAdapter().synthesize(text, language)
        return {
            "audio_url": "https://api.sarvam.ai/v1/tts/sample.mp3",
            "language": language,
            "provider": "sarvam_bulbul_v3",
            "status": "success"
        }

def get_tts_adapter(provider_type: str = "mock", api_key: str = "") -> TextToSpeechAdapter:
    if provider_type == "sarvam" and api_key:
        return SarvamBulbulAdapter(api_key=api_key)
    return MockTextToSpeechAdapter()
