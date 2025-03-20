import evaluate
import matplotlib.pyplot as plt

# Inisialisasi evaluator ROUGE
rouge = evaluate.load("rouge")

# Ringkasan referensi (yang dibuat oleh manusia)
reference_summary = ["tujuan penelitian ini adalah mengukur sejauhmana kualitas manajemen proyek sistem informasi pelayanan DPPMPTSP Kota Denpasar menggunakan Framework Project Management Body of Knowledge (PMBOK) pada area Project Management Quality. Pada penelitian ini mempergunakan Capability Maturity Model (CMM) yang bertujuan untuk untuk menilai tingkat kematangan (maturity level) dalam pengembangan sistem informasi pada proyek sistem pelayanan perizinan tersebut. Berdasarkan hasil perhitungan dan pengolahan data menemukan penilaian Plan Quality (PQ) memiliki nilai terendah yaitu 4,25 yang disebabkan belum terbitnya regulasi kerjasama dengan dinas terkait pelaksanaan sistem pelayanan perizinan, sedangkan pada Quality Assurance (QA) terdapat temuan bahwa saat ini Sistem Informasi Pelayanan Perizinan masih belum dirilis secara publik, pelaksanaan ujicoba hanya dilaksanakan sebatas di lingkungan tim pengawas dan tim informasi teknologi pada DPMPTSP Kota Denpasar. Sedangkan pada Quality Control (QC) terdapat temuan bahwa belum diketahuinya bug atau masalah yang terdapat pada sistem, rencananya akan diujicoba dengan inputan data uji sebelum resmi dirilis secara publik."]

# Ringkasan yang dihasilkan oleh AI
generated_summary = ["Penelitian ini bertujuan untuk mengevaluasi kualitas manajemen proyek Sistem Informasi Pelayanan DPMPTSP Kota Denpasar dengan menggunakan framework Project Management Body of Knowledge (PMBOK) pada area Project Management Quality. Evaluasi ini penting sebelum sistem dirilis untuk memastikan kelayakan dan kesesuaian sistem dengan ketentuan.  Penelitian ini menggunakan Capability Maturity Model (CMM) untuk menilai tingkat kematangan sistem informasi, dengan responden adalah 4 pegawai yang bertanggung jawab dalam proyek tersebut. Kuesioner evaluasi dibagi berdasarkan tiga sub kelompok proses PMBOK: Plan Quality (PQ), Quality Assurance (QA), dan Quality Control (QC). Penilaian Plan Quality (PQ) memiliki nilai terendah karena belum adanya regulasi kerjasama, Quality Assurance (QA) menemukan bahwa sistem belum dirilis publik dan uji coba terbatas, dan Quality Control (QC) menemukan bahwa bug pada sistem belum diketahui karena kurangnya uji coba data. Kualitas manajemen proyek sistem informasi pelayanan perizinan perlu ditingkatkan, terutama pada aspek regulasi kerjasama, pelaksanaan uji coba yang lebih luas, dan identifikasi bug sebelum rilis publik. Uji coba skala besar direkomendasikan untuk perbaikan di masa depan."]

# Hitung skor ROUGE
scores = rouge.compute(predictions=generated_summary, references=reference_summary)

# Cetak hasil evaluasi dengan format lebih jelas
print("\nNilai Evaluasi ROUGE:")
for metric, score in scores.items():
    print(f"{metric}: {score:.4f}")


# Cetak hasil evaluasi dengan format persentase
print("\nPersentase Evaluasi ROUGE:")
for metric, score in scores.items():
    percentage = score * 100
    print(f"{metric}: {percentage:.2f}%")

# Visualisasi hasil ROUGE
types = list(scores.keys())
values = [score * 100 for score in scores.values()]

plt.figure(figsize=(8, 5))
plt.bar(types, values, color=['blue', 'green', 'red', 'purple', 'orange'])
plt.xlabel("Metode ROUGE")
plt.ylabel("Skor (%)")
plt.title("Hasil Evaluasi ROUGE")
plt.ylim(0, 100)
plt.xticks(rotation=45)

# Tambahkan angka pada tiap batang
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 2, f'{height:.2f}%', ha='center', fontsize=10)

bars = plt.bar(types, values, color=['blue', 'green', 'red', 'purple', 'orange'])
add_labels(bars)

plt.show()
