import streamlit as st
import cv2
import numpy as np
import os
import pytesseract
from PIL import Image, ImageDraw, ImageFont

# Hubungkan Python ke software Tesseract Windows secara absolut
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Konfigurasi Halaman Utama Web Browser
st.set_page_config(page_title="VisionStudio Advanced Multimedia", layout="wide")

# Custom UI CSS Styling Premium Dark Studio
st.markdown("""
    <style>
        [data-testid="stSidebar"] { background-color: #0F0F11; }
        .stButton>button { width: 100%; background-color: #1F1F24; color: white; border: 1px solid #2D2D34; }
        .stButton>button:hover { background-color: #00ADB5; color: white; border: 1px solid #00ADB5; }
        h1, h2, h3 { color: #F5F5F7; }
        .reportview-container { background: #09090B; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ VisionStudio Advanced Multimedia Cloud")
st.caption("Platform Pengolahan Gambar, Video, OCR Text Extraction, & Crypto-Steganography")

# --- CORE FUNCTIONS (MESIN MULTIMEDIA RUMIT) ---

def apply_pigura(img_bgr, color_hex, thickness_pct):
    """Menambahkan frame/pigura profesional di sekeliling gambar"""
    h, w = img_bgr.shape[:2]
    thickness = int(min(h, w) * (thickness_pct / 100))
    # Konversi hex ke BGR
    color_hex = color_hex.lstrip('#')
    rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    bgr = (rgb[2], rgb[1], rgb[0])
    return cv2.copyMakeBorder(img_bgr, thickness, thickness, thickness, thickness, cv2.BORDER_CONSTANT, value=bgr)

def apply_steganography_encode(img_bgr, secret_message):
    """Menyisipkan pesan rahasia ke dalam bit gambar (LSB Steganography) - Anti Overflow"""
    secret_message += "#####" # Delimiter akhir pesan
    binary_secret = ''.join(format(ord(i), '08b') for i in secret_message)
    
    # Konversi sementara ke int32 agar operasi matematika bitwise tidak overflow
    flatten_img = img_bgr.flatten().astype(np.int32)
    
    if len(binary_secret) > len(flatten_img):
        return None
        
    for idx, bit in enumerate(binary_secret):
        flatten_img[idx] = (flatten_img[idx] & ~1) | int(bit)
        
    # Kembalikan lagi ke tipe data uint8 asli gambar setelah selesai
    return flatten_img.clip(0, 255).astype(np.uint8).reshape(img_bgr.shape)

def apply_steganography_decode(img_bgr):
    """Membaca pesan rahasia dari pixel gambar bit terendah"""
    flatten_img = img_bgr.flatten()
    binary_data = ""
    for pixel in flatten_img:
        binary_data += str(pixel & 1)
        
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_text = ""
    for byte in all_bytes:
        decoded_text += chr(int(byte, 2))
        if decoded_text.endswith("#####"):
            return decoded_text[:-5]
    return "Tidak ditemukan pesan rahasia yang valid."

def convert_image_to_ascii(img_bgr, cols=100):
    """Mengubah pixel gambar menjadi susunan karakter kata/ASCII (Kreatif)"""
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    aspect_ratio = h / w
    rows = int(cols * aspect_ratio * 0.55) # 0.55 penyesuaian font font tinggi
    small_img = cv2.resize(gray, (cols, rows))
    
    chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
    ascii_str = ""
    for row in small_img:
        for pixel in row:
            ascii_str += chars[pixel // 25]
        ascii_str += "\n"
    return ascii_str

# --- SIDEBAR INPUT PANEL ---
st.sidebar.header("🗂️ ASSET RESOURCE MANAGER")
uploaded_file = st.sidebar.file_uploader("Upload File Anda (Gambar/Video)", type=["png", "jpg", "jpeg", "mp4", "mov"])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    is_video = file_ext in [".mp4", ".mov"]

    # MEMBUAT TAMPILAN SCREEN WORKSPACE DENGAN TABS (DILIHAT DOSEN SANGAT RAPI)
    tab_editor, tab_stickers, tab_ocr, tab_stego, tab_ascii = st.tabs([
        "🎥 Photo & Video Processor", 
        "🎨 Frame & Emoticon", 
        "🔍 OCR Text Extractor", 
        "🔐 Steganography (Pesan Rahasia)", 
        "📝 Image To ASCII Word"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: PHOTO & VIDEO PROCESSOR
    # -------------------------------------------------------------------------
    with tab_editor:
        col_view, col_ctrl = st.columns([2, 1])
        
        if is_video:
            with col_view:
                st.subheader("Video Monitor Viewport")
                temp_video_path = "temp_web_video" + file_ext
                with open(temp_video_path, "wb") as f:
                    f.write(file_bytes)
                
                video_placeholder = st.empty()
                
            with col_ctrl:
                st.write("### Filter Video Layer")
                v_filter = st.selectbox("Pilih Filter Efek Video", ["Normal", "Soft Tone (Blur)", "Monochrome", "Negative Invert"])
                run_video = st.button("▶ Start Live Render Video Processing")
                
            if run_video:
                cap = cv2.VideoCapture(temp_video_path)
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret: break
                    
                    if v_filter == "Soft Tone (Blur)":
                        frame = cv2.GaussianBlur(frame, (15, 15), 0)
                    elif v_filter == "Monochrome":
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                    elif v_filter == "Negative Invert":
                        frame = cv2.bitwise_not(frame)
                        
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    video_placeholder.image(frame_rgb, use_container_width=True)
                cap.release()
        else:
            cv_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            with col_ctrl:
                st.write("### Image Adjustment Parameter")
                b_val = st.slider("☀️ Brightness / Kecerahan", -100, 100, 0)
                c_val = st.slider("🌗 Contrast / Kontras", -100, 100, 0)
                s_val = st.slider("🧪 Saturation / Saturasi Warna", -100, 100, 0)
                blur_val = st.slider("💧 Soft Tone (Gaussian Blur)", 0, 50, 0)
                
                show_hist = st.checkbox("📊 Tampilkan Histogram Analisis Gambar")

            # Kalkulasi Manipulasi Matrix Pixel
            # Brightness & Contrast
            adjusted = cv2.convertScaleAbs(cv_img.copy(), alpha=1.0 + (c_val/100.0), beta=b_val)
            # Saturation
            if s_val != 0:
                hsv = cv2.cvtColor(adjusted, cv2.COLOR_BGR2HSV).astype("float32")
                h, s, v = cv2.split(hsv)
                s = np.clip(s + s_val, 0, 255)
                adjusted = cv2.cvtColor(cv2.merge([h, s, v]).astype("uint8"), cv2.COLOR_HSV2BGR)
            # Blur
            if blur_val > 0:
                if blur_val % 2 == 0: blur_val += 1
                adjusted = cv2.GaussianBlur(adjusted, (blur_val, blur_val), 0)

            with col_view:
                st.image(cv2.cvtColor(adjusted, cv2.COLOR_BGR2RGB), caption="Output Monitor Viewport", use_container_width=True)
                
                if show_hist:
                    st.write("#### Live Histogram Channel Analysis")
                    hist_data = {}
                    for i, col in enumerate(['B', 'G', 'R']):
                        hist = cv2.calcHist([adjusted], [i], None, [256], [0, 256])
                        hist_data[col] = hist.flatten()
                    st.line_chart(hist_data)

    # -------------------------------------------------------------------------
    # TAB 2: FRAME & EMOTICON (PIGURA & STICKER) - FIXED FOR EMOJI PNG
    # -------------------------------------------------------------------------
    with tab_stickers:
        if is_video:
            st.warning("Fitur Pigura & Emoticon saat ini hanya dioptimalkan untuk aset format foto statis.")
        else:
            col_view2, col_ctrl2 = st.columns([2, 1])
            with col_ctrl2:
                st.write("### Frame Designer & Overlays")
                use_frame = st.checkbox("Aktifkan Pigura Borders")
                frame_color = st.color_picker("Warna Pigura", "#00ADB5")
                frame_thick = st.slider("Ketebalan Bingkai (%)", 1, 15, 5)
                
                st.write("### Add Text Emoticon Stamp")
                # Menggunakan ID Kode Hex Emoji resmi Twemoji
                emoticon_select = st.selectbox(
                    "Pilih Emoticon", 
                    ["😊 Happy Face", "🔥 Fire Bold", "❤️ Love Heart", "👑 Crown King", "⭐ Star Light"]
                )
                
                # Mapping pilihan ke kode unicode hex resmi untuk diunduh otomatis
                emoji_mapping = {
                    "😊 Happy Face": "1f60a",
                    "🔥 Fire Bold": "1f525",
                    "❤️ Love Heart": "2764",
                    "👑 Crown King": "1f451",
                    "⭐ Star Light": "2b50"
                }
                
                selected_hex = emoji_mapping[emoticon_select]
                emo_size = st.slider("Ukuran Emoticon Teks", 20, 200, 80)
                pos_x = st.slider("Koordinat Posisi X", 0, cv_img.shape[1], int(cv_img.shape[1]/2))
                pos_y = st.slider("Koordinat Posisi Y", 0, cv_img.shape[0], int(cv_img.shape[0]/2))
            
            with col_view2:
                img_result = cv_img.copy()
                if use_frame:
                    img_result = apply_pigura(img_result, frame_color, frame_thick)
                
                # Konversi hasil OpenCV ke PIL Image
                pil_img = Image.fromarray(cv2.cvtColor(img_result, cv2.COLOR_BGR2RGB))
                
                # Mengunduh aset gambar PNG emoji secara real-time dari repository resmi Twemoji
                emoji_url = f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{selected_hex}.png"
                
                try:
                    import urllib.request
                    # Simpan emoji sementara
                    emoji_path = f"temp_{selected_hex}.png"
                    if not os.path.exists(emoji_path):
                        urllib.request.urlretrieve(emoji_url, emoji_path)
                    
                    # Buka gambar emoji dan ubah ukurannya sesuai slider
                    emoji_img = Image.open(emoji_path).convert("RGBA")
                    emoji_img = emoji_img.resize((emo_size, emo_size), Image.Resampling.LANCZOS)
                    
                    # Tempelkan gambar emoji di atas foto utama (mendukung transparansi)
                    pil_img.paste(emoji_img, (pos_x, pos_y), emoji_img)
                except Exception as e:
                    # Fallback jika koneksi server gagal, tampilkan teks penanda biasa
                    draw = ImageDraw.Draw(pil_img)
                    draw.text((pos_x, pos_y), "[Sticker]", fill=(255, 255, 255))
                
                st.image(pil_img, caption="Hasil Kreasi Custom Overlay & Pigura", use_container_width=True)
                
                # Sediakan tombol download hasil modifikasi
                buffered = np.array(pil_img)
                final_bgr = cv2.cvtColor(buffered, cv2.COLOR_RGB2BGR)
                is_success, buffer = cv2.imencode(".png", final_bgr)
                if is_success:
                    st.download_button(
                        label="💾 Download Hasil Modifikasi Stiker",
                        data=buffer.tobytes(),
                        file_name="vision_studio_sticker.png",
                        mime="image/png"
                    )

    # -------------------------------------------------------------------------
    # TAB 3: OCR TEXT EXTRACTOR (DETEKSI TEKS ASLI)
    # -------------------------------------------------------------------------
    with tab_ocr:
        st.subheader("🚀 Ekstraksi Teks Otomatis dari Gambar (OCR)")
        
        if st.button("🔍 Jalankan Ekstraksi Deteksi Teks Sekarang"):
            if cv_img is not None:
                with st.spinner("Sedang membaca teks pada gambar..."):
                    try:
                        # Konversi OpenCV BGR ke PIL RGB
                        pil_img_ocr = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
                        
                        # Eksekusi ekstraksi teks asli menggunakan Tesseract
                        teks_hasil = pytesseract.image_to_string(pil_img_ocr, lang='ind+eng')
                        
                        if teks_hasil.strip():
                            st.success("Teks Berhasil Diekstrak!")
                            # Menampilkan teks asli hasil pembacaan gambar dokumen
                            st.text_area("Hasil Ekstraksi Teks Asli:", value=teks_hasil, height=300)
                        else:
                            st.warning("Gambar berhasil dibaca, namun engine tidak mendeteksi karakter teks yang jelas.")
                            
                    except Exception as e:
                        st.error(f"Gagal mengeksekusi OCR. Periksa kembali instalasi Tesseract di laptopmu. Error: {e}")
            else:
                st.error("Silakan unggah file gambar terlebih dahulu di sidebar kiri!")
    # -------------------------------------------------------------------------
    # TAB 4: CRYPTO-STEGANOGRAPHY (PENYISIPAN PESAN RAHASIA)
    # -------------------------------------------------------------------------
    with tab_stego:
        st.subheader("🔐 Kripto-Steganografi: Menyembunyikan Kata Rahasia ke Dalam Piksel")
        st.info("Pesan rahasia akan disisipkan ke dalam kode biner piksel gambar terendah (LSB), sehingga secara kasat mata gambar tidak akan mengalami perubahan warna sama sekali.")
        
        mode_stego = st.radio("Pilih Operasi Lab", ["Encode (Sembunyikan Pesan)", "Decode (Pecahkan/Baca Pesan Rahasia)"])
        
        if mode_stego == "Encode (Sembunyikan Pesan)":
            if is_video:
                st.warning("Silakan gunakan aset Foto untuk melakukan proses penyisipan pesan teks rahasia.")
            else:
                pesan_input = st.text_input("Ketik Kata/Kalimat Rahasia yang Ingin Disisipkan:")
                if st.button("🔒 Amankan & Enkripsi ke Gambar"):
                    if pesan_input:
                        stego_img = apply_steganography_encode(cv_img, pesan_input)
                        if stego_img is not None:
                            st.success("Pesan Berhasil Disembunyikan ke dalam matriks piksel gambar!")
                            st.image(cv2.cvtColor(stego_img, cv2.COLOR_BGR2RGB), caption="Gambar Stego (Terlihat normal, tapi mengandung pesan rahasia)", use_container_width=True)
                            
                            # Konversi ke bytes untuk di-download
                            is_success, buffer = cv2.imencode(".png", stego_img)
                            st.download_button("💾 Download Hasil Gambar Stego (.PNG wajib)", data=buffer.tobytes(), file_name="stego_image_protected.png", mime="image/png")
                        else:
                            st.error("Ukuran teks rahasia terlalu besar dibandingkan dengan resolusi piksel gambar penampung.")
                    else:
                        st.warning("Isi pesan rahasia tidak boleh kosong.")
                        
        elif mode_stego == "Decode (Pecahkan/Baca Pesan Rahasia)":
            if is_video:
                st.warning("Gunakan file foto hasil download stego untuk memecahkan pesan.")
            else:
                if st.button("🔓 Jalankan Ekstraksi Bit Analisis (Pecahkan Sandi)"):
                    with st.spinner("Sedang melacak bit biner piksel gambar..."):
                        pesan_terbongkar = apply_steganography_decode(cv_img)
                        st.write("### Isi Pesan yang Berhasil Ditemukan:")
                        st.code(pesan_terbongkar, language="text")

    # -------------------------------------------------------------------------
    # TAB 5: IMAGE TO ASCII WORD (PERUBAHAN GAMBAR MENJADI KATA)
    # -------------------------------------------------------------------------
    with tab_ascii:
        if is_video:
            st.warning("Fitur konversi seni karakter kata dioptimalkan khusus untuk file foto.")
        else:
            st.subheader("📝 Mengubah Tekstur Piksel Gambar Menjadi Susunan Karakter Kata ASCII")
            lebar_karakter = st.slider("Kerapatan Kolom Karakter Kata", 50, 200, 100)
            
            if st.button("🎨 Konversi Gambar Menjadi Kata/ASCII Art"):
                ascii_art = convert_image_to_ascii(cv_img, cols=lebar_karakter)
                # KODE YANG SUDAH DIPERBAIKI TOTAL (TANPA PARAMETER TYPO):
                st.text_area("Output Struktur Kata Seni Gambar (Gunakan Zoom Out jika teks terpotong):", value=ascii_art, height=450)
                st.success("Seni Gambar Kata Selesai Dibuat!")
else:
    st.info("Silakan import asset foto atau video Anda di panel sebelah kiri untuk memuat dashboard studio multimedia.")