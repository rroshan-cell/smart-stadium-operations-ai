import os

def load_config():
    return {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "STADIUM_NAME": "MetLife Stadium",
        "CAPACITY": 82500
    }
