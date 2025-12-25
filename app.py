 import streamlit as st
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Inventaris Akuntansi", layout="wide")

st.title("📦 Sistem Manajemen Inventaris & HPP")
st.subheader("Metode Penilaian: Average Cost")

# Inisialisasi Database Sederhana di Session State
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar untuk Input
with st.sidebar:
    st.header("Input Transaksi")
    action = st.selectbox("Jenis Transaksi", ["Barang Masuk (Beli)", "Barang Keluar (Jual)"])
    item_name = st.text_input("Nama Barang", placeholder="Contoh: Kopi Bubuk")
    qty = st.number_input("Jumlah (Qty)", min_value=1, value=1)
    price = st.number_input("Harga per Unit (Rp)", min_value=0, value=1000)
    
    if st.button("Simpan Transaksi"):
        if item_name:
            if item_name not in st.session_state.inventory:
                st.session_state.inventory[item_name] = {'qty': 0, 'total_cost': 0}
            
            inv = st.session_state.inventory[item_name]
            
            if action == "Barang Masuk (Beli)":
                inv['qty'] += qty
                inv['total_cost'] += (qty * price)
                st.session_state.history.append({"Tipe": "Masuk", "Barang": item_name, "Qty": qty, "Harga": price})
                st.success("Data Masuk Tersimpan!")
            
            elif action == "Barang Keluar (Jual)":
                if inv['qty'] >= qty:
                    avg_cost = inv['total_cost'] / inv['qty']
                    inv['qty'] -= qty
                    inv['total_cost'] -= (qty * avg_cost)
                    st.session_state.history.append({"Tipe": "Keluar", "Barang": item_name, "Qty": qty, "Harga": avg_cost})
                    st.warning(f"Data Keluar Tersimpan! HPP dihitung: Rp{avg_cost:,.2f}")
                else:
                    st.error("Stok tidak mencukupi!")
        else:
            st.error("Nama barang harus diisi!")

# Dashboard Utama
col1, col2 = st.columns(2)

with col1:
    st.write("### 📊 Status Stok Saat Ini")
    if st.session_state.inventory:
        df_inv = pd.DataFrame.from_dict(st.session_state.inventory, orient='index').reset_index()
        df_inv.columns = ['Nama Barang', 'Stok Tersedia', 'Total Nilai Aset (Rp)']
        df_inv['Harga Rata-rata'] = df_inv['Total Nilai Aset (Rp)'] / df_inv['Stok Tersedia']
        st.dataframe(df_inv.style.format({"Total Nilai Aset (Rp)": "{:,.0f}", "Harga Rata-rata": "{:,.0f}"}), use_container_width=True)
    else:
        st.info("Belum ada data stok.")

with col2:
    st.write("### 📜 Riwayat Transaksi")
    if st.session_state.history:
        st.table(pd.DataFrame(st.session_state.history))
    else:
        st.info("Belum ada riwayat.")

# Tombol Reset
if st.button("Hapus Semua Data"):
    st.session_state.inventory = {}
    st.session_state.history = []
    st.rerun()
