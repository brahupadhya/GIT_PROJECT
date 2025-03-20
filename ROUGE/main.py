from flask import Flask, render_template, request, jsonify
import evaluate
import matplotlib
matplotlib.use('Agg')  # Gunakan backend non-GUI
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
rouge = evaluate.load("rouge")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate_summary():
    reference_summary = request.form['reference_summary']
    generated_summary = request.form['generated_summary']
    
    scores = rouge.compute(predictions=[generated_summary], references=[reference_summary])

    # Simpan hasil grafik
    types = list(scores.keys())
    values = [score * 100 for score in scores.values()]
    plt.figure(figsize=(8, 5))
    bars = plt.bar(types, values, color=['blue', 'green', 'red', 'purple', 'orange'])

    # Tambahkan angka pada tiap batang
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 2, f'{height:.2f}%', ha='center', fontsize=10)

    plt.xlabel("Metode ROUGE")
    plt.ylabel("Skor (%)")
    plt.title("Hasil Evaluasi ROUGE")
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Pastikan folder static ada
    if not os.path.exists('static'):
        os.makedirs('static')

    img_path = os.path.join('static', 'rouge_scores.png')
    plt.savefig(img_path)  # Simpan gambar
    plt.close()  # Tutup plt agar tidak error

    return jsonify({"scores": scores, "img_path": img_path})

if __name__ == '__main__':
    app.run(debug=True)
