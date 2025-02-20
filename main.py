import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Pizza Sales Dashboard", page_icon="🍕", layout="wide")

st.markdown(
    "<h1 style='text-align: center; font-size: 36px;'>🍕 Pizza Sales Analysis</h1>",
    unsafe_allow_html=True
)

fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))

if fl is not None:
    df = pd.read_csv(fl)
else:
    df = pd.read_csv("A_year_of_pizza_sales_from_a_pizza_place_872_68.csv")

# Standardize column names
df.columns = df.columns.str.strip().str.lower()

# Rename and process date column if exists
if "date" in df.columns:
    df.rename(columns={"date": "order_date"}, inplace=True)
    df["order_date"] = pd.to_datetime(df["order_date"], errors='coerce')
else:
    st.error("Column 'date' not found in dataset.")

df.drop(columns=["unnamed: 0", "x"], errors='ignore', inplace=True)

col1, col2 = st.columns((2))

if "order_date" in df.columns:
    startDate = df["order_date"].min()
    endDate = df["order_date"].max()
    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))
    df = df[(df["order_date"] >= date1) & (df["order_date"] <= date2)].copy()
else:
    df = pd.DataFrame()

st.sidebar.header("Choose your filters:")

pizza_types = st.sidebar.multiselect("Pick your Pizza Type", df["name"].unique(), key="pizza_type")
pizza_sizes = st.sidebar.multiselect("Pick your Pizza Size", df["size"].unique(), key="pizza_size")
pizza_categories = st.sidebar.multiselect("Pick your Pizza Category", df["type"].unique(), key="pizza_category")

# Apply filters to DataFrame
df2 = df.copy()
if pizza_types:
    df2 = df2[df2["name"].isin(pizza_types)]
if pizza_sizes:
    df2 = df2[df2["size"].isin(pizza_sizes)]
if pizza_categories:
    df2 = df2[df2["type"].isin(pizza_categories)]

if not df.empty:
    category_df = df2.groupby(by=["type"], as_index=False)["price"].sum()

    with col1:
        st.subheader("Category-wise Sales")
        fig = px.bar(category_df, x="type", y="price", text=['${:,.2f}'.format(x) for x in category_df["price"]],
                     template="seaborn")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Pizza-wise Sales")
        fig = px.pie(df2, values="price", names="name", hole=0.5)
        st.plotly_chart(fig, use_container_width=True)

    df2["month_year"] = df2["order_date"].dt.strftime("%Y-%b")

    st.subheader('Time Series Analysis')
    linechart = df2.groupby("month_year")["price"].sum().reset_index()
    fig2 = px.line(linechart, x="month_year", y="price", labels={"price": "Revenue"}, height=500, template="gridon")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Hierarchical View of Sales using TreeMap")
    fig3 = px.treemap(df2, path=["type", "name", "size"], values="price", color="name")
    st.plotly_chart(fig3, use_container_width=True)

    chart1, chart2 = st.columns((2))
    with chart1:
        st.subheader('Category-wise Sales')
        fig = px.pie(df2, values="price", names="type", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with chart2:
        st.subheader('Pizza Size-wise Sales')
        fig = px.pie(df2, values="price", names="size", template="gridon")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader(":point_right: Month-wise Pizza Sales Summary")
    with st.expander("Summary_Table"):
        df_sample = df2[["name", "type", "size", "price"]].head()
        st.write(df_sample.style.background_gradient(cmap="Blues"))

    data1 = px.scatter(df2, x="price", y="size", size="price", title="Sales vs. Size Scatter Plot")
    st.plotly_chart(data1, use_container_width=True)

    with st.expander("View Data"):
        st.write(df2.iloc[:500, :].style.background_gradient(cmap="Oranges"))

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data=csv, file_name="Pizza_Sales.csv", mime="text/csv")