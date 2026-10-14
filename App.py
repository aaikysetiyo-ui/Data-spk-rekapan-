import os
import json
import base64
import streamlit as st
from datetime import datetime

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Arsip & Data SPK Asuransi",
    page_icon="📄",
    layout="wide",
)

# File penyimpanan lokal untuk data SPK
DATA_FILE = "spk_database.json"
UPLOAD_DIR = "uploaded_spk_files"

# Pastikan folder upload ada
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Load data awal
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.loadf(f)
        except:
            pass
    
    # Default Dummy Data jika file kosong
    return [
        {
            "id": 1,
            "no_spk": "SPK/2027/001",
            "plat_nomor": "B 1234 SKP",
            "tertanggung": "PT Sentosa Abadi",
            "jenis": "Kendaraan Comprehensive",
            "tahun": "2027",
            "bulan": "Januari",
            "status": "Aktif",
            "file_name": "SPK_B1234SKP_Jan2027.pdf",
            "file_path": None
        },
        {
            "id": 2,
            "no_spk": "SPK/2027/002",
            "plat_nomor": "D 8888 RFS",
            "tertanggung": "Budi Santoso",
            "jenis": "Total Loss Only (TLO)",
            "tahun": "2027",
            "bulan": "Januari",
            "status": "Proses",
            "file_name": "SPK_D8888RFS_Jan2027.pdf",
            "file_path": None
        },
        {
            "id": 3,
            "no_spk": "SPK/2025/112",
            "plat_nomor": "B 5543 NIK",
            "tertanggung": "Dewi Lestari",
            "jenis": "Total Loss Only (TLO)",
            "tahun": "2025",
            "bulan": "Desember",
            "status": "Klaim",
            "file_name": "SPK_B5543NIK_Des2025.pdf",
            "file_path": None
        }
    ]

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "spk_list" not in st.session_state:
    st.session_state.spk_list = load_data()

MONTHS = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
YEARS = ["2025", "2026", "2027"]

# --- HEADER APLIKASI ---
st.title("📄 Arsip & Manajemen SPK Asuransi")
st.markdown("Kelola dokumen SPK, folder arsip tahun 2025-2027, plat nomor kendaraan, serta pratinjau PDF.")
st.markdown("---")

# --- SIDEBAR: INPUT & UPLOAD SPK BARU ---
st.sidebar.header("📥 Upload / Input SPK Baru")
with st.sidebar.form("form_upload_spk", clear_on_submit=True):
    no_spk = st.text_input("Nomor SPK", placeholder="Contoh: SPK/2027/005")
    plat_nomor = st.text_input("Plat Nomor Kendaraan", placeholder="Contoh: B 1234 ABC").upper()
    tertanggung = st.text_input("Nama Tertanggung / Pemilik")
    jenis = st.selectbox("Jenis Asuransi", ["Kendaraan Comprehensive", "Total Loss Only (TLO)", "Asuransi Jiwa & Kesehatan", "Properti & Kebakaran"])
    status = st.selectbox("Status SPK", ["Aktif", "Proses", "Klaim"])
    
    col_y, col_m = st.columns(2)
    with col_y:
        tahun = st.selectbox("Tahun Folder", YEARS, index=2) # Default 2027
    with col_m:
        bulan = st.selectbox("Bulan Folder", MONTHS)
        
    uploaded_file = st.file_uploader("Upload File Berkas PDF SPK", type=["pdf"])
    
    submit_btn = st.form_submit_button("Simpan Berkas SPK")
    
    if submit_btn:
        if not no_spk or not plat_nomor or not tertanggung:
            st.sidebar.error("Nomor SPK, Plat Nomor, dan Nama Tertanggung wajib diisi!")
        else:
            file_path = None
            file_name = f"{no_spk.replace('/', '_')}_{plat_nomor.replace(' ', '')}.pdf"
            
            if uploaded_file is not None:
                file_name = uploaded_file.name
                file_path = os.path.join(UPLOAD_DIR, file_name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            new_record = {
                "id": int(datetime.now().timestamp()),
                "no_spk": no_spk,
                "plat_nomor": plat_nomor,
                "tertanggung": tertanggung,
                "jenis": jenis,
                "tahun": tahun,
                "bulan": bulan,
                "status": status,
                "file_name": file_name,
                "file_path": file_path
            }
            
            st.session_state.spk_list.insert(0, new_record)
            save_data(st.session_state.spk_list)
            st.sidebar.success(f"Berkas SPK {no_spk} berhasil disimpan!")
            st.rerun()

# --- STATISTIK RINGKASAN ---
total_berkas = len(st.session_state.spk_list)
count_2025 = sum(1 for x in st.session_state.spk_list if x["tahun"] == "2025")
count_2026 = sum(1 for x in st.session_state.spk_list if x["tahun"] == "2026")
count_2027 = sum(1 for x in st.session_state.spk_list if x["tahun"] == "2027")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Berkas SPK", total_berkas)
c2.metric("Arsip 2025", count_2025)
c3.metric("Arsip 2026", count_2026)
c4.metric("Folder Baru 2027", count_2027)

st.markdown("---")

# --- NAVIGASI TAHUN & FOLDER BULAN ---
selected_year = st.radio("Pilih Folder Tahun:", YEARS, horizontal=True, index=2)

st.markdown(f"**Pilih Folder Bulan untuk Tahun {selected_year}:**")
month_cols = st.columns(6)
selected_month = st.session_state.get("selected_month", None)

for i, m in enumerate(MONTHS):
    col_idx = i % 6
    count_m = sum(1 for x in st.session_state.spk_list if x["tahun"] == selected_year and x["bulan"] == m)
    label = f"📁 {m} ({count_m})"
    
    with month_cols[col_idx]:
        is_active = (selected_month == m)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"btn_m_{m}", use_container_width=True, type=btn_type):
            if st.session_state.get("selected_month") == m:
                st.session_state.selected_month = None # Toggle off
            else:
                st.session_state.selected_month = m
            st.rerun()

