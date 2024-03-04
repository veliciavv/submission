import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
#sns.set(style='dark')

def cust_total(df):
    total_customer = df['customer_id'].nunique()
    return total_customer

def rate_total(df):
    total_rating = df['review_score'].mean()
    return round(total_rating, 1)

def order_total(df):
    total_orders = df['order_id'].nunique()
    return total_orders

def revenue_total(df):
    total_revenue = df['payment_value'].sum()
    return round(total_revenue,2)

def revenue_monthly(df):
    order_bulanan = df.resample(rule='M', on='order_purchase_timestamp').agg({
    "order_id": "nunique",
    "payment_value": "sum"
    })
    order_bulanan.index = order_bulanan.index.strftime('%Y-%m')
    order_bulanan = order_bulanan.reset_index()
    order_bulanan.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return order_bulanan

def top_category(df):
    most_order_item = df["product_category_name"].value_counts()
    return most_order_item

def create_rfm_df(df):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    rfm_analysis = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "payment_value": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_analysis.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
 
    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_analysis["max_order_timestamp"] = rfm_analysis["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_analysis["recency"] = rfm_analysis["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_analysis.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_analysis

## Load main_data.csv ##
all_df = pd.read_csv("https://raw.githubusercontent.com/veliciavv/submission/main/dashboard/main_data.csv")

datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])


## SIDE BAR ##
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    st.image("https://static.vecteezy.com/system/resources/previews/006/547/178/original/creative-modern-abstract-ecommerce-logo-design-colorful-gradient-online-shopping-bag-logo-design-template-free-vector.jpg")
    
    # # Mengambil start_date & end_date dari date_input
    # start_date, end_date = st.date_input(
    #     label='Rentang Waktu',min_value=min_date,
    #     max_value=max_date,
    #     value=[min_date, max_date]
    # )
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    available_years = range(start_date.year, end_date.year + 1)
    selected_years = st.multiselect('Pilih Tahun', available_years, default=available_years)
    
    st.caption("Copyright (c) veliciavv 2024")


## MAIN ##
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]  

total_customer = cust_total(main_df)
total_rating = rate_total(main_df)
total_orders = order_total(main_df)
total_revenue = revenue_total(main_df)
order_bulanan = revenue_monthly(main_df)
most_order_item = top_category(main_df)
rfm_analysis = create_rfm_df(main_df)

## MAIN PAGE ##
st.header('E-commerce Analysis 🛒✨')

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("Total Customer")
    st.info(total_customer, icon="👥")
with col2:
    st.subheader("Average Ratings")
    st.info(total_rating, icon="🌟")
with col3:
    st.subheader("Total Orders")
    st.info(total_orders, icon="🛒")
with col4:
    st.subheader("Total Revenue")
    st.info(total_revenue, icon="💰")

tab1, tab2, tab3 = st.tabs(["Revenue", "Kategori Produk", "RFM Analysis"])

with tab1:    
    st.header("Revenue dalam 3 tahun terakhir")

    x_values = order_bulanan["order_purchase_timestamp"]
    y_values = order_bulanan["revenue"]
    y_ticks = np.arange(0, order_bulanan["revenue"].max() + 100000, 100000)

    plt.figure(figsize=(10, 5))
    plt.plot(x_values, y_values, marker='o')

    plt.title("Total Revenue per Month (2016-2018)", loc="center", fontsize=20)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Revenue", fontsize=12)
    plt.yticks(y_ticks, [f"{revenue:.0f}" for revenue in y_ticks], fontsize=10)
    plt.xticks(rotation=70, fontsize=10)

    st.pyplot(plt)

with tab2:
    st.header("Kategori Produk Terlaris")
    categories = most_order_item.head(15).index
    counts = most_order_item.head(15).values

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(categories, counts, color='skyblue')

    ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=10)
    ax.set_yticklabels(ax.get_yticks(), fontsize=10)
    ax.set_xlabel('Product Categories', fontsize=12)
    ax.set_ylabel('Number of Orders', fontsize=12)
    ax.set_title('Top 15 Product Categories by Number of Orders', fontsize=14)

    st.pyplot(fig)
    
with tab3:
    st.header("RFM Analysis")
    sorted_rfm_recency = rfm_analysis.sort_values(by="recency", ascending=True)
    sorted_rfm_frequency = rfm_analysis.sort_values(by="frequency", ascending=False)
    sorted_rfm_monetary = rfm_analysis.sort_values(by="monetary", ascending=False)

    st.write("Top 5 Customers by Recency:")
    st.dataframe(sorted_rfm_recency.head())
    
    st.write("Top 5 Customers by Frequency:")
    st.dataframe(sorted_rfm_frequency.head())
    
    st.write("Top 5 Customers by Monetary:")
    st.dataframe(sorted_rfm_monetary.head())
    
    st.subheader("Best Customer based on RFM Analysis")
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(8, 15))

    colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

    # Barplot untuk Recency
    sns.barplot(x="recency", y="customer_id", data=rfm_analysis.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
    ax[0].tick_params(axis ='x', labelsize=15)  # Menggunakan labelsize

    # Barplot untuk Frequency
    sns.barplot(x="frequency", y="customer_id", data=rfm_analysis.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title("By Frequency", loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=15)  # Menggunakan labelsize

    # Barplot untuk Monetary
    sns.barplot(x="monetary", y="customer_id", data=rfm_analysis.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title("By Monetary", loc="center", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=15)

    st.pyplot(fig)