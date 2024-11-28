def extract_file_path(message: str) -> str:
    for line in message.split('\n'):
        if line.endswith('.mp4'):
            return line
