
# Project Overview
This project is a Computer Vision-based Attendance System that allows users to register faces and recognize them using both a Command Line Interface (CLI) and a Graphical User Interface (GUI).
Contains multi-thread architecture and MVC pattern architecture for scalability and responsiveness

## Features
- Face registration and recognition
- Attendance management
- CLI and GUI modes
- Test image support for development and evaluation

---

# Getting Started

## 1. Install Dependencies
```bash
pip install -r requirements.txt
```

## 2. Project Structure
- `app/main-cli.py`: Command Line Interface for registration and recognition
- `app/main.py`: Graphical User Interface (GUI) for the app
- `test_images/registration/`: Images for registration
- `test_images/test/`: Images for testing recognition
- `database/`: SQLite database files

---

# Usage

## A. Using the CLI App
Run the CLI app for face registration and recognition:
```bash
python app/main-cli.py
```

### CLI Options
- Register a new user: Follow prompts to input user details and provide registration images.
- Recognize a face: Provide a test image to identify the user.
- Mark Attendance using photo or web cam
- Run test case and generate confusion matrix on seeded test case data

## B. Using the GUI App
Launch the GUI for a user-friendly interface:
```bash
python app/main.py
```

### GUI Features
- Register faces with webcam or by uploading images
- Recognize faces in real-time or from images
- View attendance records

---

# Testing
To run the test script, Use CLI and select `option 3`   

---

# Notes
- All images for registration should be placed in `test_images/registration/`. Images placed in this folder will be seeded into the database. File name will be taken as user name. For e.g. `prabhu.jpeg`, Prabhu will be the username.
- Test images for recognition should be placed in `test_images/test/`. Here, the image file name should be `[username]_[number].jpeg`. For e.g. `prabhu_1.jpeg`. This images are used to generate test accuracy report. 
- The database is stored in `database/main.db`. 

---

# Troubleshooting
- Ensure all dependencies are installed.
- If you encounter issues with the GUI, verify that all required Python packages for GUI (e.g., PyQt5) are installed.
- For database errors, check that the `database/` directory exists and is writable.

---

# Contact
For any issues, contact: Prabhu Gurung (K2463337)

---
