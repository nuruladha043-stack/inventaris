import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi Halaman agar tampil penuh (Wide Mode)
st.set_page_config(page_title="Visual Inventory Pro", layout="wide")

# --- DATABASE SEDERHANA ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("📊 Visual Inventory & Asset Dashboard")
st.markdown("---")

# --- SIDEBAR UNTUK INPUT ---
with st.sidebar:
    st.header("📥 Transaksi Baru")
    tipe = st.selectbox("Aksi", ["Masuk (Beli)", "Keluar (Jual)"])
    item = st.text_input("Nama Produk").upper()
    qty = st.number_input("Jumlah Unit", min_value=1, value=1)
    price = st.number_input("Harga Satuan (Rp)", min_value=0, value=10000)
    limit = st.number_input("Batas Stok Minimum", min_value=0, value=10)
    
    if st.button("Simpan Data", use_container_width=True):
        if item:
            if item not in st.session_state.inventory:
                st.session_state.inventory[item] = {'stok': 0, 'total_biaya': 0, 'limit': limit, 'terjual': 0}
            
            inv = st.session_state.inventory[item]
            if tipe == "Masuk (Beli)":
                inv['stok'] += qty
                inv['total_biaya'] += (qty * price)
                st.success(f"Added: {item}")
            elif tipe == "Keluar (Jual)":
                if inv['stok'] >= qty:
                    avg_cost = inv['total_biaya'] / inv['stok']
                    inv['stok'] -= qty
                    inv['total_biaya'] -= (qty * avg_cost)
                    inv['terjual'] += qty
                    st.warning(f"Sold: {item}")
                else:
                    st.error("Stok Habis!")
            
            st.session_state.history.append({
                "Waktu": datetime.now().strftime("%H:%M"),
                "Barang": item, "Tipe": tipe, "Qty": qty, "Nilai": price
            })
            st.rerun()

# --- DASHBOARD VISUAL ---
if st.session_state.inventory:
    # 1. Persiapan Data
    df = pd.DataFrame.from_dict(st.session_state.inventory, orient='index').reset_index()
    df.columns = ['Barang', 'Stok', 'Total Nilai', 'Limit', 'Terjual']
    df['Status'] = df.apply(lambda x: "🚨 KRITIS" if x['Stok'] <= x['Limit'] else "✅ AMAN", axis=1)

    # 2. Row Metrik (Visual Card)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Aset", f"Rp{df['Total Nilai'].sum():,.0f}")
    c2.metric("📦 Jenis Barang", len(df))
    c3.metric("🔥 Total Terjual", f"{df['Terjual'].sum()} unit")
    c4.metric("⚠️ Barang Kritis", len(df[df['Status'] == "🚨 KRITIS"]))

    st.markdown("### 📈 Analisis Visual")
    
    # 3. Grafik Bar & Pie (Row Visual 1)
    row1_1, row1_2 = st.columns([2, 1])
    
    with row1_1:
        st.write("**Perbandingan Stok vs Batas Minimum**")
        fig_stok = px.bar(df, x='Barang', y=['Stok', 'Limit'], 
                         barmode='group',
                         color_discrete_sequence=['#3366CC', '#FF9900'],
                         template="plotly_white")
        st.plotly_chart(fig_stok, use_container_width=True)
        

    with row1_2:
        st.write("**Proporsi Nilai Investasi**")
        fig_pie = px.pie(df, values='Total Nilai', names='Barang', hole=.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
        

    # 4. Grafik Tren/Log (Row Visual 2)
    st.markdown("### 🕒 Riwayat Pergerakan Barang")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        
        # Visualisasi riwayat dengan grafik garis sederhana
        fig_trend = px.line(df_hist, x='Waktu', y='Qty', color='Barang', markers=True,
                           title="Volume Transaksi per Waktu",
                           template="plotly_dark")
        st.plotly_chart(fig_trend, use_container_width=True)
        

    # 5. Tabel Detail dengan Style Visual
    st.subheader("📋 Tabel Inventaris Lengkap")
    
    def color_status(val):
        color = '#ff4b4b' if val == "🚨 KRITIS" else '#00cc96'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df.style.applymap(color_status, subset=['Status'])
                 .format({'Total Nilai': 'Rp{:,.0f}'}), 
                 use_container_width=True)

else:
    st.info("👋 Dashboard kosong. Silakan masukkan data barang di panel samping!")

# Tombol Reset Visual
if st.button("Reset Dashboard"):
    st.session_state.inventory = {}
    st.session_state.history = []
    st.rerun()
