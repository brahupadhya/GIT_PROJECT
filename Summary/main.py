import os
import re
import logging
from flask import Flask, request, render_template, jsonify
import requests
import fitz
from dotenv import load_dotenv

# Konfigurasi logging
logging.basicConfig(level=logging.DEBUG)

# Memuat variabel lingkungan dari file .env
load_dotenv()

app = Flask(__name__)

# Mengambil API key dari file .env
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logging.error("API Key tidak ditemukan. Pastikan sudah diatur di .env")
    raise ValueError("API Key tidak ditemukan. Pastikan sudah diatur di .env")

gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

def clean_text(text):
    """
    Membersihkan teks dari karakter khusus dan mengganti beberapa simbol dengan karakter ASCII yang lebih umum.
    """
    try:
        text = text.encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'[\u2022\u2023\u25aa\u25cf\u25e6]', '*', text)
        text = re.sub(r'[\u2013\u2014]', '-', text)
        text = re.sub(r'[\u2018\u2019]', "'", text)
        text = re.sub(r'[\u201c\u201d]', '"', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    except Exception as e:
        logging.error(f"Error saat membersihkan teks: {e}")
        return f"Error saat membersihkan teks: {str(e)}"

def extract_metadata_from_text(text):
    """
    Mengekstrak metadata dari teks artikel ilmiah seperti nama jurnal, penulis, dan tahun terbit.
    """
    try:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        metadata = {}
        
        if lines and len(lines[0]) > 5:
            title_candidate = lines[0].split(":")[0].strip()
            if title_candidate:
                metadata["Nama Jurnal"] = title_candidate
        
        author_pattern = r'(?:penulis|by|author)\s*:\s*([A-Za-z\s,\.]+(?:,\s*[A-Za-z\.]+)*)'
        for i, line in enumerate(lines):
            author_match = re.search(author_pattern, line, re.IGNORECASE)
            if author_match:
                metadata["Penulis"] = author_match.group(1).strip()
                break
            elif i == 1 and len(line) > 5 and not line[0].isdigit() and "tujuan" not in line.lower():
                metadata["Penulis"] = line.strip()
                break
        
        year_pattern = r'\b(19|20)\d{2}\b'
        for line in lines:
            year_match = re.search(year_pattern, line)
            if year_match:
                metadata["Tahun Terbit"] = year_match.group(0)
                break
        
        return metadata if metadata else {}
    except Exception as e:
        logging.error(f"Error saat mengekstrak metadata: {e}")
        return {"Error": f"Error saat mengekstrak metadata: {str(e)}"}

def extract_text_from_pdf(pdf_file):
    """
    Mengekstrak teks dari file PDF yang diunggah.
    """
    try:
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
            text = "\n".join([page.get_text("text") for page in doc])
        return clean_text(text)
    except Exception as e:
        logging.error(f"Error saat mengekstrak teks dari PDF: {e}")
        return f"Error saat mengekstrak teks dari PDF: {str(e)}"

def summarize_text(text):
    """
    Menghasilkan ringkasan otomatis menggunakan API Gemini AI.
    """
    try:
        if len(text) > 4000:
            text = text[:4000] + "... [teks dipotong untuk efisiensi]"

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"""
                    Buat ringkasan singkat dan terstruktur dari artikel ilmiah berikut dengan format:
                    
                    **Pendahuluan / Latar Belakang / Tujuan:**  
                    (Ringkas dalam 1-2 kalimat)
                    
                    **Studi Literatur / Metode:**  
                    (Ringkas dalam 1-2 kalimat)
                    
                    **Hasil / Pembahasan:**  
                    (Ringkas dalam 1-2 kalimat)
                    
                    **Kesimpulan:**  
                    (Ringkas dalam 1-2 kalimat)

                    Artikel Ilmiah:  
                    {text}
                    """
                }]
            }]
        }

        response = requests.post(gemini_api_url, headers=headers, json=payload)
        logging.debug(f"API Response: {response.status_code} - {response.text}")

        if not response.ok:
            return f"Error dari API: {response.status_code} - {response.text}"
        
        result = response.json()
        if "candidates" not in result or not result["candidates"]:
            return f"Error: Respons API tidak valid - {result}"
        
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error jaringan: {e}")
        return f"Error jaringan saat menghubungi API: {str(e)}"
    except Exception as e:
        logging.error(f"Error tak terduga: {e}")
        return f"Error tak terduga saat menghasilkan ringkasan: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Halaman utama untuk mengunggah PDF dan menampilkan metadata serta teks hasil ekstraksi.
    """
    if request.method == "POST":
        pdf_file = request.files.get("pdf_file")
        if not pdf_file:
            return jsonify({"error": "Tidak ada file yang diunggah"}), 400
        if pdf_file.mimetype != "application/pdf":
            return jsonify({"error": "File harus berformat PDF"}), 400
        
        extracted_text = extract_text_from_pdf(pdf_file)
        if not isinstance(extracted_text, str) or "Error" in extracted_text:
            return jsonify({"error": "Gagal mengekstrak teks dari PDF"}), 500
        
        metadata = extract_metadata_from_text(extracted_text)
        if "Error" in metadata:
            return jsonify({"error": metadata["Error"]}), 500

        return jsonify({
            "metadata": metadata,
            "extracted_text": extracted_text
        })
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    """
    Endpoint untuk meringkas teks yang diberikan oleh pengguna.
    """
    try:
        data = request.get_json()
        text = data.get("text", "")
        if not text:
            return jsonify({"error": "Tidak ada teks yang diberikan"}), 400
        
        summary = summarize_text(text)
        if "Error" in summary:
            return jsonify({"error": summary}), 500
        
        return jsonify({"summary": summary})
    except Exception as e:
        logging.error(f"Server error: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
