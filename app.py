import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px # Tambahkan ini untuk grafik yang interaktif

# Konfigurasi Halaman
st.set_page_config(page_title="Pro Inventory Manager", layout="wide")

st.title("🚀 Pro Accounting Inventory System")

# Inisialisasi Database
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("📝 Input Transaksi")
    tipe = st.selectbox("Jenis Transaksi", ["Masuk (Pembelian)", "Keluar (Penjualan)"])
    nama_barang = st.text_input("Nama Barang").upper()
    jumlah = st.number_input("Jumlah Unit", min_value=1)
    harga = st.number_input("Harga Satuan (Rp)", min_value=0)
    # FITUR BARU: Penentuan batas minimum stok
    stok_min = st.number_input("Batas Minimal Stok (Alert)", min_value=0, value=5)
    
    if st.button("Proses"):
        if nama_barang:
            if nama_barang not in st.session_state.inventory:
                st.session_state.inventory[nama_barang] = {'stok': 0, 'total_biaya': 0, 'min_stok': stok_min, 'total_keluar': 0}
            
            data = st.session_state.inventory[nama_barang]
            
            if tipe == "Masuk (Pembelian)":
                data['stok'] += jumlah
                data['total_biaya'] += (jumlah * harga)
                st.success(f"Masuk: {nama_barang}")
            elif tipe == "Keluar (Penjualan)":
                if data['stok'] >= jumlah:
                    avg_cost = data['total_biaya'] / data['stok']
                    data['stok'] -= jumlah
                    data['total_biaya'] -= (jumlah * avg_cost)
                    data['total_keluar'] += jumlah # Track untuk analisis
                    st.warning(f"Keluar: {nama_barang} (HPP: Rp{avg_cost:,.0f})")
                else:
                    st.error("Stok Kurang!")
            
            st.session_state.history.append({
                "Waktu": datetime.now().strftime("%d/%m %H:%M"),
                "Item": nama_barang, "Tipe": tipe, "Qty": jumlah
            })
        st.rerun()

# --- DASHBOARD UTAMA ---
if st.session_state.inventory:
    df = pd.DataFrame.from_dict(st.session_state.inventory, orient='index').reset_index()
    df.columns = ['Barang', 'Stok', 'Total Nilai', 'Min Stok', 'Terjual']
    
    # 1. METRIK UTAMA
    m1, m2, m3 = st.columns(3)
    total_nilai = df['Total Nilai'].sum()
    stok_rendah = df[df['Stok'] <= df['Min Stok']].shape[0]
    
    m1.metric("Total Aset (Rp)", f"{total_nilai:,.0f}")
    m2.metric("Barang Kritis (Low Stock)", stok_rendah)
    m3.metric("Total Unit Terjual", df['Terjual'].sum())

    st.divider()

    # 2. VISUALISASI (FITUR MENARIK)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("💰 Proporsi Nilai Aset")
        fig_pie = px.pie(df, values='Total Nilai', names='Barang', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        

    with col_chart2:
        st.subheader("📉 Analisis Stok vs Batas Minimum")
        fig_bar = px.bar(df, x='Barang', y=['Stok', 'Min Stok'], barmode='group', 
                         color_discrete_sequence=['#00CC96', '#EF553B'])
        st.plotly_chart(fig_bar, use_container_width=True)
        

    # 3. TABEL DATA DENGAN HIGHLIGHT
    st.subheader("🔍 Detail Inventaris")
    def highlight_low_stock(s):
        return ['background-color: #ffcccc' if s.Stok <= s['Min Stok'] else '' for _ in s]
    
    st.dataframe(df.style.apply(highlight_low_stock, axis=1).format({'Total Nilai': '{:,.0f}'}), use_container_width=True)

else:
    st.info("👋 Selamat Datang! Masukkan transaksi pertama Anda di sidebar untuk memulai.")

# --- FITUR EKSPOR ---
if st.session_state.history:
    st.divider()
    with st.expander("📥 Ekspor Data & Riwayat"):
        csv = pd.DataFrame(st.session_state.history).to_csv(index=False).encode('utf-8')
        st.download_button("Download Riwayat (CSV)", data=csv, file_name="history_stok.csv")
