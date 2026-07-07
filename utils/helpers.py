import os

def load_config():
    return {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "STADIUM_NAME": "MetLife Stadium",
        "CAPACITY": 82500
    }
