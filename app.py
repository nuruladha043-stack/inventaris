import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="UMKM Smart Inventory & Profit", layout="wide")

# Inisialisasi Database Sederhana (Session State)
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("🏪 UMKM Smart Inventory & Profit Tracker")
st.markdown("---")

# 2. Bagian Sidebar: Input Transaksi
with st.sidebar:
    st.header("📝 Catat Transaksi")
    with st.form("transaction_form"):
        tipe = st.selectbox("Jenis Kegiatan", ["Masuk (Beli Stok)", "Keluar (Jual Barang)"])
        nama = st.text_input("Nama Barang (Gunakan Huruf Kapital)", placeholder="CONTOH: BERAS PREMIUM").upper()
        qty = st.number_input("Jumlah (Unit)", min_value=1, value=1)
        harga = st.number_input("Harga Satuan (Rp)", min_value=0, value=10000, step=500)
        limit = st.number_input("Batas Stok Aman (Minimal)", min_value=0, value=5)
        submitted = st.form_submit_button("Simpan Transaksi")

    if submitted and nama:
        if nama not in st.session_state.inventory:
            st.session_state.inventory[nama] = {
                'stok': 0, 
                'total_biaya': 0, 
                'limit': limit, 
                'terjual': 0, 
                'pendapatan': 0,
                'total_hpp': 0 # Tambahan penampung HPP
            }
        
        data = st.session_state.inventory[nama]
        
        if tipe == "Masuk (Beli Stok)":
            data['stok'] += qty
            data['total_biaya'] += (qty * harga)
            st.success(f"Berhasil menambah stok {nama}")
            
        elif tipe == "Keluar (Jual Barang)":
            if data['stok'] >= qty:
                # Logika Average Costing (HPP per Unit)
                avg_cost_hpp = data['total_biaya'] / data['stok']
                
                # Update Data
                data['stok'] -= qty
                data['total_biaya'] -= (qty * avg_cost_hpp)
                data['terjual'] += qty
                data['pendapatan'] += (qty * harga)
                data['total_hpp'] += (qty * avg_cost_hpp) # Akumulasi HPP
                
                st.warning(f"Terjual {qty} unit {nama}. HPP: Rp{avg_cost_hpp:,.0f}")
            else:
                st.error("Stok tidak mencukupi!")
        
        st.session_state.history.append({
            "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Barang": nama, "Tipe": tipe, "Qty": qty, "Nilai": harga
        })

# 3. Dashboard Metrik
if st.session_state.inventory:
    df = pd.DataFrame.from_dict(st.session_state.inventory, orient='index').reset_index()
    df.columns = ['Barang', 'Stok', 'Total_Modal_Sisa', 'Limit', 'Terjual', 'Pendapatan', 'Total_HPP']
    
    # Hitung Laba Kotor
    df['Laba_Kotor'] = df['Pendapatan'] - df['Total_HPP']
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Nilai Aset Gudang (Sisa)", f"Rp{df['Total_Modal_Sisa'].sum():,.0f}")
    m2.metric("📈 Total Pendapatan", f"Rp{df['Pendapatan'].sum():,.0f}")
    m3.metric("💵 Total Laba Kotor", f"Rp{df['Laba_Kotor'].sum():,.0f}")
    m4.metric("⚠️ Barang Perlu Re-order", len(df[df['Stok'] <= df['Limit']]))

    st.markdown("---")

    # 4. Visualisasi
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.subheader("📊 Komposisi Modal Tersisa")
        fig_pie = px.pie(df, values='Total_Modal_Sisa', names='Barang', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_v2:
        st.subheader("📉 Status Stok vs Batas Aman")
        df['Status'] = df.apply(lambda x: 'BAHAYA' if x['Stok'] <= x['Limit'] else 'AMAN', axis=1)
        fig_bar = px.bar(df, x='Barang', y=['Stok', 'Limit'], barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)

    # 5. Tabel Detail dengan HPP & Laba
    st.subheader("🔍 Detail Inventaris, HPP & Laba")
    
    # Fungsi styling warna merah untuk stok tipis
    def highlight_low(s):
        return ['background-color: #ffcccc' if s.Status == 'BAHAYA' else '' for _ in s]

    # Pilih dan urutkan kolom agar informatif
    df_tampil = df[['Barang', 'Stok', 'Total_Modal_Sisa', 'Terjual', 'Total_HPP', 'Pendapatan', 'Laba_Kotor', 'Status']]
    
    st.dataframe(
        df_tampil.style.apply(highlight_low, axis=1).format({
            'Total_Modal_Sisa': '{:,.0f}',
            'Total_HPP': '{:,.0f}',
            'Pendapatan': '{:,.0f}',
            'Laba_Kotor': '{:,.0f}'
        }),
        use_container_width=True
    )

    # 6. Riwayat & Ekspor
    with st.expander("📜 Lihat Riwayat Transaksi & Download Laporan"):
        if st.session_state.history:
            df_hist = pd.DataFrame(st.session_state.history)
            st.dataframe(df_hist, use_container_width=True)
            csv = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Laporan (CSV)", data=csv, file_name="laporan_umkm.csv", mime='text/csv')
else:
    st.info("👋 Selamat Datang! Silakan masukkan data barang di sidebar untuk memulai.")

# Tombol Reset
if st.button("Hapus Semua Data"):
    st.session_state.inventory = {}
    st.session_state.history = []
    st.rerun()
