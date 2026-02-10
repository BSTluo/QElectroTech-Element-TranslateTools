import json
import os
import re
import shutil
import time
import urllib.request
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

CONFIG_PATH = "translate_config.json"
SRC_DIR = "src"
RESULT_DIR = "result"


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_cache(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(path, cache):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def escape_xml(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
        .replace("'", "&apos;")
    )


def translate_text(text, config, cache, cache_lock=None):
    # Thread-safe cache read
    if cache_lock:
        with cache_lock:
            if text in cache:
                return cache[text]
    else:
        if text in cache:
            return cache[text]

    payload = {
        "ToLang": config["to_lang"],
        "text": text,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = config.get("headers", {})
    request = urllib.request.Request(config["endpoint"], data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=config.get("timeout_seconds", 20)) as response:
            body = response.read().decode("utf-8")
            result = json.loads(body)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"API Error {e.code}: {error_body}")
        raise RuntimeError(f"Translation API failed for '{text}': {error_body}")

    translated = result.get("translate", "").strip()
    if not translated:
        raise RuntimeError(f"Empty translation for: {text}")

    # Thread-safe cache write
    if cache_lock:
        with cache_lock:
            cache[text] = translated
    else:
        cache[text] = translated
    
    time.sleep(config.get("sleep_seconds", 0))
    return translated


def insert_zh_name(xml_text, config, cache, cache_lock=None):
    names_match = re.search(r"<names>.*?</names>", xml_text, re.DOTALL)
    if not names_match:
        return xml_text, False

    names_block = names_match.group(0)
    if re.search(r"<name\s+lang=\"zh\">", names_block):
        return xml_text, False

    source_text = None
    for lang in config.get("source_lang_priority", ["en", "fr"]):
        lang_match = re.search(
            rf"<name\s+lang=\"{re.escape(lang)}\">\s*(.*?)\s*</name>",
            names_block,
            re.DOTALL,
        )
        if lang_match:
            source_text = lang_match.group(1).strip()
            break

    if not source_text:
        return xml_text, False

    translated = translate_text(source_text, config, cache, cache_lock)
    translated = escape_xml(translated)

    indent_match = re.search(r"\n([ \t]*)<name", names_block)
    name_indent = indent_match.group(1) if indent_match else "    "
    closing_indent_match = re.search(r"\n([ \t]*)</names>", names_block)
    closing_indent = closing_indent_match.group(1) if closing_indent_match else ""

    new_block = re.sub(
        r"</names>",
        f"\n{name_indent}<name lang=\"zh\">{translated}</name>\n{closing_indent}</names>",
        names_block,
        count=1,
    )

    new_text = xml_text.replace(names_block, new_block, 1)
    return new_text, True


def process_file(path, config, cache):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    updated, changed = insert_zh_name(original, config, cache)
    if not changed:
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    return True


def print_progress(current, total, updated, start_time):
    """Print progress bar with statistics"""
    if total == 0:
        return
    
    percentage = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    elapsed = time.time() - start_time
    rate = current / elapsed if elapsed > 0 else 0
    remaining = (total - current) / rate if rate > 0 else 0
    
    print(f"\r[{bar}] {percentage:.1f}% ({current}/{total}) Updated: {updated} | Speed: {rate:.1f} files/s | ETA: {remaining:.0f}s", end="", flush=True)


def process_file_wrapper(file_path, config, cache, cache_lock):
    """Wrapper for parallel processing with thread-safe cache access"""
    with open(file_path, "r", encoding="utf-8") as f:
        original = f.read()

    updated, changed = insert_zh_name(original, config, cache, cache_lock)
    if not changed:
        return False

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated)
    return True


def main():
    print("="*60)
    print(f"QET Directory & Element Translator")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    config = load_config(CONFIG_PATH)
    cache_path = config.get("cache_file", "translate_cache.json")
    cache = load_cache(cache_path)

    # Clean and copy src to result
    print("\n[1/3] Copying src to result directory...")
    if os.path.exists(RESULT_DIR):
        shutil.rmtree(RESULT_DIR)
    shutil.copytree(SRC_DIR, RESULT_DIR)
    print("✓ Copy completed")

    # Count total files to process
    print("\n[2/3] Scanning files...")
    total_files = 0
    file_paths = []
    for root, _, files in os.walk(RESULT_DIR):
        for filename in files:
            if filename == "qet_directory" or filename.lower().endswith(".elmt"):
                file_paths.append(os.path.join(root, filename))
                total_files += 1
    print(f"✓ Found {total_files} files to process")

    # Process files with progress
    max_workers = config.get("max_workers", 0)
    print(f"\n[3/3] Processing and translating...")
    if max_workers > 0:
        print(f"Mode: Parallel (workers={max_workers})")
    else:
        print(f"Mode: Serial")
    
    updated_count = 0
    processed_count = 0
    start_time = time.time()
    cache_lock = threading.Lock()
    
    if max_workers > 0:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(process_file_wrapper, fp, config, cache, cache_lock): fp for fp in file_paths}
            
            for future in as_completed(future_to_file):
                processed_count += 1
                try:
                    if future.result():
                        updated_count += 1
                except Exception as e:
                    print(f"\nError processing file: {e}")
                print_progress(processed_count, total_files, updated_count, start_time)
    else:
        # Serial processing
        for idx, file_path in enumerate(file_paths, 1):
            if process_file(file_path, config, cache):
                updated_count += 1
            print_progress(idx, total_files, updated_count, start_time)

    save_cache(cache_path, cache)
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\n\n{'='*60}")
    print(f"✓ Completed!")
    print(f"  Total files processed: {total_files}")
    print(f"  Files updated: {updated_count}")
    print(f"  Time elapsed: {elapsed:.1f}s")
    print(f"  End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Cache file: {cache_path}")
    print(f"  Output directory: {RESULT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
