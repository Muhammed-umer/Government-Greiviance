import abc

class SpeechToTextAdapter(abc.ABC):
    @abc.abstractmethod
    def transcribe(self, audio_bytes: bytes, language_hint: str = "ta") -> dict:
        """Returns dict with transcript, confidence, and detected language"""
        pass

class MockSpeechToTextAdapter(SpeechToTextAdapter):
    def transcribe(self, audio_bytes: bytes, language_hint: str = "ta") -> dict:
        # Returns controlled transcript fixture for testing / dev
        return {
            "transcript": "எங்கள் தெருவில் கடந்த 3 நாட்களாக மின்சார விளக்கு எரியவில்லை, குப்பைகளும் அதிகமாக சேர்ந்துள்ளது.",
            "confidence": 0.94,
            "detected_language": "ta",
            "provider": "mock_sarvam_saaras_v3"
        }

class SarvamSaarasAdapter(SpeechToTextAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def transcribe(self, audio_bytes: bytes, language_hint: str = "ta") -> dict:
        # Production call to Sarvam Saaras API (fallback to mock if key missing)
        if not self.api_key:
            return MockSpeechToTextAdapter().transcribe(audio_bytes, language_hint)
        # Placeholder for actual Sarvam HTTP request
        return {
            "transcript": "Production Sarvam audio transcript placeholder",
            "confidence": 0.95,
            "detected_language": language_hint,
            "provider": "sarvam_saaras_v3"
        }

def get_stt_adapter(provider_type: str = "mock", api_key: str = "") -> SpeechToTextAdapter:
    if provider_type == "sarvam" and api_key:
        return SarvamSaarasAdapter(api_key=api_key)
    return MockSpeechToTextAdapter()
