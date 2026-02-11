import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
import winreg
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import threading

CONFIG_PATH = "translate_config.json"
SRC_DIR = "src"
RESULT_DIR = "result"


def resolve_shortcut_target(lnk_path):
    try:
        escaped_path = str(lnk_path).replace("'", "''")
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{escaped_path}'); $s.TargetPath",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        target = result.stdout.strip()
        return target if target else None
    except Exception:
        return None


def confirm_path(candidate_path, source_label):
    while True:
        answer = input(
            f"检测到{source_label}: {candidate_path}\n是否使用这个路径？[Y/n]: "
        ).strip().lower()
        if answer in ("", "y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("请输入 Y 或 N。")


def find_qet_installation():
    """
    自动检测QElectroTech安装路径（Windows）
    优先级：
    1. 从注册表读取
    2. 从桌面快捷方式解析安装位置
    3. 检查常见安装位置
    4. 从配置文件读取用户自定义路径
    """
    print("[检测] QElectroTech 安装路径...")

    # 1. 尝试从注册表读取（最准确）
    try:
        key_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\QElectroTech",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\QElectroTech",
        ]

        for key_path in key_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    install_location, _ = winreg.QueryValueEx(key, "InstallLocation")
                    elements_path = Path(install_location) / "elements"
                    if elements_path.exists():
                        print(f"✓ 从注册表找到: {elements_path}")
                        return str(elements_path)
            except FileNotFoundError:
                continue
    except Exception as e:
        print(f"  注册表检测失败: {e}")

    # 2. 从桌面快捷方式解析安装位置
    desktop_paths = [
        Path(os.path.expanduser("~")) / "Desktop",
        Path(r"C:\Users\Public\Desktop"),
    ]
    shortcut_candidates = []
    for desktop in desktop_paths:
        if not desktop.exists():
            continue
        for shortcut in desktop.glob("*.lnk"):
            if "qelectrotech" in shortcut.name.lower():
                shortcut_candidates.append(shortcut)

    for shortcut in shortcut_candidates:
        target = resolve_shortcut_target(shortcut)
        if not target:
            continue
        target_path = Path(target)
        if not target_path.exists():
            continue
        install_dir = target_path.parent
        elements_path = install_dir / "elements"
        if elements_path.exists():
            if confirm_path(elements_path, f"桌面快捷方式 ({shortcut.name})"):
                print(f"✓ 使用快捷方式路径: {elements_path}")
                return str(elements_path)
            break

    # 3. 检查常见安装位置
    common_paths = [
        Path(r"C:\Program Files\QElectroTech\elements"),
        Path(r"C:\Program Files (x86)\QElectroTech\elements"),
        Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "QElectroTech" / "elements",
        Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "QElectroTech" / "elements",
    ]

    print("  检查常见安装位置...")
    for path in common_paths:
        if path.exists():
            print(f"✓ 找到安装路径: {path}")
            return str(path)

    # 4. 从配置文件读取（如果有）
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            custom_path = config.get("qet_elements_path")
            if custom_path:
                path = Path(custom_path)
                if path.exists():
                    print(f"✓ 使用配置文件路径: {path}")
                    return str(path)
                else:
                    print(f"⚠ 配置文件中的路径不存在: {path}")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    print("✗ 未找到QElectroTech安装路径")
    return None


def sync_elements(qet_path, src_path):
    """
    同步QElectroTech的elements文件夹到src目录
    """
    print(f"\n[同步] 开始同步元件库...")
    print(f"  源路径: {qet_path}")
    print(f"  目标路径: {src_path}")

    if os.path.exists(src_path):
        print("  清空现有src目录...")
        shutil.rmtree(src_path)

    print("  复制文件中...")
    shutil.copytree(qet_path, src_path)

    file_count = 0
    for root, _, files in os.walk(src_path):
        for filename in files:
            if filename == "qet_directory" or filename.lower().endswith(".elmt"):
                file_count += 1

    print(f"✓ 同步完成！共 {file_count} 个元件文件")
    return file_count


def add_path_to_config(qet_path):
    """
    将QElectroTech路径保存到配置文件中，方便下次使用
    """
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    config["qet_elements_path"] = qet_path

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("✓ QElectroTech路径已保存到配置文件")


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


def translate_text_openai(text, config):
    api_key = config.get("openai_api_key")
    if not api_key:
        raise RuntimeError("Missing openai_api_key in translate_config.json")

    base_url = config.get("openai_base_url", "https://api.openai.com/v1").rstrip("/")
    model = config.get("openai_model", "gpt-5.2")
    to_lang = config.get("to_lang", "zh-CHS")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": f"Translate the user text to {to_lang}. Return only the translated text."},
            {"role": "user", "content": text},
        ],
        "temperature": 0,
    }

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=config.get("timeout_seconds", 20)) as response:
            body = response.read().decode("utf-8")
            result = json.loads(body)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"OpenAI Error {e.code}: {error_body}")
        raise RuntimeError(f"OpenAI translation failed for '{text}': {error_body}")

    choices = result.get("choices", [])
    if not choices:
        raise RuntimeError(f"Empty OpenAI response for: {text}")

    translated = choices[0].get("message", {}).get("content", "").strip()
    if not translated:
        raise RuntimeError(f"Empty translation for: {text}")

    time.sleep(config.get("sleep_seconds", 0))
    return translated


def translate_text(text, config, cache, cache_lock=None):
    # Thread-safe cache read
    if cache_lock:
        with cache_lock:
            if text in cache:
                return cache[text]
    else:
        if text in cache:
            return cache[text]

    mode = config.get("translate_mode", "api").lower()
    if mode == "openai":
        translated = translate_text_openai(text, config)
    else:
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

    print("\n[1/4] 同步元件库...")
    qet_path = find_qet_installation()
    if not qet_path:
        print("\n❌ 无法自动检测QElectroTech安装路径")
        print("\n请手动指定路径：")
        print("方法1: 在 translate_config.json 中添加以下配置：")
        print('  "qet_elements_path": "C:\\Program Files\\QElectroTech\\elements"')
        print("\n方法2: 运行时指定路径：")
        manual_path = input("请输入QElectroTech的elements文件夹路径（或按回车退出）: ").strip()

        if not manual_path:
            print("已取消")
            return 1

        qet_path = manual_path.strip('"').strip("'")
        if not os.path.exists(qet_path):
            print(f"❌ 路径不存在: {qet_path}")
            return 1

    try:
        sync_elements(qet_path, SRC_DIR)
        add_path_to_config(qet_path)
    except Exception as e:
        print(f"\n❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    cache_path = config.get("cache_file", "translate_cache.json")
    cache = load_cache(cache_path)

    # Clean and copy src to result
    print("\n[2/4] Copying src to result directory...")
    if os.path.exists(RESULT_DIR):
        shutil.rmtree(RESULT_DIR)
    shutil.copytree(SRC_DIR, RESULT_DIR)
    print("✓ Copy completed")

    # Count total files to process
    print("\n[3/4] Scanning files...")
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
    print(f"\n[4/4] Processing and translating...")
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
