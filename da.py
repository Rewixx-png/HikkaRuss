import os
import sys
import argparse
from pathlib import Path

# --- КОНФИГУРАЦИЯ ПО УМОЛЧАНИЮ ---
DEFAULT_MAX_CHUNK_SIZE = 500 * 1024  # 500 KB
OUTPUT_DIR = "project_chunks"

# Папки, которые мы игнорируем (системные, кэши, билды, сессии)
IGNORE_DIRS = {
    '.git', '.idea', '.vscode', '.github', 
    '__pycache__', 'node_modules', 'venv', 'env', 
    'build', 'dist', 'bin', 'obj', 'target',
    'project_chunks', 'migrations', 'coverage',
    '.pytest_cache', '.mypy_cache', 'Session'
}

# Файлы, которые мы игнорируем (бинарники, медиа, локи, СЕССИИ)
IGNORE_EXTENSIONS = {
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp', '.bmp', '.tiff',
    # Executables / Libs
    '.exe', '.dll', '.so', '.dylib', '.class', '.o', '.a',
    # Archives
    '.zip', '.tar', '.gz', '.7z', '.rar', '.jar',
    # Documents / Data
    '.pdf', '.docx', '.xlsx', '.pptx', '.db', '.sqlite', '.sqlite3',
    # Python bytecode
    '.pyc', '.pyo',
    # Lock files
    'package-lock.json', 'yarn.lock', 'poetry.lock', 'Cargo.lock',
    # SENSITIVE DATA (SESSIONS)
    '.session', '.session-journal' 
}

def is_text_file(filepath):
    """Проверяет, является ли файл текстовым, пытаясь прочитать начало."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read(1024)
            return True
    except (UnicodeDecodeError, PermissionError):
        return False

def generate_tree(source_path):
    """Генерирует визуальное дерево проекта для контекста."""
    tree_str = ["PROJECT STRUCTURE:"]
    source_path = Path(source_path)
    
    for root, dirs, files in os.walk(source_path):
        # Фильтрация и сортировка на месте
        dirs[:] = sorted([d for d in dirs if d not in IGNORE_DIRS])
        files = sorted([f for f in files if Path(f).suffix.lower() not in IGNORE_EXTENSIONS])
        
        level = root.replace(str(source_path), '').count(os.sep)
        indent = ' ' * 4 * level
        
        current_dir_name = os.path.basename(root)
        if root == str(source_path):
            current_dir_name = "."
            
        tree_str.append(f"{indent}{current_dir_name}/")
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree_str.append(f"{subindent}{f}")
            
    return "\n".join(tree_str) + "\n\n" + ("="*50) + "\n\n"

def save_chunk(chunk_data, chunk_number, output_folder):
    if not chunk_data:
        return

    filename = os.path.join(output_folder, f"project_part_{chunk_number}.txt")
    content = "".join(chunk_data)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
        
    size_kb = os.path.getsize(filename) / 1024
    print(f"📦 [Chunk {chunk_number}] Сохранен: {filename} ({size_kb:.2f} KB)")

def main():
    parser = argparse.ArgumentParser(description="Упаковщик проекта для LLM контекста.")
    parser.add_argument("--source", default=".", help="Папка исходного кода")
    parser.add_argument("--out", default=OUTPUT_DIR, help="Папка для сохранения чанков")
    parser.add_argument("--size", type=int, default=DEFAULT_MAX_CHUNK_SIZE, help="Макс размер чанка в байтах")
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    output_path = Path(args.out)

    if not output_path.exists():
        os.makedirs(output_path)
    else:
        # Очистка старых чанков
        for f in output_path.glob("project_part_*.txt"):
            os.remove(f)

    print(f"🚀 Старт упаковки: {source_path}")
    print(f"⚙️  Лимит чанка: {args.size / 1024:.0f} KB")

    # 1. Генерируем дерево проекта и кладем в начало первого чанка
    project_tree = generate_tree(source_path)
    current_chunk = [project_tree]
    current_size = len(project_tree.encode('utf-8'))
    chunk_counter = 1

    script_name = os.path.basename(__file__)

    # 2. Обходим файлы
    for root, dirs, files in os.walk(source_path):
        # Фильтрация директорий
        dirs[:] = sorted([d for d in dirs if d not in IGNORE_DIRS and d != args.out])
        
        # Сортировка файлов для детерминированного порядка
        files.sort()

        for file in files:
            file_path = Path(root) / file
            
            if file == script_name:
                continue

            if file_path.suffix.lower() in IGNORE_EXTENSIONS:
                continue

            if not is_text_file(file_path):
                continue

            try:
                relative_path = file_path.relative_to(source_path)
                
                # Формируем заголовок
                file_header = (
                    f"========================================\n"
                    f"FILE PATH: {relative_path}\n"
                    f"========================================\n"
                )
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                file_footer = "\n\n"

                full_entry = file_header + content + file_footer
                entry_size = len(full_entry.encode('utf-8'))

                # Если файл больше лимита чанка — он пойдет отдельно или обрежется (здесь просто кладем в новый)
                if current_size + entry_size > args.size:
                    if current_chunk: # Сохраняем текущий, если не пуст
                        save_chunk(current_chunk, chunk_counter, output_path)
                        chunk_counter += 1
                        current_chunk = []
                        current_size = 0

                current_chunk.append(full_entry)
                current_size += entry_size

            except Exception as e:
                print(f"⚠️ Ошибка обработки {file}: {e}")

    # Сохраняем остаток
    if current_chunk:
        save_chunk(current_chunk, chunk_counter, output_path)

    print(f"\n✅ Готово! Файлы лежат в: {output_path.absolute()}")

if __name__ == "__main__":
    main()
