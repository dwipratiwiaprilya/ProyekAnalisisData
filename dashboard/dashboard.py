import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


sns.set(style='dark')
sns.set(style='darkgrid')  # Seaborn dark theme
plt.style.use('dark_background')  # Matplotlib dark background


def create_pesanan_bulanan_df(df):
    pesanan_bulanan_df = df.resample('M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()

    pesanan_bulanan_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    pesanan_bulanan_df['month'] = pesanan_bulanan_df['order_purchase_timestamp'].dt.strftime('%B')
    
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
    payment_df = df.groupby(by="payment_type")['order_id'].nunique().reset_index()
    payment_df.rename(columns={"order_id": "order_count"}, inplace=True)
    return payment_df

def create_rata_rata_waktu_pengiriman_negara(df):
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    df['waktu_pengiriman'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    rata_rata_waktu_pengiriman_negara = df.groupby('customer_state')['waktu_pengiriman'].mean().reset_index()
    rata_rata_waktu_pengiriman_negara.sort_values(by='waktu_pengiriman', ascending=False, inplace=True)
    return rata_rata_waktu_pengiriman_negara

def create_rfm(df):
    rfm = df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max",
    "order_id": "nunique",
    "payment_value": "sum"
})
    rfm.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    # Menghitung recency
    rfm["max_order_timestamp"] = pd.to_datetime(rfm["max_order_timestamp"])
    recent_date = df["order_purchase_timestamp"].max()
    # Hitung recency dalam hari
    rfm["recency"] = (recent_date - rfm["max_order_timestamp"]).dt.days
    return rfm

def create_rfm(df):
    rfm = df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max",
    "order_id": "nunique",
    "payment_value": "sum"
})
    rfm.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    # Menghitung recency
    rfm["max_order_timestamp"] = pd.to_datetime(rfm["max_order_timestamp"])
    recent_date = df["order_purchase_timestamp"].max()
    # Hitung recency dalam hari
    rfm["recency"] = (recent_date - rfm["max_order_timestamp"]).dt.days
    return rfm

def segment_customer(df):
  if df['RFM_Score'] >= 250:
    return 'Champion'
  elif df['RFM_Score'] >= 200:
    return 'Loyal Customer'
  elif df['RFM_Score'] >= 150:
    return 'Potential Loyalist'
  elif df['RFM_Score'] >= 100:
    return 'Recent Customer'
  elif df['RFM_Score'] >= 50:
    return 'Promising'
  elif df['RFM_Score'] >= 1:
    return 'Customer Need Attention'
  else:
    return 'Lost'



# Load the data
all_df = pd.read_csv("dashboard/data.csv")

# Convert the 'order_purchase_timestamp' column to datetime
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# Sidebar for date range selection
with st.sidebar:
    st.image("https://github.com/dwipratiwiaprilya/ProyekAnalisisData/blob/main/assets/logo__2_-removebg-preview.png?raw=true")
    st.markdown("<h1 style='text-align: center;'>Please Filter Data</h1>", unsafe_allow_html=True)
    start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime('2018-01-01'))
    end_date = st.sidebar.date_input("End Date", value=pd.to_datetime('2018-12-31'))

    # Filter the DataFrame based on the selected date range
    filtered_df = all_df[(all_df['order_purchase_timestamp'] >= pd.Timestamp(start_date)) & 
                        (all_df['order_purchase_timestamp'] <= pd.Timestamp(end_date))]
    

# Create DataFrames
pesanan_bulanan_df = create_pesanan_bulanan_df(filtered_df)
jumlah_pesanan_product = create_jumlah_pesanan_product(filtered_df)
city_df = create_city_df(filtered_df)
negara_df = create_negara_df(filtered_df)
status_pengiriman_df = create_status_pengiriman_df(filtered_df)
payment_df = create_payment_df(filtered_df)
rata_rata_waktu_pengiriman_negara = create_rata_rata_waktu_pengiriman_negara(filtered_df)
rfm=create_rfm(filtered_df)

# Create RFM scores here, after `rfm` is defined
rfm['RFM_Score'] = rfm['recency'] + rfm['frequency'] + rfm['monetary']

# Sort and segment customers based on RFM scores
sorted_by_rfm = rfm.sort_values(by='RFM_Score', ascending=False)
sorted_by_rfm['Segment'] = sorted_by_rfm.apply(segment_customer, axis=1)

# Count customers in each segment
segment_counts = sorted_by_rfm.groupby('Segment')['customer_id'].nunique().reset_index()
sorted_segments = segment_counts.sort_values(by='Segment')




# Display header
st.header("E-Commerce Public Dataset Dashboard 🛒")

# Create tabs
tabs = st.tabs(["Orders", "Products", "Customers","RFM Analysis"])

