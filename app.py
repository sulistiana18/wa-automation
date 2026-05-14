from flask import Flask, render_template, request
import pandas as pd
import pywhatkit as kit
import time
import os
import webbrowser

app = Flask(__name__)

# =========================
# UPLOAD FOLDER
# =========================

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================
# MAIN PAGE
# =========================

@app.route("/", methods=["GET", "POST"])
def index():

    success_message = ""

    # default template
    template_pesan = """
Halo {nama},

Kami mengingatkan bahwa interview untuk posisi {posisi}
akan dilaksanakan pada tanggal {tanggal}.

Mohon hadir tepat waktu.

Terima kasih.
"""

    if request.method == "POST":

        try:

            # =========================
            # GET FORM
            # =========================

            file = request.files["excel"]

            tanggal_pilih = request.form["tanggal"]

            # ambil pesan terakhir dari textarea
            template_pesan = request.form["pesan"]

            # =========================
            # SAVE FILE
            # =========================

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )

            file.save(filepath)

            # =========================
            # READ EXCEL
            # =========================

            df = pd.read_excel(filepath)

            # rapikan nama kolom
            df.columns = df.columns.str.strip()

            # =========================
            # VALIDASI KOLOM
            # =========================

            required_columns = [
                "Nama",
                "Nomor",
                "Posisi",
                "Tanggal Interview"
            ]

            for col in required_columns:

                if col not in df.columns:

                    success_message = (
                        f"Kolom '{col}' tidak ditemukan."
                    )

                    return render_template(
                        "index.html",
                        success_message=success_message,
                        template_pesan=template_pesan
                    )

            # =========================
            # FORMAT TANGGAL
            # =========================

            df["Tanggal Interview"] = pd.to_datetime(
                df["Tanggal Interview"],
                errors="coerce"
            ).dt.strftime("%Y-%m-%d")

            # =========================
            # FILTER TANGGAL
            # =========================

            kandidat = df[
                df["Tanggal Interview"] == tanggal_pilih
            ]

            kandidat = kandidat.reset_index(drop=True)

            # =========================
            # VALIDASI DATA
            # =========================

            if kandidat.empty:

                success_message = (
                    "Tidak ada kandidat "
                    "pada tanggal tersebut."
                )

                return render_template(
                    "index.html",
                    success_message=success_message,
                    template_pesan=template_pesan
                )

            # =========================
            # TOTAL TERKIRIM
            # =========================

            total_terkirim = 0

            print("\n===================")
            print("MULAI KIRIM PESAN")
            print("===================\n")

            # =========================
            # LOOP KANDIDAT
            # =========================

            for i in range(len(kandidat)):

                row = kandidat.iloc[i]

                # stop kalau nama kosong
                if pd.isna(row["Nama"]):

                    print(
                        "Nama kosong -> stop"
                    )

                    break

                # stop kalau nomor kosong
                if pd.isna(row["Nomor"]):

                    print(
                        "Nomor kosong -> stop"
                    )

                    break

                # =========================
                # AMBIL DATA
                # =========================

                nama = str(
                    row["Nama"]
                ).strip()

                posisi = str(
                    row["Posisi"]
                ).strip()

                nomor = ''.join(
                    filter(
                        str.isdigit,
                        str(row["Nomor"])
                    )
                )

                # stop kalau nomor invalid
                if nomor == "":

                    print(
                        "Nomor invalid -> stop"
                    )

                    break

                # =========================
                # TEMPLATE PESAN
                # =========================

                pesan_final = template_pesan

                pesan_final = pesan_final.replace(
                    "{nama}",
                    nama
                )

                pesan_final = pesan_final.replace(
                    "{posisi}",
                    posisi
                )

                pesan_final = pesan_final.replace(
                    "{tanggal}",
                    tanggal_pilih
                )

                print(
                    f"{i + 1}. Kirim ke {nama}"
                )

                # =========================
                # KIRIM WHATSAPP
                # =========================

                kit.sendwhatmsg_instantly(
                    phone_no="+" + nomor,
                    message=pesan_final,

                    wait_time=10,

                    tab_close=True,

                    close_time=5
                )

                total_terkirim += 1

                print(
                    f"Berhasil ke {nama}"
                )

                # delay antar kandidat
                time.sleep(5)

            print("\n===================")
            print("SELESAI")
            print("===================\n")

            # =========================
            # SUCCESS MESSAGE
            # =========================

            success_message = (
                f"Pesan terkirim ke "
                f"{total_terkirim} kandidat"
            )

        except Exception as e:

            print(e)

            success_message = f"Error: {e}"

    return render_template(
        "index.html",
        success_message=success_message,
        template_pesan=template_pesan
    )


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    
    webbrowser.open("http://127.0.0.1:5000")

    app.run(
        debug=False
    )