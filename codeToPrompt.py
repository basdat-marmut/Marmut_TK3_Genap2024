import os

def read_file(file_path):
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading {file_path}: {e}"

def get_files_in_directory(directory):
    file_paths = []
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isfile(full_path):
            file_paths.append(full_path)
    return file_paths

def write_to_txt(file_paths, output_file="codeToPrompt.txt"):
    content = "ini adalah kode sekarang:\n\n"
    for path in file_paths:
        if not path:  # Skip empty paths
            continue
        if os.path.isdir(path):  # If the path is a directory
            directory_files = get_files_in_directory(path)
            for file_path in directory_files:
                file_content = read_file(file_path)
                content += f"{file_path}:\n{file_content}\n\n\n"
        else:  # If the path is a file
            file_content = read_file(path)
            content += f"{path}:\n{file_content}\n\n\n"
    
    try:
        with open(output_file, "w", encoding='utf-8') as file:
            file.write(content)
        print(f"Content written to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

# List of file paths including empty ones and directories
file_paths = [
    r"langganan",
    r"marmut",
    r"connector",
    r"main",
    r"",
    r"",
    r"",
    r"",
    r"",
    r"",
    r"",
]

write_to_txt(file_paths)