# Orders Tab
with tabs[0]:
    col1, col2, col3 = st.columns(3)

    with col1:
        total_orders = filtered_df['order_id'].nunique()
        st.metric("Total Orders", total_orders, "The total number of unique orders placed.")

    with col2:
        total_revenue = filtered_df['payment_value'].sum()
        total_revenue_display = format_currency(total_revenue / 1000, 'USD') + "K"  # Display in thousands
        st.metric("Total Revenue", total_revenue_display, "The total revenue generated from all orders.")

    with col3:
        average_delivery_time = (filtered_df['order_delivered_customer_date'] - filtered_df['order_purchase_timestamp']).mean().days
        st.metric("Average Delivery Time (days)", average_delivery_time, "The average time taken to deliver orders to customers.")


    # Interactive Line Chart using Plotly
    if 'month' in pesanan_bulanan_df.columns:
        fig = px.line(pesanan_bulanan_df, x='month', y='order_count', 
                    title="Monthly Orders",
                    markers=True,)
        fig.update_layout(title_text='Monthly Orders', title_x=0.5)
        st.plotly_chart(fig)
    else:
        st.write("Column 'month' not found in the monthly orders DataFrame.")


    # Create a pie chart for order status percentages
    colors = ["#4379F2", "#F1F1F1"]

    # Interactive Pie Chart using Plotly
    fig = px.pie(status_pengiriman_df, values='order_count', names='status_pengiriman', 
                title='Order Status Percentages', color_discrete_sequence=colors)
    st.plotly_chart(fig)
    
    # Create an interactive bar chart for payment types using Plotly
    payment_fig = px.bar(
    payment_df.sort_values(by="order_count", ascending=False).head(5),
    x='order_count',
    y='payment_type',
    title='Payment Types Commonly Used by Customers',
    orientation='h',  # Corrected from '' to 'h' for horizontal bars
    color='payment_type', 
    color_discrete_sequence=["#4379F2", "#F1F1F1", "#F1F1F1", "#F1F1F1"]  # Maintain your color scheme
)

    # Update layout for better presentation
    payment_fig.update_layout(title_x=0.5, yaxis_title=None, xaxis_title=None)
    payment_fig.update_traces(marker=dict(line=dict(width=1, color='black')))  # Optional: Add borders to bars for better visibility

    # Display the Plotly chart in Streamlit
    st.plotly_chart(payment_fig)

    
    # Create an interactive bar chart for average delivery time by state
    average_delivery_fig = px.bar(
        rata_rata_waktu_pengiriman_negara,
        x='customer_state',
        y='waktu_pengiriman',
        title='Average Delivery Time for Each State',
        labels={'customer_state': 'State', 'waktu_pengiriman': 'Average Delivery Time (days)'},
        text='waktu_pengiriman',
        color='waktu_pengiriman',
        color_continuous_scale='Blues'
    )

    average_delivery_fig.update_layout(
        xaxis_title='State',
        yaxis_title='Average Delivery Time (days)',
        title_x=0.5,
        xaxis_tickangle=-45
    )

    st.plotly_chart(average_delivery_fig)



# Products Tab
with tabs[1]:
    col1, col2 = st.columns(2)

    with col1:
        # Total Products Sold
        total_products_sold = filtered_df['order_id'].count()
        st.metric("Total Products Sold", total_products_sold, "Total units sold across all product categories.")

    with col2:
        # Total Revenue by Products
        total_revenue_products = filtered_df['payment_value'].sum()
        
        # Average Price per Product
        average_price = total_revenue_products / total_products_sold if total_products_sold > 0 else 0
        st.metric("Average Price per Product", format_currency(average_price, 'USD'), "Average selling price of products.")
        # Check if there is enough data to plot
    if not jumlah_pesanan_product.empty and len(jumlah_pesanan_product) > 5:

        # Create two subplots side by side
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

        colors = ["#4379F2", "#C7C8CC", "#C7C8CC", "#C7C8CC", "#C7C8CC"]

        # Products with Highest Revenue
        sns.barplot(x="payment_value", y="product_category_name", data=jumlah_pesanan_product.head(5), palette=colors, ax=ax[0])
        ax[0].set_ylabel(None)  # Remove y-axis label
        ax[0].set_xlabel(None)  # Remove x-axis label
        ax[0].set_title("Products Generating the Highest Revenue", loc="center", fontsize=18)
        ax[0].tick_params(axis='y', labelsize=15)  # Adjust y-axis label size

        # Products with Lowest Revenue
        sns.barplot(x="payment_value", y="product_category_name", data=jumlah_pesanan_product.sort_values(by="payment_value", ascending=True).head(5), palette=colors, ax=ax[1])
        ax[1].set_ylabel(None)
        ax[1].set_xlabel(None)
        ax[1].invert_xaxis()  # Invert the x-axis for the second chart
        ax[1].yaxis.set_label_position("right")  # Move the y-axis label to the right
        ax[1].yaxis.tick_right()  # Move the ticks to the right side
        ax[1].set_title("Products Generating the Lowest Revenue", loc="center", fontsize=18)
        ax[1].tick_params(axis='y', labelsize=15)  # Adjust y-axis label size

        # Add a main title
        plt.suptitle("Comparison of Products Generating the Highest and Lowest Revenue", fontsize=21)

        # Display the plot in Streamlit
        st.pyplot(fig)

    else:
        st.write("Not enough data to display the bar plots for product revenues.")

    
    # Dynamic Filter for Product Categories
    product_categories = filtered_df['product_category_name'].unique()
    selected_category = st.selectbox('Select Product Category', product_categories)

    # Filter DataFrame based on selection
    filtered_by_category_df = filtered_df[filtered_df['product_category_name'] == selected_category]

    # Display filtered data
    st.write(f"Displaying data for category: {selected_category}")
    st.dataframe(filtered_by_category_df)


