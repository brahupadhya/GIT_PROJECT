import os
import sys

# Tambahkan direktori proyek ke sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Import aplikasi Flask dari main.py
from main import app as application

# Pastikan aplikasi berjalan dengan Passenger
if __name__ == "__main__":
    application.run()