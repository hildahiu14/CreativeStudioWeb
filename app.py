import streamlit as st
import cv2
import numpy as np
import os
from modules import filter_engine

# Konfigurasi Halaman Utama Web Browser
st.set_page_config(page_title="VisionStudio Creative Cloud", layout="wide")

# Custom UI CSS Styling agar Sidebar terlihat premium dan elegan
st.markdown("""
    <style>
        [data-testid="stSidebar"] { background-color: #121214; }
        .stButton>button { width: 100%; background-color: #1F1F24; color: white; border: 1px solid #2D2D34; }
        .stButton>button:hover { background-color: #00ADB5; color: white; border: 1px solid #00ADB5; }
        h1, h2, h3 { color: #F5F5F7; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ VisionStudio Creative Cloud")
st.caption("Aplikasi Produksi Multimedia Foto & Video Berbasis Web")

# --- SIDEBAR KONTROL PANEL (INSPECTOR KIRI) ---
st.sidebar.header("🎛️ STUDIO INSPECTOR")

# Komponen 1: Upload File Multimedia (Foto atau Video)
uploaded_file = st.sidebar.file_uploader("Import Source Asset", type=["png", "jpg", "jpeg", "mp4", "mov", "avi"])

# Setup Workspace Grid Kolom (Kolom Kiri untuk Tampilan, Kolom Kanan untuk Kontrol Parameter)
col_display, col_controls = st.columns([2, 1])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    is_video = file_ext in [".mp4", ".mov", ".avi"]
    
    # --- PROSES UNTUK ASSET VIDEO ---
    if is_video:
        with col_display:
            st.subheader("🎥 Source Monitor (Video Viewport)")
            # Simpan file sementara agar bisa dibaca stream oleh OpenCV
            temp_video_path = "temp_uploaded_video" + file_ext
            with open(temp_video_path, "wb") as f:
                f.write(file_bytes)
                
            # Kontrol pilihan filter video di kolom kanan
            with col_controls:
                st.write("### 🎬 Video Effect Layer")
                chosen_filter = st.selectbox("Pilih Preset Filter Video", 
                                             ["Original Normal", "Monochrome", "Warm Sepia", "Vintage Film", "Cyberpunk Neon"])
            
            # Membaca stream frame video menggunakan OpenCV
            cap = cv2.VideoCapture(temp_video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Tempat penampung frame video di web browser
            video_placeholder = col_display.empty()
            
            # Tombol pemicu pemrosesan video render
            if st.button("Render & Play Video Effect"):
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Terapkan filter pilihan user secara real-time pada frame video
                    if chosen_filter == "Monochrome":
                        frame = filter_engine.apply_grayscale(frame)
                    elif chosen_filter == "Warm Sepia":
                        frame = filter_engine.apply_sepia(frame)
                    elif chosen_filter == "Vintage Film":
                        frame = filter_engine.apply_vintage_vignette(frame)
                    elif chosen_filter == "Cyberpunk Neon":
                        frame = filter_engine.apply_cyberpunk(frame)
                        
                    # Konversi warna BGR ke RGB agar didukung browser
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                cap.release()
                
    # --- PROSES UNTUK ASSET FOTO ---
    else:
        cv_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        with col_controls:
            # Menu Tab seperti CapCut Web
            tab_preset, tab_adjust, tab_geom = st.tabs(["🎨 Presets", "☀️ Adjust", "↔️ Geometry"])
            
            with tab_preset:
                preset = st.radio("Pilih Preset Filter", 
                                  ["Normal", "Monochrome", "Warm Sepia", "Vintage Film", "Cyberpunk Neon", "X-Ray Invert", "Pencil Sketch", "Pop Cartoon"])
            
            with tab_adjust:
                b_val = st.slider("☀️ Brightness", -100, 100, 0)
                c_val = st.slider("🌗 Contrast", -100, 100, 0)
                s_val = st.slider("🧪 Saturation", -100, 100, 0)
                blur_val = st.slider("💧 Gaussian Blur", 0, 50, 0)
                
            with tab_geom:
                rotate_clicks = st.number_input("🔄 Rotasi (Kelipatan 90°)", min_value=0, max_value=3, value=0)
                flip_h = st.checkbox("↔️ Flip Horizontal (Mirror)")
                flip_v = st.checkbox("↕️ Flip Vertical")

        # --- JALUR PIPELINE PEMROSESAN EFEK FOTO ---
        processed_img = filter_engine.adjust_light_and_color(cv_img.copy(), b_val, c_val, s_val)
        
        if blur_val > 0:
            processed_img = filter_engine.apply_blur(processed_img, blur_val)
            
        if preset == "Monochrome": processed_img = filter_engine.apply_grayscale(processed_img)
        elif preset == "Warm Sepia": processed_img = filter_engine.apply_sepia(processed_img)
        elif preset == "Vintage Film": processed_img = filter_engine.apply_vintage_vignette(processed_img)
        elif preset == "Cyberpunk Neon": processed_img = filter_engine.apply_cyberpunk(processed_img)
        elif preset == "X-Ray Invert": processed_img = filter_engine.apply_invert(processed_img)
        elif preset == "Pencil Sketch": processed_img = filter_engine.apply_pencil_sketch(processed_img)
        elif preset == "Pop Cartoon": processed_img = filter_engine.apply_cartoon(processed_img)

        for _ in range(rotate_clicks):
            processed_img = filter_engine.rotate_90(processed_img)
        if flip_h: processed_img = filter_engine.flip_image(processed_img, "horizontal")
        if flip_v: processed_img = filter_engine.flip_image(processed_img, "vertical")

        # Konversi warna BGR ke RGB untuk render halaman web
        processed_rgb = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
        
        with col_display:
            st.subheader("🖼️ Source Monitor (Photo Viewport)")
            st.image(processed_rgb, use_container_width=True)
            
            # Fitur Download instan lewat web browser tanpa terminal
            is_success, buffer = cv2.imencode(".png", processed_img)
            if is_success:
                st.download_button(
                    label="💾 Export Result (Download Photo)",
                    data=buffer.tobytes(),
                    file_name="vision_studio_export.png",
                    mime="image/png"
                )
else:
    with col_display:
        st.info("Silakan import asset foto atau video Anda di panel sebelah kiri untuk memulai editing studio.")