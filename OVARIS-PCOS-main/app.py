import streamlit as st
import pandas as pd
import numpy as np
import io

# Pustaka untuk Export PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# =========================================================================
# 1. KONFIGURASI HALAMAN & CUSTOM CSS MODERN
# =========================================================================
st.set_page_config(
    page_title="Skrining Kesehatan PraLansia",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Design CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #f3e8ff 100%);
    }

    .login-container {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #ec4899 100%);
        border-radius: 28px;
        padding: 40px;
        box-shadow: 0 20px 40px rgba(79, 70, 229, 0.25);
        color: white;
        text-align: center;
    }
    
    .login-card {
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(16px);
        border-radius: 24px;
        padding: 35px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.8);
    }

    .header-banner {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        padding: 25px 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2);
    }
    
    .header-banner h1 {
        color: white !important;
        font-weight: 800;
        margin: 0;
        font-size: 2.2rem;
    }
    
    .header-banner p {
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 5px 0 0 0;
        font-size: 1rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre;
        border-radius: 12px;
        font-weight: 600;
        color: #64748b;
        padding: 0px 20px;
        background-color: transparent;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    .metric-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 22px 25px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04);
        border: 2px solid transparent;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(99, 102, 241, 0.15);
    }

    .card-1 { border-image: linear-gradient(135deg, #3b82f6, #60a5fa) 1; }
    .card-2 { border-image: linear-gradient(135deg, #a855f7, #c084fc) 1; }
    .card-3 { border-image: linear-gradient(135deg, #f59e0b, #fbbf24) 1; }

    .metric-title {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        color: #0f172a;
        font-size: 2.2rem;
        font-weight: 800;
        margin-top: 5px;
    }

    .content-box {
        background: #ffffff;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.03);
        border: 1px solid #e2e8f0;
        margin-top: 15px;
        margin-bottom: 20px;
    }

    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        color: white !important;
        border: none;
        padding: 0.65rem 1.4rem;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.25);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
    }

    .patient-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #6366f1;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .patient-card-high { border-left-color: #ef4444; }
    .patient-card-med { border-left-color: #f59e0b; }
    .patient-card-low { border-left-color: #10b981; }

    .badge-rank {
        background: linear-gradient(135deg, #4f46e5, #3b82f6);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Helper Function: Render Tabel Berwarna
def render_styled_table(df):
    styled = df.style.set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#4f46e5'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center'), ('padding', '12px')]},
        {'selector': 'td', 'props': [('text-align', 'center'), ('padding', '10px')]},
        {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f8fafc')]},
        {'selector': 'tr:nth-child(odd)', 'props': [('background-color', '#ffffff')]},
        {'selector': 'tr:hover', 'props': [('background-color', '#e0e7ff')]}
    ])
    st.write(styled.to_html(), unsafe_allow_html=True)

# Helper Function: Generator Rekomendasi Medis & Pola Hidup
def get_recommendations(pasien):
    skrining = []
    pola_hidup = []
    
    if pasien["Tekanan_Darah"] >= 140 or pasien["Riwayat_TD"] == "Ada":
        skrining.append("Skrining Fungsi Jantung (EKG) untuk evaluasi risiko kardiovaskular.")
        skrining.append("Pemeriksaan Profil Lipid Lengkap (Kolesterol Total, LDL, HDL, Trigliserida).")
    else:
        skrining.append("Monitoring Tekanan Darah rutin berkala 1 bulan sekali.")
        skrining.append("Pemeriksaan Kolesterol Rutin tiap 6 bulan.")
        
    if pasien["Gula_Darah"] >= 140:
        skrining.append("Pemeriksaan HbA1c & Gula Darah Puasa untuk evaluasi diabetes melitus.")
    else:
        skrining.append("Skrining Gula Darah Sewaktu berkala per 3 bulan.")
        
    if pasien["IMT"] in ["Obesitas I", "Obesitas II", "Berat Badan Lebih"]:
        skrining.append("Analisis Komposisi Tubuh & Lemak Viseral dengan Ahli Gizi.")
    else:
        skrining.append("Evaluasi Lingkar Pinggang & IMT rutin setiap bulan.")
        
    skrining.append("Pemeriksaan Retinometri / Kesehatan Mata Pasien Pralansia.")
    
    if pasien["Tekanan_Darah"] >= 140:
        pola_hidup.append("Diet Rendah Garam (DASH): Batasi konsumsi natrium maksimal 1 sdt/hari.")
    else:
        pola_hidup.append("Nutrisi Seimbang: Tingkatkan asupan serat dari sayur dan buah segar.")

    if pasien["Gula_Darah"] >= 140:
        pola_hidup.append("Batasi Gula Sederhana: Hindari minuman manis dan karbohidrat olahan berlebih.")
    
    if pasien["IMT"] in ["Obesitas I", "Obesitas II", "Berat Badan Lebih"]:
        pola_hidup.append("Aktivitas Fisik Aerobik: Jalan cepat/senam pralansia 30 menit/hari (min. 5x seminggu).")
    else:
        pola_hidup.append("Tetap Aktif: Pertahankan aktivitas fisik ringan hingga sedang secara konsisten.")
        
    pola_hidup.append("Istirahat Cukup: Tidur teratur 7-8 jam per malam dan kendalikan stres.")
    pola_hidup.append("Hidrasi Optimal: Konsumsi air putih minimal 1.5 - 2 liter sehari.")

    return skrining[:5], pola_hidup

# =========================================================================
# GENERATOR EXPORT PDF (REPORTLAB)
# =========================================================================
def generate_single_pdf(pasien, rank):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#4f46e5"), spaceAfter=6)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#64748b"), spaceAfter=12)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor("#1e293b"), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=13)
    
    elements = []
    
    elements.append(Paragraph("LAPORAN REKOMENDASI MEDIS PRALANSIA", title_style))
    elements.append(Paragraph("Posyandu / Layanan Kesehatan Pralansia • Hasil Analisis Electre dan TOPSIS", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4f46e5"), spaceAfter=15))
    
    data_info = [
        [Paragraph("<b>Nama Pasien:</b>", body_style), Paragraph(pasien["Nama"], body_style), Paragraph("<b>Peringkat Prioritas:</b>", body_style), Paragraph(f"<b>Rank #{rank}</b>", body_style)],
        [Paragraph("<b>NIK:</b>", body_style), Paragraph(pasien["NIK"], body_style), Paragraph("<b>Skor Preferensi:</b>", body_style), Paragraph(str(pasien["Skor"]), body_style)],
        [Paragraph("<b>Umur:</b>", body_style), Paragraph(f"{pasien['Umur']} Tahun", body_style), Paragraph("<b>IMT Status:</b>", body_style), Paragraph(pasien["IMT"], body_style)],
        [Paragraph("<b>Tekanan Darah:</b>", body_style), Paragraph(f"{pasien['Tekanan_Darah']} mmHg", body_style), Paragraph("<b>Gula Darah:</b>", body_style), Paragraph(f"{pasien['Gula_Darah']} mg/dL", body_style)]
    ]
    
    t_info = Table(data_info, colWidths=[100, 160, 110, 150])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 15))
    
    skrining, pola_hidup = get_recommendations(pasien)
    
    elements.append(Paragraph("<b>5 Rekomendasi Skrining Medis Lanjutan:</b>", heading_style))
    for i, s in enumerate(skrining, 1):
        elements.append(Paragraph(f"{i}. {s}", body_style))
        
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Panduan Intervensi Pola Hidup Sehat:</b>", heading_style))
    for i, ph in enumerate(pola_hidup, 1):
        elements.append(Paragraph(f"{i}. {ph}", body_style))
        
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_all_pdf(pasien_ranked):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#4f46e5"), spaceAfter=6)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#64748b"), spaceAfter=12)
    
    elements = []
    elements.append(Paragraph("REKAPITULASI PRIORITY RANKING PRALANSIA", title_style))
    elements.append(Paragraph(f"Total Pasien: {len(pasien_ranked)} Orang | Metode ELECTRE & TOPSIS", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4f46e5"), spaceAfter=15))
    
    table_data = [["Rank", "Nama Pasien", "NIK", "Umur", "TD", "GDS", "IMT", "Skor"]]
    for i, p in enumerate(pasien_ranked, 1):
        table_data.append([
            str(i), p["Nama"], p["NIK"], f"{p['Umur']} Thn", 
            f"{p['Tekanan_Darah']}", f"{p['Gula_Darah']}", p["IMT"], str(p["Skor"])
        ])
        
    t_rekap = Table(table_data, colWidths=[35, 100, 110, 50, 50, 50, 80, 45])
    t_rekap.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4f46e5")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTFLAGS', (0,0), (-1,0), 'BOLD'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    
    elements.append(t_rekap)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# =========================================================================
# 2. STATE MANAGEMENT & DATA USERS (LOGIN PERSISTENT)
# =========================================================================
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": "admin123",
        "petugas": "petugas123"
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""

if "data_pralansia" not in st.session_state:
    st.session_state.data_pralansia = [
        {"NIK": "1234567890123456", "Nama": "Ahmad", "Umur": 55, "IMT": "Normal", "Riwayat_TD": "Ada", "Tekanan_Darah": 145, "Gula_Darah": 120},
        {"NIK": "1234567890123457", "Nama": "Budi", "Umur": 48, "IMT": "Normal", "Riwayat_TD": "Ada", "Tekanan_Darah": 150, "Gula_Darah": 110},
        {"NIK": "1234567890123458", "Nama": "Rina", "Umur": 50, "IMT": "Berat Badan Lebih", "Riwayat_TD": "Tidak Ada", "Tekanan_Darah": 120, "Gula_Darah": 210},
    ]

KRITERIA = {"C1": "Umur", "C2": "IMT", "C3": "Riwayat TD", "C4": "Tekanan Darah", "C5": "Gula Darah"}
BOBOT = {"C1": 0.15, "C2": 0.20, "C3": 0.25, "C4": 0.25, "C5": 0.15}

def nilai_sub_kriteria(p):
    c1 = 2 if p["Umur"] < 50 else (4 if p["Umur"] < 55 else 5)
    c2 = 2 if p["IMT"] == "Normal" else (3 if p["IMT"] == "Berat Badan Lebih" else (4 if p["IMT"] == "Obesitas I" else 5))
    c3 = 5 if p["Riwayat_TD"] == "Ada" else 2
    c4 = 2 if p["Tekanan_Darah"] < 130 else (4 if p["Tekanan_Darah"] < 140 else 5)
    c5 = 2 if p["Gula_Darah"] < 140 else (4 if p["Gula_Darah"] < 200 else 5)
    return [c1, c2, c3, c4, c5]

# =========================================================================
# 3. HALAMAN LOGIN MULTI-USER
# =========================================================================
if not st.session_state.logged_in:
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 1.3, 1])
    
    with col2:
        st.markdown("""
            <div class="login-container">
                <div style="font-size: 3.5rem; margin-bottom: 10px;">🏥</div>
                <h2 style="margin: 0; font-weight: 800; font-size: 2rem;">SPK PRALANSIA</h2>
                <p style="opacity: 0.9; font-size: 0.95rem; margin-top: 5px;">Sistem Pengambilan Keputusan Skrining Medis</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: -25px;'>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            with st.form("login_form"):
                st.markdown("<h4 style='color: #1e293b; font-weight: 700; margin-bottom: 15px;'>🔐 Masuk Ke Sistem</h4>", unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Masukkan username (cth: admin / petugas)")
                password = st.text_input("Password", type="password", placeholder="Masukkan password")
                
                st.write("")
                submit = st.form_submit_button("🚀 Masuk", use_container_width=True)
                
                if submit:
                    if username in st.session_state.users and st.session_state.users[username] == password:
                        st.session_state.logged_in = True
                        st.session_state.current_user = username
                        st.success(f"Selamat datang {username}!")
                        st.rerun()
                    else:
                        st.error("Username atau Password salah!")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================================
# 4. HALAMAN UTAMA (SETELAH LOGGED IN)
# =========================================================================
else:
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.markdown(f"""
            <div class="header-banner">
                <h1>🏥 Skrining Kesehatan Pra Lansia</h1>
                <p>Pengguna Aktif: <b>{st.session_state.current_user}</b> • Metode ELECTRE & TOPSIS</p>
            </div>
        """, unsafe_allow_html=True)
    with col_head2:
        st.write("")
        st.write("")
        if st.button("🚪 Keluar (Logout)", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.rerun()

    # TAB MANAJEMEN USER SUDAH DIHAPUS
    tabs = st.tabs([
        "🏠 Dashboard", 
        "👥 Data Pralansia", 
        "📊 Kriteria & Bobot", 
        "🧮 Perhitungan SPK", 
        "🏆 Hasil Ranking & Rekomendasi"
    ])

    # ---------------------------------------------------------------------
    # TAB 1: DASHBOARD
    # ---------------------------------------------------------------------
    with tabs[0]:
        st.markdown("### 📈 Ringkasan Statistik Utama")
        c1, c2, c3 = st.columns(3)
        total_p = len(st.session_state.data_pralansia)
        total_hipertensi = sum(1 for p in st.session_state.data_pralansia if p["Tekanan_Darah"] >= 140)
        
        with c1:
            st.markdown(f'<div class="metric-card card-1"><div class="metric-title">Total Pasien</div><div class="metric-value">{total_p}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card card-2"><div class="metric-title">Kriteria Medis</div><div class="metric-value">{len(KRITERIA)}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card card-3"><div class="metric-title">Risiko Hipertensi</div><div class="metric-value">{total_hipertensi}</div></div>', unsafe_allow_html=True)

        st.write("")
        col_dash1, col_dash2 = st.columns([2, 1])
        with col_dash1:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("#### 📥 Import Data Pasien dari Excel")
            st.write("Tambahkan data pasien pralansia dalam jumlah banyak menggunakan file spreadsheet Excel `.xlsx`.")
            uploaded = st.file_uploader("Upload File Excel", type=["xlsx"], key="dash_upload")
            if uploaded:
                try:
                    df_up = pd.read_excel(uploaded)
                    st.session_state.data_pralansia.extend(df_up.to_dict(orient="records"))
                    st.success("✅ Data berhasil di-import!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal membaca file: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_dash2:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("#### ⚙️ Opsi Pengaturan")
            st.write("Reset atau bersihkan database sementara pasien.")
            if st.button("🗑️ Hapus Semua Pasien", use_container_width=True):
                st.session_state.data_pralansia = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # TAB 2: DATA PRALANSIA
    # ---------------------------------------------------------------------
    with tabs[1]:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("### ➕ Form Input Data Pasien Baru")
        with st.form("form_add_pasien"):
            f1, f2 = st.columns(2)
            with f1:
                nik = st.text_input("NIK Pasien", max_chars=16)
                nama = st.text_input("Nama Lengkap")
                umur = st.number_input("Umur (Tahun)", min_value=30, max_value=80, value=50)
                imt = st.selectbox("Indeks Massa Tubuh (IMT)", ["Normal", "Berat Badan Lebih", "Obesitas I", "Obesitas II"])
            with f2:
                riwayat_td = st.selectbox("Riwayat Hipertensi", ["Tidak Ada", "Ada"])
                tekanan_darah = st.number_input("Tekanan Darah (mmHg)", min_value=80, max_value=220, value=120)
                gula_darah = st.number_input("Gula Darah Sewaktu (mg/dL)", min_value=50, max_value=500, value=110)
                
            if st.form_submit_button("💾 Simpan Pasien Baru", use_container_width=True):
                if nik and nama:
                    st.session_state.data_pralansia.append({
                        "NIK": nik, "Nama": nama, "Umur": umur, "IMT": imt,
                        "Riwayat_TD": riwayat_td, "Tekanan_Darah": tekanan_darah, "Gula_Darah": gula_darah
                    })
                    st.success("✅ Data Pasien Berhasil Disimpan!")
                    st.rerun()
                else:
                    st.warning("Mohon isi NIK dan Nama Pasien.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### 📋 Daftar Seluruh Pasien Pralansia")
        if st.session_state.data_pralansia:
            render_styled_table(pd.DataFrame(st.session_state.data_pralansia))

    # ---------------------------------------------------------------------
    # TAB 3: KRITERIA & BOBOT
    # ---------------------------------------------------------------------
    with tabs[2]:
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("### 📋 Daftar Kriteria Medis")
            render_styled_table(pd.DataFrame(list(KRITERIA.items()), columns=["Kode", "Nama Kriteria"]))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_k2:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("### ⚖️ Bobot Preferensi Kriteria")
            render_styled_table(pd.DataFrame([{"Kode": k, "Nama": KRITERIA[k], "Bobot": v} for k, v in BOBOT.items()]))
            st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # TAB 4: PERHITUNGAN SPK (DETAIL MANUAL - STEP BY STEP)
    # ---------------------------------------------------------------------
    with tabs[3]:
        st.markdown("### 🧮 Detail Perhitungan Langkah demi Langkah (Lengkap & Manual)")
        
        if len(st.session_state.data_pralansia) < 2:
            st.warning("⚠️ Minimal dibutuhkan 2 data pasien untuk menjalankan perhitungan ELECTRE & TOPSIS.")
        else:
            calc_tab1, calc_tab2 = st.tabs(["⚡ Detail Perhitungan ELECTRE", "📐 Detail Perhitungan TOPSIS"])
            
            # --- PREPARASI DATA ---
            names = [p["Nama"] for p in st.session_state.data_pralansia]
            X = np.array([nilai_sub_kriteria(p) for p in st.session_state.data_pralansia], dtype=float)
            w = np.array(list(BOBOT.values()))
            kriteria_keys = list(KRITERIA.keys())
            n_pasien = len(names)
            n_kriteria = len(kriteria_keys)

            # -------------------------------------------------------------
            # SUB-TAB 1: ELECTRE
            # -------------------------------------------------------------
            with calc_tab1:
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                
                # Langkah 1: Matriks Keputusan (X)
                st.markdown("#### 1. Matriks Keputusan ($X$)")
                st.caption("Hasil pemetaan kondisi medis pasien menjadi skor pembobotan sub-kriteria (skala 1-5).")
                df_X = pd.DataFrame(X, index=names, columns=kriteria_keys)
                render_styled_table(df_X)

                # Langkah 2: Matriks Ternormalisasi (R)
                st.markdown("#### 2. Matriks Ternormalisasi ($R$)")
                st.caption("Formula: $r_{ij} = \\frac{x_{ij}}{\\sqrt{\\sum_{i=1}^{m} x_{ij}^2}}$")
                pembagi = np.sqrt(np.sum(X**2, axis=0))
                pembagi[pembagi == 0] = 1
                R = X / pembagi
                df_R = pd.DataFrame(R.round(4), index=names, columns=kriteria_keys)
                render_styled_table(df_R)

                # Langkah 3: Matriks Ternormalisasi Terbobot (V)
                st.markdown("#### 3. Matriks Ternormalisasi Terbobot ($V$)")
                st.caption("Formula: $v_{ij} = w_j \\times r_{ij}$")
                V = R * w
                df_V = pd.DataFrame(V.round(4), index=names, columns=kriteria_keys)
                render_styled_table(df_V)

                # Langkah 4: Himpunan Concordance & Discordance
                st.markdown("#### 4. Himpunan Concordance ($C_{kl}$) & Discordance ($D_{kl}$)")
                st.caption("Membagi kriteria ke himpunan Unggul ($v_{kj} \\ge v_{lj}$) atau Lemah ($v_{kj} < v_{lj}$).")
                
                concordance_sets = {}
                discordance_sets = {}
                for k in range(n_pasien):
                    for l in range(n_pasien):
                        if k != l:
                            c_set = [kriteria_keys[j] for j in range(n_kriteria) if V[k, j] >= V[l, j]]
                            d_set = [kriteria_keys[j] for j in range(n_kriteria) if V[k, j] < V[l, j]]
                            concordance_sets[f"C({names[k]}, {names[l]})"] = ", ".join(c_set) if c_set else "-"
                            discordance_sets[f"D({names[k]}, {names[l]})"] = ", ".join(d_set) if d_set else "-"

                col_cd1, col_cd2 = st.columns(2)
                with col_cd1:
                    st.markdown("**Himpunan Concordance ($C_{kl}$):**")
                    render_styled_table(pd.DataFrame(list(concordance_sets.items()), columns=["Pasangan Pasien", "Kriteria Unggul"]))
                with col_cd2:
                    st.markdown("**Himpunan Discordance ($D_{kl}$):**")
                    render_styled_table(pd.DataFrame(list(discordance_sets.items()), columns=["Pasangan Pasien", "Kriteria Lemah"]))

                # Langkah 5: Matriks Concordance (C) & Discordance (D)
                st.markdown("#### 5. Matriks Concordance ($C$) dan Discordance ($D$)")
                C_matrix = np.zeros((n_pasien, n_pasien))
                D_matrix = np.zeros((n_pasien, n_pasien))

                for k in range(n_pasien):
                    for l in range(n_pasien):
                        if k != l:
                            c_idx = [j for j in range(n_kriteria) if V[k, j] >= V[l, j]]
                            C_matrix[k, l] = sum(w[j] for j in c_idx)
                            
                            d_idx = [j for j in range(n_kriteria) if V[k, j] < V[l, j]]
                            num = max([abs(V[k, j] - V[l, j]) for j in d_idx]) if d_idx else 0
                            den = max([abs(V[k, j] - V[l, j]) for j in range(n_kriteria)])
                            D_matrix[k, l] = num / den if den != 0 else 0

                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown("**Matriks Concordance ($C$):**")
                    render_styled_table(pd.DataFrame(C_matrix.round(4), index=names, columns=names))
                with col_m2:
                    st.markdown("**Matriks Discordance ($D$):**")
                    render_styled_table(pd.DataFrame(D_matrix.round(4), index=names, columns=names))

                # Langkah 6: Dominan Matriks & Aggregated Dominance Matrix (E)
                st.markdown("#### 6. Matriks Dominasi Agregat ($E$)")
                c_threshold = np.sum(C_matrix) / (n_pasien * (n_pasien - 1))
                d_threshold = np.sum(D_matrix) / (n_pasien * (n_pasien - 1))
                
                st.info(f"Threshold Concordance (c): **{c_threshold:.4f}** | Threshold Discordance (d): **{d_threshold:.4f}**")
                
                F_matrix = (C_matrix >= c_threshold).astype(int)
                G_matrix = (D_matrix < d_threshold).astype(int)
                np.fill_diagonal(F_matrix, 0)
                np.fill_diagonal(G_matrix, 0)
                
                E_matrix = F_matrix * G_matrix
                render_styled_table(pd.DataFrame(E_matrix, index=names, columns=names))
                st.caption("*Catatan: Nilai 1 berarti Pasien di Baris mendominasi Pasien di Kolom.*")
                
                st.markdown('</div>', unsafe_allow_html=True)

            # -------------------------------------------------------------
            # SUB-TAB 2: TOPSIS
            # -------------------------------------------------------------
            with calc_tab2:
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                
                # Langkah 1: Matriks Terbobot
                st.markdown("#### 1. Menggunakan Matriks Ternormalisasi Terbobot ($V$)")
                render_styled_table(pd.DataFrame(V.round(4), index=names, columns=kriteria_keys))

                # Langkah 2: Solusi Ideal Positif (A+) & Negatif (A-)
                st.markdown("#### 2. Solusi Ideal Positif ($A^+$) & Negatif ($A^-$)")
                st.caption("Karena seluruh kriteria bersifat Benefit (makin tinggi makin prioritas): $A^+ = \\max(V)$ dan $A^- = \\min(V)$")
                
                A_plus = np.max(V, axis=0)
                A_minus = np.min(V, axis=0)
                
                df_solusi = pd.DataFrame([A_plus.round(4), A_minus.round(4)], index=["Solusi Ideal Positif (A+)", "Solusi Ideal Negatif (A-)"], columns=kriteria_keys)
                render_styled_table(df_solusi)

                # Langkah 3: Jarak Solusi Ideal (D+ dan D-)
                st.markdown("#### 3. Jarak ke Solusi Ideal Positif ($D^+$) & Negatif ($D^-$)")
                st.caption("Formula: $D_i^+ = \\sqrt{\\sum (v_{ij} - a_j^+)^2}$ dan $D_i^- = \\sqrt{\\sum (v_{ij} - a_j^-)^2}$")
                
                D_plus = np.sqrt(np.sum((V - A_plus)**2, axis=1))
                D_minus = np.sqrt(np.sum((V - A_minus)**2, axis=1))
                
                df_jarak = pd.DataFrame({
                    "Nama Pasien": names,
                    "Jarak Positif (D+)": D_plus.round(4),
                    "Jarak Negatif (D-)": D_minus.round(4)
                })
                render_styled_table(df_jarak)

                # Langkah 4: Skor Preferensi TOPSIS (V_i)
                st.markdown("#### 4. Nilai Preferensi Akhir ($V_i$)")
                st.caption("Formula: $V_i = \\frac{D_i^-}{D_i^+ + D_i^-}$ (Makin mendekati 1, makin tinggi prioritas penanganan medis)")
                
                pref = D_minus / (D_plus + D_minus)
                
                df_topsis_final = pd.DataFrame({
                    "Nama Pasien": names,
                    "D+": D_plus.round(4),
                    "D-": D_minus.round(4),
                    "Nilai Preferensi (V_i)": pref.round(4)
                }).sort_values(by="Nilai Preferensi (V_i)", ascending=False)
                
                render_styled_table(df_topsis_final)
                
                st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------------------
    # TAB 5: HASIL RANKING & FITUR DOWNLOAD PDF
    # ---------------------------------------------------------------------
    with tabs[4]:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        
        if len(st.session_state.data_pralansia) > 0:
            names = [p["Nama"] for p in st.session_state.data_pralansia]
            X = np.array([nilai_sub_kriteria(p) for p in st.session_state.data_pralansia], dtype=float)
            pembagi = np.sqrt(np.sum(X**2, axis=0))
            pembagi[pembagi == 0] = 1
            V = (X / pembagi) * np.array(list(BOBOT.values()))
            
            A_plus, A_minus = np.max(V, axis=0), np.min(V, axis=0)
            D_plus = np.sqrt(np.sum((V - A_plus)**2, axis=1))
            D_minus = np.sqrt(np.sum((V - A_minus)**2, axis=1))
            pref = (D_minus / (D_plus + D_minus)).round(3)
            
            pasien_ranked = []
            for idx, p in enumerate(st.session_state.data_pralansia):
                p_copy = p.copy()
                p_copy["Skor"] = pref[idx]
                pasien_ranked.append(p_copy)
                
            pasien_ranked = sorted(pasien_ranked, key=lambda x: x["Skor"], reverse=True)

            col_rank_head, col_rank_btn = st.columns([3, 1])
            with col_rank_head:
                st.markdown("### 🏆 Tabel Prioritas Pasien Pralansia")
            with col_rank_btn:
                pdf_all_bytes = generate_all_pdf(pasien_ranked)
                st.download_button(
                    label="📄 Download PDF Rekapitulasi",
                    data=pdf_all_bytes,
                    file_name="Rekapitulasi_Ranking_Pralansia.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            df_rank = pd.DataFrame([{
                "Peringkat": i+1,
                "Nama Pasien": p["Nama"],
                "NIK": p["NIK"],
                "Umur": f"{p['Umur']} Thn",
                "TD (mmHg)": p["Tekanan_Darah"],
                "Gula Darah": p["Gula_Darah"],
                "IMT": p["IMT"],
                "Skor Preferensi": p["Skor"]
            } for i, p in enumerate(pasien_ranked)])
            
            render_styled_table(df_rank)
            st.markdown('</div>', unsafe_allow_html=True)

            # CARDS REKOMENDASI INDIVIDUAL
            st.markdown("### 💡 Rekomendasi Skrining & Pola Hidup Pasien")

            for i, p in enumerate(pasien_ranked):
                skrining, pola_hidup = get_recommendations(p)
                card_class = "patient-card-high" if p["Skor"] >= 0.6 else ("patient-card-med" if p["Skor"] >= 0.4 else "patient-card-low")
                
                col_p_title, col_p_pdf = st.columns([3, 1])
                with col_p_title:
                    st.markdown(f'''
                        <div class="patient-card {card_class}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h3 style="margin: 0; color: #1e293b;">👤 {p['Nama']} <span style="font-size: 0.9rem; color: #64748b;">(NIK: {p['NIK']})</span></h3>
                                <span class="badge-rank">Rank #{i+1} | Skor: {p['Skor']}</span>
                            </div>
                            <p style="margin: 10px 0 0 0; color: #475569;">
                                <b>Status:</b> Umur {p['Umur']} thn | TD: <b>{p['Tekanan_Darah']} mmHg</b> | GDS: <b>{p['Gula_Darah']} mg/dL</b> | IMT: <b>{p['IMT']}</b>
                            </p>
                        </div>
                    ''', unsafe_allow_html=True)
                with col_p_pdf:
                    st.write("")
                    pdf_single = generate_single_pdf(p, i+1)
                    st.download_button(
                        label=f"📥 PDF {p['Nama']}",
                        data=pdf_single,
                        file_name=f"Laporan_Medis_{p['Nama']}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{p['NIK']}",
                        use_container_width=True
                    )

                col_rec1, col_rec2 = st.columns(2)
                with col_rec1:
                    st.markdown("##### 🔬 5 Rekomendasi Skrining Medis Lanjutan")
                    for s in skrining:
                        st.markdown(f"- {s}")

                with col_rec2:
                    st.markdown("##### 🥗 Intervensi & Panduan Pola Hidup")
                    for ph in pola_hidup:
                        st.markdown(f"- {ph}")
                st.markdown("---")
        else:
            st.info("Belum ada data pasien untuk di-ranking.")
            st.markdown('</div>', unsafe_allow_html=True)