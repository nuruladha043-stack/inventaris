import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="UMKM Smart Inventory", layout="wide")

# Inisialisasi Database Sederhana
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("🏪 UMKM Smart Inventory & Profit Tracker")
st.markdown("---")

# 2. Fitur Sidebar: Input Transaksi
with st.sidebar:
    st.header("📝 Catat Transaksi")
    with st.form("transaction_form"):
        tipe = st.selectbox("Jenis Kegiatan", ["Masuk (Beli Stok)", "Keluar (Jual Barang)"])
        nama = st.text_input("Nama Barang (Gunakan Huruf Kapital)", placeholder="CONTOH: KOPI ARABIKA").upper()
        qty = st.number_input("Jumlah (Unit)", min_value=1, value=1)
        harga = st.number_input("Harga Satuan (Rp)", min_value=0, value=10000, step=500)
        limit = st.number_input("Batas Stok Aman (Minimal)", min_value=0, value=5)
        submitted = st.form_submit_button("Simpan Transaksi")

    if submitted and nama:
        if nama not in st.session_state.inventory:
            st.session_state.inventory[nama] = {'stok': 0, 'total_biaya': 0, 'limit': limit, 'terjual': 0, 'pendapatan': 0}
        
        data = st.session_state.inventory[nama]
        
        if tipe == "Masuk (Beli Stok)":
            data['stok'] += qty
            data['total_biaya'] += (qty * harga)
            st.success(f"Berhasil menambah stok {nama}")
        elif tipe == "Keluar (Jual Barang)":
            if data['stok'] >= qty:
                avg_cost = data['total_biaya'] / data['stok']
                data['stok'] -= qty
                data['total_biaya'] -= (qty * avg_cost)
                data['terjual'] += qty
                data['pendapatan'] += (qty * harga)
                st.warning(f"Terjual {qty} unit {nama}")
            else:
                st.error("Stok tidak cukup!")
        
        st.session_state.history.append({
            "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Barang": nama, "Tipe": tipe, "Qty": qty, "Nilai": harga
        })

# 3. FITUR: DASHBOARD METRIK (Fitur #4)
if st.session_state.inventory:
    df = pd.DataFrame.from_dict(st.session_state.inventory, orient='index').reset_index()
    df.columns = ['Barang', 'Stok', 'Total_Modal', 'Limit', 'Terjual', 'Pendapatan']
    
    # Hitung Estimasi Laba Kotor (Fitur #9)
    # Laba = Pendapatan - (Barang Terjual * Harga Modal Rata-rata saat itu)
    # Sederhananya di sini kita tampilkan pendapatan vs modal yang tersisa
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Nilai Aset Gudang", f"Rp{df['Total_Modal'].sum():,.0f}")
    m2.metric("📦 Total Jenis Barang", len(df))
    m3.metric("📈 Total Pendapatan", f"Rp{df['Pendapatan'].sum():,.0f}")
    m4.metric("⚠️ Barang Perlu Re-order", len(df[df['Stok'] <= df['Limit']]))

    st.markdown("---")

    # 4. FITUR: VISUALISASI (Fitur #5 & #6)
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.subheader("📊 Komposisi Modal per Barang")
        fig_pie = px.pie(df, values='Total_Modal', names='Barang', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_v2:
        st.subheader("📉 Status Stok vs Batas Aman")
        df['Status'] = df.apply(lambda x: 'BAHAYA' if x['Stok'] <= x['Limit'] else 'AMAN', axis=1)
        fig_bar = px.bar(df, x='Barang', y=['Stok', 'Limit'], barmode='group', color_discrete_sequence=['#1f77b4', '#ff7f0e'])
        st.plotly_chart(fig_bar, use_container_width=True)

    # 5. FITUR: TABEL DETAIL & PENCARIAN (Fitur #7)
    st.subheader("🔍 Detail & Pencarian Inventaris")
    search = st.text_input("Cari nama barang...", "").upper()
    df_display = df[df['Barang'].str.contains(search)]
    
    # Beri warna pada baris yang stoknya sedikit
    def highlight_low(s):
        return ['background-color: #ffcccc' if s.Stok <= s.Limit else '' for _ in s]
    
    st.dataframe(df_display.style.apply(highlight_low, axis=1).format({'Total_Modal': '{:,.0f}', 'Pendapatan': '{:,.0f}'}), use_container_width=True)

    # 6. FITUR: RIWAYAT & EKSPOR (Fitur #8 & #10)
    st.markdown("---")
    with st.expander("📜 Lihat Riwayat Transaksi & Download Laporan"):
        if st.session_state.history:
            df_hist = pd.DataFrame(st.session_state.history)
            st.dataframe(df_hist, use_container_width=True)
            
            csv = df_hist.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Laporan (CSV untuk Excel)",
                data=csv,
                file_name=f"Laporan_UMKM_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
            )
else:
    st.info("👋 Halo! Silakan masukkan data barang pertama Anda di sidebar sebelah kiri.")

# Tombol Reset
if st.button("Hapus Semua Data"):
    st.session_state.inventory = {}
    st.session_state.history = []
    st.rerun()
