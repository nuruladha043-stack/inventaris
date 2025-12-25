import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Pro Inventory Manager", layout="wide")

# --- DATABASE SEDERHANA (Session State) ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("🚀 Pro Accounting Inventory & Analytics")

# --- BAGIAN SIDEBAR (INPUT & KONTROL) ---
with st.sidebar:
    st.header("📥 Entri Transaksi")
    tipe = st.selectbox("Jenis Transaksi", ["Masuk (Pembelian)", "Keluar (Penjualan)"])
    nama_barang = st.text_input("Nama Barang").upper()
    jumlah = st.number_input("Jumlah Unit", min_value=1, value=1)
    harga = st.number_input("Harga/HPP per Unit (Rp)", min_value=0, value=10000)
    
    # Fitur Baru: Batas Minimum Stok
    stok_min = st.number_input("Batas Stok Minimum", min_value=0, value=5)
    
    if st.button("Proses Transaksi"):
        if nama_barang:
            if nama_barang not in st.session_state.inventory:
                st.session_state.inventory[nama_barang] = {
                    'stok': 0, 'total_biaya': 0, 'limit': stok_min, 'terjual': 0
                }
            
            data = st.session_state.inventory[nama_barang]
            
            if tipe == "Masuk (Pembelian)":
                data['stok'] += jumlah
                data['total_biaya'] += (jumlah * harga)
                st.session_state.history.append({
                    "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Item": nama_barang, "Tipe": "Masuk", "Qty": jumlah, "Nilai": harga
                })
                st.success(f"Stok {nama_barang} berhasil ditambah!")
            
            elif tipe == "Keluar (Penjualan)":
                if data['stok'] >= jumlah:
                    avg_cost = data['total_biaya'] / data['stok']
                    data['stok'] -= jumlah
                    data['total_biaya'] -= (jumlah * avg_cost)
                    data['terjual'] += jumlah
                    st.session_state.history.append({
                        "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Item": nama_barang, "Tipe": "Keluar", "Qty": jumlah, "Nilai": avg_cost
                    })
                    st.warning(f"Barang keluar. HPP: Rp{avg_cost:,.0f}")
                else:
                    st.error("Gagal: Stok tidak mencukupi!")
            st.rerun()

# --- BAGIAN DASHBOARD UTAMA ---
if st.session_state.inventory:
    # Mengolah data untuk tampilan
    df = pd.DataFrame.from_dict(st.session_state.inventory, orient='index').reset_index()
    df.columns = ['Barang', 'Stok', 'Total Nilai', 'Limit', 'Total Terjual']
    
    # Tambahkan Status
    df['Status'] = df.apply(lambda x: "🚨 RE-ORDER" if x['Stok'] <= x['Limit'] else "✅ AMAN", axis=1)

    # 1. Row Metrik Utama
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Aset (Rp)", f"{df['Total Nilai'].sum():,.0f}")
    m2.metric("Total Barang", len(df))
    m3.metric("Stok Kritis", len(df[df['Status'] == "🚨 RE-ORDER"]))
    m4.metric("Unit Terjual", df['Total Terjual'].sum())

    st.divider()

    # 2. Row Visualisasi (FITUR MENARIK)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 Komposisi Nilai Aset")
        fig_pie = px.pie(df, values='Total Nilai', names='Barang', hole=0.3, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)
        

    with col_chart2:
        st.subheader("📈 Analisis Volume Stok")
        fig_bar = px.bar(df, x='Barang', y='Stok', color='Status', 
                         color_discrete_map={"✅ AMAN": "#00CC96", "🚨 RE-ORDER": "#EF553B"})
        st.plotly_chart(fig_bar, use_container_width=True)
        

    # 3. Tabel Detail
    st.subheader("🔍 Detail Inventaris")
    st.dataframe(df.style.format({'Total Nilai': '{:,.0f}'}), use_container_width=True)

    # 4. Riwayat & Tombol Ekspor
    st.divider()
    with st.expander("📜 Lihat Riwayat Lengkap & Ekspor"):
        hist_df = pd.DataFrame(st.session_state.history)
        st.table(hist_df.tail(10))
        
        csv = hist_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data Riwayat (CSV)",
            data=csv,
            file_name=f"log_inventaris_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )
else:
    st.info("Silakan masukkan transaksi di sidebar untuk melihat dashboard.")

# Reset Button
if st.button("Hapus Semua Data"):
    st.session_state.inventory = {}
    st.session_state.history = []
    st.rerun()
