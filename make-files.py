import os



structure = {
    "backend": {
        "models": [
            "__init__.py",
            "nlp_model.py",
            "emotion_detector.py",
            "face_recognition.py",
            "task_classifier.py",
        ],
        "core": [
            "__init__.py",
            "memory_manager.py",
            "voice_handler.py",
            "scheduler.py",
            "context_manager.py",
        ],
        "utils": [
            "__init__.py",
            "audio_utils.py",
            "text_processing.py",
            "security.py",
        ],
        "data": {
            "models": [],
            "datasets": [],
            "user_data": [],
        },
        "database": [
            "init_db.py",
            "schemas.sql",
        ],
        "files": [
            "app.py",
            "config.py",
            "requirements.txt",
        ],
    },
    "frontend": {
        "css": [
            "style.css",
        ],
        "js": [
            "main.js",
            "voice.js",
            "camera.js",
        ],
        "assets": {
            "images": [],
            "sounds": [],
        },
        "files": [
            "index.html",
        ],
    },
    "training": {
        "datasets": [
            "intents.json",
            "emotions.json",
        ],
        "files": [
            "train_nlp_model.py",
            "train_emotion_model.py",
        ],
    },
    "docs": [
        "README.md",
        "API_documentation.md",
    ],
}

def create_structure(base_path, tree):
    for name, contents in tree.items():
        dir_path = os.path.join(base_path, name)
        os.makedirs(dir_path, exist_ok=True)

        if isinstance(contents, dict):
            create_structure(dir_path, contents)
        elif isinstance(contents, list):
            for item in contents:
                if isinstance(item, str):
                    file_path = os.path.join(dir_path, item)
                    open(file_path, 'w').close()

def create_files(folder, files):
    for file in files:
        open(os.path.join(folder, file), 'w').close()

def run():
    root = "."  # Current directory
    for folder, content in structure.items():
        folder_path = os.path.join(root, folder)
        os.makedirs(folder_path, exist_ok=True)

        if isinstance(content, dict):
            create_structure(folder_path, content)
        elif isinstance(content, list):
            create_files(folder_path, content)

if __name__ == "__main__":
    run()
