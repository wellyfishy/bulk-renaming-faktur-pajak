import fitz  # PyMuPDF
import os
import re
import sys
import difflib

def resource_path(relative_path):
    """Mencari path ke resource ketika menjalankan script python atau exe."""
    try:
        # Jika dijalankan sebagai .exe
        base_path = sys._MEIPASS
    except AttributeError:
        # Jika dijalankan sebagai .py
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_unique_filename(directory, desired_filename, current_filename=None):
    base, ext = os.path.splitext(desired_filename)

    # Strip "(n)" suffix for clean base
    match = re.match(r"^(.*?)( \((\d+)\))?$", base)
    if match:
        clean_base = match.group(1)
    else:
        clean_base = base

    # Case 1: if desired == current, just keep it
    if current_filename and desired_filename == current_filename:
        return current_filename

    # Case 2: if desired exists but is not current, add suffix
    counter = 1
    new_filename = f"{clean_base}{ext}"
    while os.path.exists(os.path.join(directory, new_filename)):
        # if the existing file is ourself, allow it
        if current_filename and new_filename == current_filename:
            return current_filename
        new_filename = f"{clean_base} ({counter}){ext}"
        counter += 1

    return new_filename

def extract_all_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_all_key_value_pairs(text):
    # Mengambil pasangan "Label: Value" sampai newline atau tutup kurung
    pairs = re.findall(r"([\w\s]+?)\s*:\s*([^\n)]+)", text)

    data = {}

    for key, value in pairs:
        key = key.strip()
        value = value.strip()

        if ":" in value:
            inner_pairs = re.findall(r"([\w\s]+?)\s*:\s*([^\n]+)", value)
            for inner_key, inner_value, in inner_pairs:
                data.setdefault(inner_key.strip(), []).append(inner_value.strip())
        else:
            data.setdefault(key, []).append(value)

    return data

def sanitize_filename(filename):
    # Menghapus karakter keyboard yang illegal untuk file Windows
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# fuzzy yeha
def fuzzy_get(data, key):
    keys = list(data.keys())
    match = difflib.get_close_matches(key, keys, n=1, cutoff=0.7)
    if match:
        values = data[match[0]]
        if isinstance(values, list):
            return values[-1]
        return values
    return ""

def extract_above_and_date(text):
    lines = text.splitlines()
    results = []

    for i, line in enumerate(lines):
        if re.match(r"\b\d{1,2}-\d{4}\b", line):
            date = line.strip()
            above = lines[i-1].strip() if i > 0 else ""
            results.append((above, date))
    return results

def rename_pdfs_in_folder(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(directory, filename)
            print(f"Processing: {filename}")


            text = extract_all_text_from_pdf(path)
            data = extract_all_key_value_pairs(text)

            pairs = extract_above_and_date(text)

            # Ganti variabel sesuai yang kalian mau
            if pairs:
                kode = pairs[0][0] if pairs[0][0] else ""
                masa_pajak = pairs[0][1] if pairs[0][1] else ""
            else:
                kode = ""
                masa_pajak = ""
            nomor = fuzzy_get(data, "Nomor Dokumen")
            nama_pemotong = fuzzy_get(data, "PEMUNGUT PPh")

            print(data)

            # Variabel nama file tersebut dengan aman, ganti variabel sesuai yang kalian mau
            new_filename = f"{kode} - {masa_pajak} - {nomor} - {nama_pemotong}.pdf"
            new_filename = sanitize_filename(new_filename)

            new_filename = get_unique_filename(directory, new_filename, filename)

            new_path = os.path.join(directory, new_filename)

            # Ganti nama file PDF jika terganti
            if filename != new_filename:
                os.rename(path, new_path)
                print(f"Ganti nama ke: {new_filename}")
            else:
                print(f"PDF Tidak diganti namanya: {filename}")

if __name__ == "__main__":
    # Ambil folder yang sama dengan .exe atau scriptnya
    folder = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    rename_pdfs_in_folder(folder)

    print("\nDone!")