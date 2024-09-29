import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_pesanan_bulanan_df(df):
    pesanan_bulanan_df = df.resample('M', on='order_purchase_timestamp').agg({
    "order_id": "nunique",
    "payment_value": "sum"
}).reset_index()

    pesanan_bulanan_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    data_2018 = pesanan_bulanan_df[pesanan_bulanan_df['order_purchase_timestamp'].dt.year == 2018].copy()
    data_2018['month'] = data_2018['order_purchase_timestamp'].dt.strftime('%B')
    data_2018 = data_2018[['month', 'order_count', 'revenue']]
    
    return pesanan_bulanan_df

def create_jumlah_pesanan_product(df):
    jumlah_pesanan_product=df.groupby(by="product_category_name")['payment_value'].sum().reset_index().sort_values(by='payment_value', ascending=False)
    return jumlah_pesanan_product

def create_city_df(df):
    city_df=df.groupby(by="customer_city").customer_id.nunique().reset_index().sort_values(by="customer_id", ascending=False)
    city_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return city_df

def create_negara_df(df):
    negara_df=df.groupby(by="customer_state").customer_id.nunique().reset_index().sort_values(by="customer_id", ascending=False)
    negara_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return negara_df

def create_status_pengiriman_df(df):
    status_pengiriman_df=df.groupby(by="status_pengiriman").order_id.nunique().reset_index()
    status_pengiriman_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)
    return status_pengiriman_df

def create_payment_df(df):
    payment_df=df.groupby(by="payment_type").order_id.nunique().reset_index()
    payment_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)
    return payment_df

# Fungsi untuk membuat DataFrame rata-rata waktu pengiriman berdasarkan negara
def create_rata_rata_waktu_pengiriman_negara(df):
    # Pastikan kolom 'order_delivered_customer_date' dalam format datetime
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    
    # Hitung waktu pengiriman
    df['waktu_pengiriman'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    
    rata_rata_waktu_pengiriman_negara = df.groupby('customer_state')['waktu_pengiriman'].mean().reset_index()
    rata_rata_waktu_pengiriman_negara.sort_values(by='waktu_pengiriman', ascending=False, inplace=True)
    
    return rata_rata_waktu_pengiriman_negara

all_df=pd.read_csv("ecommerce_data.csv")

# Mengubah kolom 'order_purchase_timestamp' menjadi datetime
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# Sidebar untuk memilih rentang tanggal
with st.sidebar:
    st.write("Silahkan Filter Data")
    start_date = st.sidebar.date_input("Tanggal Mulai", value=pd.to_datetime('2018-01-01'))
    end_date = st.sidebar.date_input("Tanggal Akhir", value=pd.to_datetime('2018-12-31'))

    # Filter DataFrame berdasarkan rentang tanggal
    filtered_df = all_df[(all_df['order_purchase_timestamp'] >= pd.Timestamp(start_date)) & 
                        (all_df['order_purchase_timestamp'] <= pd.Timestamp(end_date))]

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

# Menampilkan header
st.header("E-Commerce Dashboard 🛒")

# Menggunakan DataFrame yang sudah difilter
pesanan_bulanan_df = create_pesanan_bulanan_df(filtered_df)
jumlah_pesanan_product = create_jumlah_pesanan_product(filtered_df)
city_df = create_city_df(filtered_df)
negara_df = create_negara_df(filtered_df)
status_pengiriman_df = create_status_pengiriman_df(filtered_df)
payment_df = create_payment_df(filtered_df)
rata_rata_waktu_pengiriman_negara = create_rata_rata_waktu_pengiriman_negara(filtered_df)



