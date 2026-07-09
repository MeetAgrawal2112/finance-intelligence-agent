# ml/text_utils.py
import re

def clean_text(text: str) -> str:
    """
    Transaction description clean karo.
    Yeh function training aur inference dono mein same hona chahiye.
    """
    text = text.lower()
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text