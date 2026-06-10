import streamlit as st
import re
import json
import gzip

# ======================
# LOAD TXT (KAMUS)
# ======================
with open("kbbi_dataset.txt", "r", encoding="utf-8") as f:
    kamus_txt = set([
        line.strip().lower()
        for line in f
        if " " not in line.strip()
    ])

# ======================
# LOAD JSON
# ======================
@st.cache_data
def load_kamus_json():
    with gzip.open("kbbi.json.gz", "rt", encoding="utf-8") as f:
        data = json.load(f)

    return set([
        item["kata"]
        for item in data
        if "kata" in item
    ])

kamus_json = load_kamus_json()

# ======================
# NORMALISASI
# ======================
def normalize_word(word):

    # huruf berulang
    word = re.sub(r'(.)\1+', r'\1', word)

    return word.lower()

# ======================
# METODE EMPIRIS
# ======================
def metode_empiris(kata):

    kandidat_split = []

    for i in range(3, len(kata)-2):

        kiri = kata[:i]
        kanan = kata[i:]

        if len(kiri) < 3 or len(kanan) < 3:
            continue

        skor = 0

        # cek kamus
        if kiri in kamus_txt:
            skor += 2

        if kanan in kamus_txt:
            skor += 2

        # panjang ideal
        if 3 <= len(kiri) <= 7:
            skor += 1

        if 3 <= len(kanan) <= 7:
            skor += 1

        kandidat_split.append((kiri, kanan, skor))

    # ranking terbaik
    if kandidat_split:

        kandidat_split.sort(
            key=lambda x: x[2],
            reverse=True
        )

        return kandidat_split[0]

    return None

# ======================
# PROSES KATA EMPIRIS
# ======================
def proses_empiris(kata):

    kata_asli = kata

    kata = kata.lower().strip(",.!?")
    kata = normalize_word(kata)

    # ======================
    # KATA SUDAH BENAR
    # ======================
    if kata in kamus_json:
        return kata, "BENAR", None

    # ======================
    # PROSES EMPIRIS
    # ======================
    hasil_empiris = metode_empiris(kata)

    if hasil_empiris:

        kiri, kanan, skor = hasil_empiris

        hasil = kiri + " " + kanan

        detail = {
            "split": f"{kiri} + {kanan}",
            "skor": skor
        }

        return hasil, "EMPIRIS", detail

    # ======================
    # GAGAL
    # ======================
    return kata_asli, "TIDAK DIKOREKSI", None

# ======================
# UI STREAMLIT
# ======================
st.title("Spelling Correction Teks Informal Bahasa Indonesia")
st.write("Metode: EMPIRIS")

teks = st.text_area("Masukkan kalimat:")

if st.button("Koreksi"):

    hasil_kalimat = []
    detail_hasil = []

    for kata in teks.split():

        hasil, metode, detail = proses_empiris(kata)

        hasil_kalimat.append(hasil)

        if metode != "BENAR":
            detail_hasil.append(
                (kata, hasil, metode, detail)
            )

    # ======================
    # HASIL AKHIR
    # ======================
    st.subheader("Hasil:")
    st.success(" ".join(hasil_kalimat))

    # ======================
    # DETAIL
    # ======================
    st.subheader("Perbaikan Kata:")

    for kata, hasil, metode, detail in detail_hasil:

        if metode == "EMPIRIS":

            st.info(f"{kata} → {hasil} (EMPIRIS)")

            st.write("Detail Split:")
            st.write(detail["split"])

            st.write("Skor:")
            st.write(detail["skor"])

        else:

            st.warning(
                f"{kata} → tidak bisa dikoreksi"
            )