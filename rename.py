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
    return {key.strip(): value.strip() for key, value in pairs}

def sanitize_filename(filename):
    # Menghapus karakter keyboard yang illegal untuk file Windows
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def fuzzy_get(data, key):
    """Get the closest matching key from data dict."""
    keys = list(data.keys())
    match = difflib.get_close_matches(key, keys, n=1, cutoff=0.6)
    if match:
        return data[match[0]]
    return ""  # Default if no match found

def rename_pdfs_in_folder(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(directory, filename)
            print(f"Processing: {filename}")

            text = extract_all_text_from_pdf(path)
            data = extract_all_key_value_pairs(text)

            # Ganti variabel sesuai yang kalian mau
            kode = fuzzy_get(data, "Kode dan Nomor Seri Faktur Pajak")
            referensi = fuzzy_get(data, "Referensi").replace("/", "").replace("-", "")
            nama = fuzzy_get(data, "Nama")

            # print(text)

            # Variabel nama file tersebut dengan aman, ganti variabel sesuai yang kalian mau
            new_filename = f"{kode} - {referensi} - {nama}.pdf"
            print(new_filename)
            new_filename = sanitize_filename(new_filename)

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