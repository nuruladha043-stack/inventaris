import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Inventaris Akuntansi", layout="wide")

st.title("📦 Sistem Manajemen Inventaris & HPP")
st.markdown("""
Aplikasi ini mengelola stok barang dengan metode **Average Costing** untuk menghitung Nilai Persediaan dan Harga Pokok Penjualan (HPP) secara otomatis.
""")

# Inisialisasi Database Sederhana (Session State)
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# --- BAGIAN SIDEBAR (INPUT) ---
with st.sidebar:
    st.header("Entri Transaksi")
    tipe = st.selectbox("Jenis Transaksi", ["Masuk (Pembelian)", "Keluar (Penjualan)"])
    nama_barang = st.text_input("Nama Barang", placeholder="Misal: Kertas A4")
    jumlah = st.number_input("Jumlah Unit", min_value=1, value=1)
    harga = st.number_input("Harga per Unit (Rp)", min_value=0, value=10000, step=1000)
    
    if st.button("Proses Transaksi"):
        if nama_barang:
            # Pastikan barang ada di data
            if nama_barang not in st.session_state.inventory:
                st.session_state.inventory[nama_barang] = {'stok': 0, 'total_biaya': 0}
            
            data_stok = st.session_state.inventory[nama_barang]
            
            if tipe == "Masuk (Pembelian)":
                data_stok['stok'] += jumlah
                data_stok['total_biaya'] += (jumlah * harga)
                st.session_state.history.append({
                    "Waktu": datetime.now().strftime("%H:%M:%S"),
                    "Barang": nama_barang,
                    "Tipe": "Masuk",
                    "Qty": jumlah,
                    "Nilai": harga
                })
                st.success(f"Berhasil menambah stok {nama_barang}")
            
            elif tipe == "Keluar (Penjualan)":
                if data_stok['stok'] >= jumlah:
                    # Logika Average Costing
                    harga_rata_rata = data_stok['total_biaya'] / data_stok['stok']
                    data_stok['stok'] -= jumlah
                    data_stok['total_biaya'] -= (jumlah * harga_rata_rata)
                    
                    st.session_state.history.append({
                        "Waktu": datetime.now().strftime("%H:%M:%S"),
                        "Barang": nama_barang,
                        "Tipe": "Keluar",
                        "Qty": jumlah,
                        "HPP per Unit": round(harga_rata_rata, 2)
                    })
                    st.warning(f"Barang keluar. HPP per unit: Rp{harga_rata_rata:,.0f}")
                else:
                    st.error("Stok tidak mencukupi!")
        else:
            st.error("Nama barang tidak boleh kosong!")

# --- BAGIAN DASHBOARD UTAMA ---
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📋 Ringkasan Stok & Nilai Aset")
    if st.session_state.inventory:
        # Konversi dict ke DataFrame untuk tabel
        df_stok = pd.DataFrame.from_dict(st.session_state.inventory, orient='index').reset_index()
        df_stok.columns = ['Nama Barang', 'Sisa Stok', 'Total Nilai Buku (Rp)']
        
        # Hitung Harga Rata-rata untuk tampilan
        df_stok['Harga Rata-rata (Rp)'] = df_stok['Total Nilai Buku (Rp)'] / df_stok['Sisa Stok']
        df_stok['Harga Rata-rata (Rp)'] = df_stok['Harga Rata-rata (Rp)'].fillna(0)
        
        st.dataframe(df_stok.style.format({
            'Total Nilai Buku (Rp)': '{:,.0f}',
            'Harga Rata-rata (Rp)': '{:,.0f}'
        }), use_container_width=True)
        
        total_aset = df_stok['Total Nilai Buku (Rp)'].sum()
        st.metric("Total Investasi Inventaris", f"Rp{total_aset:,.0f}")
    else:
        st.info("Belum ada stok yang terdaftar.")

with col2:
    st.subheader("📜 Log Aktivitas")
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history).tail(10)) # Tampilkan 10 terakhir
    else:
        st.write("Belum ada riwayat transaksi.")

# Tombol Reset Data
if st.button("Reset Semua Data"):
    st.session_state.inventory = {}
    st.session_state.history = []
    st.rerun()