# Customers Tab
with tabs[2]:    
    # Create columns for metrics
    col1, col2 = st.columns(2)

    with col1:
        # Total Customers
        total_customers = filtered_df['customer_id'].nunique()
        st.metric("Total Customers", total_customers, "Total number of unique customers.")

    with col2:
        # Average Spending per Customer
        average_spending = filtered_df['payment_value'].mean()
        st.metric("Average Spending per Customer", format_currency(average_spending, 'USD'), "Average revenue generated per customer.")


    # Interactive Bar Chart using Plotly
    fig = px.bar(city_df.head(5), x='customer_count', y='customer_city', 
                title='Number of Customers by City', 
                orientation='h', color_discrete_sequence=colors)
    fig.update_layout(yaxis_title=None, xaxis_title=None, title_x=0.5)
    st.plotly_chart(fig)


    # Interactive Bar Chart using Plotly
    fig = px.bar(negara_df.head(5), x='customer_count', y='customer_state', 
                title='Number of Customers by State', 
                orientation='h', color_discrete_sequence=colors)
    fig.update_layout(yaxis_title=None, xaxis_title=None, title_x=0.5)
    st.plotly_chart(fig)
    
with tabs[3]: 
    # Recency Bar Plot
    recency_data = rfm.sort_values(by="recency", ascending=True).head(5)
    recency_fig = px.bar(
        recency_data, 
        x='customer_id', 
        y='recency', 
        title='Customers with Highest Recency (days)', 
        color_discrete_sequence=["#4379F2"]
    )
    recency_fig.update_layout(title_x=0.5)

    # Display Recency Chart in Streamlit
    st.plotly_chart(recency_fig)

    # Frequency Bar Plot
    frequency_data = rfm.sort_values(by="frequency", ascending=False).head(5)
    frequency_fig = px.bar(
        frequency_data, 
        x='customer_id', 
        y='frequency', 
        title='Customers with Highest Frequency', 
        color_discrete_sequence=["#4379F2"]
    )
    frequency_fig.update_layout(title_x=0.5)

    # Display Frequency Chart in Streamlit
    st.plotly_chart(frequency_fig)

    # Monetary Bar Plot
    monetary_data = rfm.sort_values(by="monetary", ascending=False).head(5)
    monetary_fig = px.bar(
        monetary_data, 
        x='customer_id', 
        y='monetary', 
        title='Customers with Highest Monetary Value', 
        color_discrete_sequence=["#4379F2"]
    )
    monetary_fig.update_layout(title_x=0.5)

    # Display Monetary Chart in Streamlit
    st.plotly_chart(monetary_fig)
    

    colors = ["#B7B7B7", "#4379F2", "#4379F2", "#B7B7B7"]

    # Create a bar plot for customer segments distribution
    fig_segment = plt.figure(figsize=(10, 6))
    sns.barplot(x='customer_id', y='Segment', data=segment_counts.sort_values(by="Segment"), palette=colors)

    plt.title('Customer Segments Distribution', fontsize=16)
    plt.xlabel(None)
    plt.ylabel(None)
    plt.tick_params(axis='y', labelsize=12)

    # Display the segment distribution
    segment_counts['Segment'] = pd.Categorical(
        segment_counts['Segment'],
        categories=["Champion", "Loyal Customer", "Potential Loyalist", "Recent Customer", "Promising", "Customer Need Attention", "Lost"],
        ordered=True
    )

    # Bar plot for customer segments distribution
    fig_segment = plt.figure(figsize=(10, 6))
    sns.barplot(x='customer_id', y='Segment', data=sorted_segments, palette=colors)

    plt.title('Customer Segments Distribution', fontsize=16)
    plt.xlabel(None)
    plt.ylabel(None)
    plt.tick_params(axis='y', labelsize=12)

    # Display the segment distribution in Streamlit
    st.pyplot(fig_segment)
    
    

