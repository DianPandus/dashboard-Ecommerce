import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px
from io import StringIO

# ID file dari Google Drive
file_id = "1gFSBGm9U_w6rrHvP3qnTnvnGT2Mwc1LP"  # Ganti dengan ID file-mu

# URL untuk mengunduh file dari Google Drive
url = f"https://drive.google.com/uc?id={file_id}"

# Download file
response = requests.get(url)
if response.status_code == 200:
    all_df = pd.read_csv(StringIO(response.text))
    st.success("Dataset berhasil dimuat dari Google Drive!")
else:
    st.error("Gagal mengunduh dataset. Periksa ID file atau izin akses.")
    st.stop()


# Load data
all_df = pd.read_csv('all_data.csv')

# Konversi kolom tanggal ke datetime
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# Sidebar untuk filter data
st.sidebar.header('Filter Data')
start_date = st.sidebar.date_input('Start Date', all_df['order_purchase_timestamp'].min())
end_date = st.sidebar.date_input('End Date', all_df['order_purchase_timestamp'].max())

# Filter tambahan: Kategori Produk
product_categories = all_df['product_category_name'].unique()
selected_categories = st.sidebar.multiselect('Pilih Kategori Produk', product_categories, default=product_categories)

# Filter data berdasarkan tanggal dan kategori produk
filtered_df = all_df[
    (all_df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & 
    (all_df['order_purchase_timestamp'] <= pd.to_datetime(end_date)) &
    (all_df['product_category_name'].isin(selected_categories))
]

# Header dashboard
st.title('E-Commerce Dashboard')
st.markdown("""
Dashboard ini menampilkan berbagai analisis terkait penjualan, pelanggan, dan produk dari data e-commerce.
""")

uploaded_file = st.sidebar.file_uploader("Upload CSV file", type="csv")


# Metrik utama
st.header('Metrik Utama')
col1, col2, col3 = st.columns(3)
with col1:
    total_orders = filtered_df['order_id'].nunique()
    st.metric("Total Orders", value=total_orders)
with col2:
    total_revenue = filtered_df['payment_value'].sum()
    st.metric("Total Revenue", value=format_currency(total_revenue, "R$", locale='id_ID'))
with col3:
    avg_order_value = filtered_df['payment_value'].mean()
    st.metric("Average Order Value", value=format_currency(avg_order_value, "R$", locale='id_ID'))

# Distribusi Harga Produk
st.header('Distribusi Harga Produk')
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(filtered_df['price'], bins=30, kde=True, color='skyblue')
avg_price = filtered_df['price'].mean()
plt.axvline(avg_price, color='red', linestyle='--', label=f'Rata-rata: {avg_price:.2f}')
plt.title('Distribusi Harga Produk')
plt.xlabel('Harga')
plt.ylabel('Frekuensi')
plt.legend()
st.pyplot(fig)

# Top 10 Kategori Produk dengan Harga Tertinggi (Plotly)
st.header('Top 10 Kategori Produk dengan Harga Tertinggi')
average_price_by_category = filtered_df.groupby('product_category_name')['price'].mean().reset_index()
average_price_by_category = average_price_by_category.sort_values(by='price', ascending=False).head(10)
fig = px.bar(average_price_by_category, x='price', y='product_category_name', orientation='h', 
             title='Top 10 Kategori Produk dengan Harga Tertinggi', labels={'price': 'Rata-rata Harga', 'product_category_name': 'Kategori Produk'})
st.plotly_chart(fig)

# Top 10 Kategori Produk dengan Penjualan Tertinggi (Plotly)
st.header('Top 10 Kategori Produk dengan Penjualan Tertinggi')
total_sales_by_category = filtered_df.groupby('product_category_name')['order_item_id'].sum().reset_index()
total_sales_by_category = total_sales_by_category.sort_values(by='order_item_id', ascending=False).head(10)
fig = px.bar(total_sales_by_category, x='order_item_id', y='product_category_name', orientation='h', 
             title='Top 10 Kategori Produk dengan Penjualan Tertinggi', labels={'order_item_id': 'Total Penjualan', 'product_category_name': 'Kategori Produk'})
st.plotly_chart(fig)

# Tren Revenue Bulanan (Plotly)
st.header('Tren Revenue Bulanan')
filtered_df['order_purchase_month'] = filtered_df['order_purchase_timestamp'].dt.to_period('M')
total_revenue_by_month = filtered_df.groupby('order_purchase_month')['payment_value'].sum().reset_index()
total_revenue_by_month['order_purchase_month'] = total_revenue_by_month['order_purchase_month'].astype(str)
fig = px.line(total_revenue_by_month, x='order_purchase_month', y='payment_value', 
              title='Total Revenue per Bulan', labels={'order_purchase_month': 'Bulan', 'payment_value': 'Total Revenue'})
st.plotly_chart(fig)

# Pola Musiman Penjualan (Plotly)
st.header('Pola Musiman Penjualan')
filtered_df['order_purchase_month_only'] = filtered_df['order_purchase_timestamp'].dt.month
seasonal_sales = filtered_df.groupby('order_purchase_month_only').size().reset_index(name='total_orders')
fig = px.bar(seasonal_sales, x='order_purchase_month_only', y='total_orders', 
             title='Pola Musiman Penjualan', labels={'order_purchase_month_only': 'Bulan', 'total_orders': 'Jumlah Pesanan'})
st.plotly_chart(fig)

# Distribusi Metode Pembayaran (Plotly)
st.header('Distribusi Metode Pembayaran')
payment_frequency = filtered_df['payment_type'].value_counts().reset_index()
payment_frequency.columns = ['payment_type', 'count']
fig = px.bar(payment_frequency, x='payment_type', y='count', 
             title='Distribusi Metode Pembayaran', labels={'payment_type': 'Metode Pembayaran', 'count': 'Jumlah Transaksi'})
st.plotly_chart(fig)

# Footer
st.caption('Copyright © 2023 by Dian Pandu Syahfitra')
