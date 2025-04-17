import os
from dotenv import load_dotenv

load_dotenv()

# Google OAuth config
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "960746908063-m2u4e7v8nfvbhjbqga0s85qsjttfa7s1.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "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")