if st.session_state.get("selected_month"):
    st.info(f"Menampilkan filter aktif untuk Bulan: **{st.session_state.selected_month} {selected_year}**")
    if st.button("Reset Filter Bulan"):
        st.session_state.selected_month = None
        st.rerun()

st.markdown("---")

# --- PENCARIAN & FILTER TABEL ---
col_search, col_status = st.columns([3, 1])
with col_search:
    search_query = st.text_input("🔍 Cari No. SPK, Plat Nomor, Nama Tertanggung, atau Asuransi", "")
with col_status:
    status_filter = st.selectbox("Filter Status", ["Semua", "Aktif", "Proses", "Klaim"])

# Filter Logic
filtered_list = []
for item in st.session_state.spk_list:
    if item["tahun"] != selected_year:
        continue
    if st.session_state.get("selected_month") and item["bulan"] != st.session_state.get("selected_month"):
        continue
    if status_filter != "Semua" and item["status"] != status_filter:
        continue
    
    q = search_query.lower()
    if q and not (q in item["no_spk"].lower() or q in item["plat_nomor"].lower() or q in item["tertanggung"].lower() or q in item["jenis"].lower()):
        continue
        
    filtered_list.append(item)

st.subheader(f"Daftar SPK ({len(filtered_list)} Berkas ditemukan)")

# --- TABEL DATA ---
for item in filtered_list:
    with st.container():
        cols = st.columns([2, 2, 2, 2, 1, 1, 1])
        with cols[0]:
            st.markdown(f"**{item['no_spk']}**")
            st.caption(f"{item['bulan']} {item['tahun']}")
        with cols[1]:
            st.code(item['plat_nomor'], language=None)
        with cols[2]:
            st.write(item['tertanggung'])
        with cols[3]:
            st.write(item['jenis'])
        with cols[4]:
            if item['status'] == 'Aktif':
                st.success(item['status'])
            elif item['status'] == 'Proses':
                st.warning(item['status'])
            else:
                st.error(item['status'])
        with cols[5]:
            # Tombol Pratinjau / Download PDF
            if st.button("👁️ Lihat PDF", key=f"view_{item['id']} data"):
                st.session_state.active_pdf = item
        with cols[6]:
            if st.button("🗑️ Hapus", key=f"del_{item['id']}"):
                st.session_state.spk_list = [x for x in st.session_state.spk_list if x["id"] != item["id"]]
                save_data(st.session_state.spk_list)
                st.success("Berhasil dihapus!")
                st.rerun()
        st.divider()

# --- MODAL / AREA PRATINJAU PDF ---
if "active_pdf" in st.session_state and st.session_state.active_pdf:
    item = st.session_state.active_pdf
    st.markdown("---")
    col_p1, col_p2 = st.columns([4, 1])
    with col_p1:
        st.subheader(f"Pratinjau Dokumen SPK: {item['no_spk']}")
    with col_p2:
        if st.button("Tutup Pratinjau"):
            st.session_state.active_pdf = None
            st.rerun()
            
    # Jika file asli ada di server, tampilkan, jika tidak tampilkan simulasi
    if item['file_path'] and os.path.exists(item['file_path']):
        with open(item['file_path'], "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        # Tampilkan Simulasi Dokumen Resmi SPK
        st.markdown(f"""
        <div style="background-color: white; padding: 30px; border-radius: 10px; border: 1px solid #ddd; color: #333;">
            <h2 style="color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px;">SURAT PERMINTAAN KENDARAAN (SPK)</h2>
            <p><b>Nomor SPK:</b> {item['no_spk']}</p>
            <p><b>Plat Nomor Kendaraan:</b> <span style="background: #0f172a; color: white; padding: 4px 8px; border-radius: 4px; font-family: monospace;">{item['plat_nomor']}</span></p>
            <p><b>Nama Tertanggung:</b> {item['tertanggung']}</p>
            <p><b>Jenis Asuransi:</b> {item['jenis']}</p>
            <p><b>Periode Arsip:</b> {item['bulan']} {item['tahun']}</p>
            <p><b>Status Polis:</b> {item['status']}</p>
            <hr style="margin: 20px 0;">
            <p style="font-size: 12px; color: #666;">Dokumen ini adalah simulasi digital arsip SPK Asuransi resmi yang tersimpan di sistem.</p>
        </div>
        """, unsafe_allow_html=True)
