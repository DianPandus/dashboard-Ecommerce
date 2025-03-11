import pandas as pd
import numpy as np
import streamlit as st
import requests
import plotly.express as px
from io import BytesIO  
from babel.numbers import format_currency

# ID file dari Google Drive
file_id = "1gFSBGm9U_w6rrHvP3qnTnvnGT2Mwc1LP"  # Ganti dengan ID file-mu
url = f"https://drive.google.com/uc?id={file_id}"

# Download file
response = requests.get(url)

if response.status_code == 200:
    all_df = pd.read_csv(BytesIO(response.content))
else:
    st.error("Gagal mengunduh dataset. Periksa ID file atau izin akses.")
    st.stop()

# Konversi kolom tanggal ke datetime
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# Sidebar untuk filter data
st.sidebar.header('Filter Data')
start_date = st.sidebar.date_input('Start Date', all_df['order_purchase_timestamp'].min())
end_date = st.sidebar.date_input('End Date', all_df['order_purchase_timestamp'].max())

# Filter tambahan: Kategori Produk
product_categories = all_df['product_category_name'].unique()
selected_categories = st.sidebar.multiselect('Pilih Kategori Produk', product_categories, default=product_categories)

# Filter data
filtered_df = all_df[
    (all_df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & 
    (all_df['order_purchase_timestamp'] <= pd.to_datetime(end_date)) & 
    (all_df['product_category_name'].isin(selected_categories))
]

# Header dashboard
st.title('E-Commerce Dashboard')


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

# Jumlah pelanggan per negara bagian (Plotly)
st.header('Jumlah Pelanggan per Negara Bagian')
customer_by_state = filtered_df.groupby('customer_state')['customer_unique_id'].nunique().reset_index(name='total_customers')
customer_by_state = customer_by_state.sort_values(by='total_customers', ascending=False)
fig = px.bar(customer_by_state, x='customer_state', y='total_customers', 
             labels={'customer_state': 'Negara Bagian', 'total_customers': 'Total Pelanggan'})
st.plotly_chart(fig)

# Jumlah pelanggan per kota (Plotly)
st.header('Top 10 Kota dengan Jumlah Pelanggan Tertinggi')
customer_by_city = filtered_df.groupby('customer_city')['customer_unique_id'].nunique().reset_index(name='total_customers')
customer_by_city = customer_by_city.sort_values(by='total_customers', ascending=False).head(10)
fig = px.bar(customer_by_city, x='customer_city', y='total_customers', 
             labels={'customer_city': 'Kota', 'total_customers': 'Total Pelanggan'})
st.plotly_chart(fig)

# Revenue per kategori produk (Plotly)
st.header('Top 10 Kategori Produk Berdasarkan Revenue')
category_revenue = filtered_df.groupby('product_category_name')['payment_value'].sum().reset_index(name='total_revenue')
category_revenue = category_revenue.sort_values(by='total_revenue', ascending=False).head(10)
fig = px.bar(category_revenue, x='product_category_name', y='total_revenue', 
             labels={'product_category_name': 'Kategori Produk', 'total_revenue': 'Total Revenue'})
st.plotly_chart(fig)

# Distribusi nilai pengiriman (Plotly)
st.header('Distribusi Nilai Pengiriman')
fig = px.histogram(filtered_df, x='freight_value', nbins=50, title="Distribusi Nilai Pengiriman")
st.plotly_chart(fig)

# Distribusi status pesanan (Plotly)
st.header('Distribusi Status Pesanan')
order_status_distribution = filtered_df['order_status'].value_counts().reset_index()
order_status_distribution.columns = ['order_status', 'count']
fig = px.bar(order_status_distribution, x='order_status', y='count', 
             labels={'order_status': 'Status Pesanan', 'count': 'Jumlah Pesanan'})
st.plotly_chart(fig)

# Top 10 kategori produk dengan harga tertinggi (Plotly)
st.header('Top 10 Kategori Produk dengan Harga Tertinggi')
average_price_by_category = filtered_df.groupby('product_category_name')['price'].mean().reset_index()
average_price_by_category = average_price_by_category.sort_values(by='price', ascending=False).head(10)
fig = px.bar(average_price_by_category, x='price', y='product_category_name', orientation='h', 
              labels={'price': 'Rata-rata Harga', 'product_category_name': 'Kategori Produk'})
st.plotly_chart(fig)

# Top 10 kategori produk dengan penjualan tertinggi (Plotly)
st.header('Top 10 Kategori Produk dengan Penjualan Tertinggi')
total_sales_by_category = filtered_df.groupby('product_category_name')['order_item_id'].sum().reset_index()
total_sales_by_category = total_sales_by_category.sort_values(by='order_item_id', ascending=False).head(10)
fig = px.bar(total_sales_by_category, x='order_item_id', y='product_category_name', orientation='h', 
              labels={'order_item_id': 'Total Penjualan', 'product_category_name': 'Kategori Produk'})
st.plotly_chart(fig)

# Tren revenue bulanan (Plotly)
st.header('Tren Revenue Bulanan')
filtered_df['order_purchase_month'] = filtered_df['order_purchase_timestamp'].dt.to_period('M')
total_revenue_by_month = filtered_df.groupby('order_purchase_month')['payment_value'].sum().reset_index()
total_revenue_by_month['order_purchase_month'] = total_revenue_by_month['order_purchase_month'].astype(str)
fig = px.line(total_revenue_by_month, x='order_purchase_month', y='payment_value', 
              labels={'order_purchase_month': 'Bulan', 'payment_value': 'Total Revenue'})
st.plotly_chart(fig)

# Pola musiman penjualan (Plotly)
st.header('Pola Musiman Penjualan')
filtered_df['order_purchase_month_only'] = filtered_df['order_purchase_timestamp'].dt.month
seasonal_sales = filtered_df.groupby('order_purchase_month_only').size().reset_index(name='total_orders')
fig = px.bar(seasonal_sales, x='order_purchase_month_only', y='total_orders', 
             labels={'order_purchase_month_only': 'Bulan', 'total_orders': 'Jumlah Pesanan'})
st.plotly_chart(fig)

# Distribusi metode pembayaran (Plotly)
st.header('Distribusi Metode Pembayaran')
payment_frequency = filtered_df['payment_type'].value_counts().reset_index()
payment_frequency.columns = ['payment_type', 'count']
fig = px.bar(payment_frequency, x='payment_type', y='count', 
             labels={'payment_type': 'Metode Pembayaran', 'count': 'Jumlah Transaksi'})
st.plotly_chart(fig)

# Footer
st.caption('Copyright © 2023 by Dian Pandu Syahfitra')
