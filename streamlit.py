import streamlit as st
import datetime
import pandas as pd
import numpy as py
import sys
import yfinance as yf
import streamlit as st
import mysql.connector
import requests
import time
import duckdb
import plotly.express as px


@st.cache_data  # This makes your app much faster!
def load_data(query):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="jujo",
        database="crypto_analysis",
        auth_plugin='mysql_native_password'
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df  # Now 'return' is inside a function, so it works!


try:
    #Loading data
    cryptocurrencies = load_data("SELECT * FROM cryptocurrencies")
    historical_Prices = load_data("SELECT * FROM historical_prices")
    oil_prices = load_data("SELECT * FROM oil_prices")
    stock_prices = load_data("SELECT * FROM stock_prices")
except Exception as e:
    st.error(f"Database Connection Error: {e}")



st.title('💰 Cross-Market Analysis')
st.markdown('#### Crypto, Oil, & Stock Prices | SQL Powered Analysis')

with st.sidebar:
    st.title("📌 Navigation")
    page = st.radio("Go to:", ["📈 Market Overview", "🔍 SQL Query Runner","Top 5 Crypto Analysis"])

if page == "📈 Market Overview":
    st.title('📊 Cross-Market Overview')
    
    stock_prices.columns = [c.lower() for c in stock_prices.columns]
    oil_prices.columns = [c.lower() for c in oil_prices.columns]
    historical_Prices.columns = [c.lower() for c in historical_Prices.columns]


    stock_prices['date'] = pd.to_datetime(stock_prices['date'])
    oil_prices['date'] = pd.to_datetime(oil_prices['date'])
    historical_Prices['date'] = pd.to_datetime(historical_Prices['date'])

    # --- 2. DATE FILTER UI ---
    col_start, col_end = st.columns(2)
    with col_start:
        start_d = st.date_input("Start Date", value=stock_prices['date'].min().date())
    with col_end:
        end_d = st.date_input("End Date", value=stock_prices['date'].max().date())

    # --- 3. FILTERING ---
    mask_stock = (stock_prices['date'].dt.date >= start_d) & (stock_prices['date'].dt.date <= end_d)
    mask_oil = (oil_prices['date'].dt.date >= start_d) & (oil_prices['date'].dt.date <= end_d)
    mask_crypto = (historical_Prices['date'].dt.date >= start_d) & (historical_Prices['date'].dt.date <= end_d)

    f_stock = stock_prices.loc[mask_stock]
    f_oil = oil_prices.loc[mask_oil]
    f_crypto = historical_Prices.loc[mask_crypto] 

    # --- 4. METRIC CALCULATIONS ---
    btc_val = f_crypto[f_crypto['coin_id'] == 'bitcoin']['price_usd'].mean()
    oil_avg = f_oil['price'].mean()
    sp_avg = f_stock[f_stock['ticker'] == 'GSPC']['close'].mean()
    nifty_avg = f_stock[f_stock['ticker'] == 'NSEI']['close'].mean()

    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Bitcoin (Avg)", f"{btc_val:,.2f}" if not pd.isna(btc_val) else "N/A")
    m2.metric("Oil Avg", f"${oil_avg:,.2f}" if not pd.isna(oil_avg) else "N/A")
    m3.metric("🇺🇸 S&P 500 Avg", f"{sp_avg:,.2f}" if not pd.isna(sp_avg) else "N/A")
    m4.metric("🇮🇳 NIFTY Avg", f"{nifty_avg:,.2f}" if not pd.isna(nifty_avg) else "N/A")

    # --- 5. SNAPSHOT (DuckDB) ---
    st.markdown("---")
    st.markdown("### 🗓️ Daily Multi-Asset Snapshot")
    
    join_query = """
        SELECT 
            CAST(COALESCE(btc.date, oil.date, sp.date, nfy.date) AS DATE) AS "Date",
            btc.price_usd AS Bitcoin,
            oil.price AS Crude_Oil,
            sp.close AS "S&P 500",
            nfy.close AS "Nifty 50"
        FROM (SELECT date, price_usd FROM f_crypto WHERE coin_id = 'bitcoin') btc
        FULL OUTER JOIN f_oil oil ON btc.date = oil.date
        FULL OUTER JOIN (SELECT date, close FROM f_stock WHERE ticker = 'GSPC') sp ON COALESCE(btc.date, oil.date) = sp.date
        FULL OUTER JOIN (SELECT date, close FROM f_stock WHERE ticker = 'NSEI') nfy ON COALESCE(btc.date, oil.date, sp.date) = nfy.date
        ORDER BY "Date" DESC
    """
    
    try:
        df_final = duckdb.query(join_query).df()
        st.dataframe(df_final, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Snapshot Error: {e}")

elif page == "🔍 SQL Query Runner":
    st.title("🔎 SQL Query Runner")
    st.markdown("###### Predefined analytical SQL queries (Full Dataset)")
    
    
    SAVED_QUERIES = {
        "1.Top 3 cryptocurrencies by market cap": """
            SELECT name, market_cap, current_price FROM cryptocurrencies ORDER BY market_cap DESC LIMIT 3
        """,
        "2.Coins with > 90% circulating supply": """
            SELECT name, circulating_supply, total_supply, 
            (circulating_supply / total_supply) * 100 AS supply_percentage
            FROM cryptocurrencies 
            WHERE (circulating_supply / total_supply) > 0.9
            ORDER BY supply_percentage DESC
        """,
        "3.Coins within 10% of their ATH": """
            SELECT name, current_price, ath, 
            ((current_price / ath) * 100) AS percent_of_ath
            FROM cryptocurrencies
            WHERE current_price >= (ath * 0.9)
            ORDER BY percent_of_ath DESC
        """,
        "4.The average rank for high volume coins": """
             SELECT 
            AVG("rank") as average_rank,  -- Use double quotes here
            COUNT(*)  as coin_count
            FROM cryptocurrencies
            WHERE total_volume > 1000000000
        """,
            
        "5.The single most recently updated record": """
            SELECT * FROM cryptocurrencies 
            ORDER BY last_updated DESC 
            LIMIT 1
        """,
         "6. Average Daily Price for Ethereum":"""
            SELECT 
            coin_id,
            "date", 
            price_usd 
            FROM historical_Prices
            where coin_id = 'bitcoin' 
            ORDER BY date DESC LIMIT 1
        """,
        "7. Average value for each day":""" 
            SELECT 
            coin_id, 
            "date", 
            AVG(price_usd) as average_daily_price 
            FROM historical_Prices
            WHERE coin_id = 'ethereum' AND "date" >= current_date - INTERVAL 1 YEAR
            GROUP BY "date", coin_id
            ORDER BY "date" DESC
        """,
        "8. Daily price trend of Bitcoin in April 2025": """
            SELECT 
            coin_id, 
            AVG(price_usd) as avg_price, 
            MIN(price_usd) as min_price, 
            MAX(price_usd) as max_price
            FROM historical_Prices 
            WHERE coin_id = 'bitcoin'
            AND "date" >= '2025-04-01' 
            AND "date" <= '2025-04-31'
           GROUP BY coin_id
        """,
          "9. coin with the highest average price": """
            SELECT coin_id, 
            AVG(price_usd) AS avg_price
            FROM historical_Prices
            WHERE "date" >= current_date - INTERVAL 1 YEAR
            GROUP BY coin_id
            ORDER BY avg_price DESC
            LIMIT 1

        """,
        "10. % change in Bitcoin’s price": """
            SELECT "date", price_usd 
            FROM historical_Prices
            WHERE coin_id = 'bitcoin' 
            AND CAST("date" AS VARCHAR) LIKE '2025-09-%' 
            OR CAST("date" AS VARCHAR) LIKE '2025-09-%'
            ORDER BY "date" ASC
        """,
        "11. highest oil price": """
            SELECT "date", "Price" 
            FROM oil_prices
            ORDER BY "Price" DESC 
            LIMIT 1
        """,
        "12.Group data by year": """
            SELECT 
            YEAR("date") AS oil_year, 
            AVG("Price") AS avg_price 
            FROM oil_prices
            GROUP BY oil_year
            ORDER BY oil_year DESC
        """,
        "13.oil prices during COVID crash": """
            SELECT 
            "date", 
            "Price" 
            FROM oil_prices 
            WHERE CAST("date" AS VARCHAR) LIKE '2020-03-%' 
            OR CAST("date" AS VARCHAR) LIKE '2020-04-%'
            ORDER BY "date" DESC
        """,
        "14. Lowest price of oil": """
              SELECT 
              "date", "Price" 
               FROM oil_prices 
               ORDER BY "Price" ASC  
            LIMIT 1              
        """,
         "15. volatility of oil prices": """
              SELECT 
            YEAR("date") AS oil_year, 
            MIN("Price") AS min_price,
            MAX("Price") AS max_price,
            (MAX("Price") - MIN("Price")) AS price_spread
            FROM oil_prices 
            GROUP BY oil_year
            ORDER BY oil_year DESC             
        """,
        "16.Highest NASDAQ (^IXIC) Overall": """
            SELECT Date, Ticker, Close 
            FROM stock_prices
            WHERE Ticker = '^IXIC' 
            ORDER BY Close DESC 
            LIMIT 1
        """,
        "17.Get all stock prices": """
            SELECT * FROM stock_prices
        """,
        
        "18.Top 5 Volatile Days (GSPC)": """
            SELECT Date, Ticker, (High - Low) AS Difference 
            FROM stock_prices
            WHERE Ticker = '^GSPC' 
            ORDER BY Difference DESC 
            LIMIT 5
        """,
        "19.Get monthly average closing price for each ticker": """
            SELECT 
            strftime(Date, '%Y-%m') AS Month, 
            Ticker, 
            AVG(Close) AS Avg_close
            FROM stock_prices
            GROUP BY Month, Ticker
            ORDER BY Month DESC
        """,
        "20.Avg volume for NSEI ": """
            SELECT 
            Ticker, 
            AVG(Volume) AS Avg_Volume
            FROM df_stock
            WHERE Ticker = '^NSEI'
            GROUP BY Ticker
        """,
        "21.Compare Bitcoin vs Oil average ": """
             SELECT  
            AVG(h.price_usd) AS btc_avg, 
            AVG(o.price) AS oil_avg
            FROM historical_Prices h
            LEFT JOIN oil_prices o ON h.date = o.date
            WHERE h.coin_id = 'bitcoin' 
            AND h.date >= '2025-01-01' 
            AND h.date <= '2025-12-31';
        """,  
         "22.Bitcoin moves with S&P 500 ": """
            SELECT  
            CAST(btc.date AS DATE) AS "Date",
            btc.price_usd AS btc_price,
            sp.close AS sp500_close
            FROM historical_Prices btc
            INNER JOIN stock_prices sp ON btc.date = sp.date
            WHERE btc.coin_id = 'bitcoin' 
            AND sp.ticker = 'GSPC'
            AND btc.date >= '2024-01-01'
            ORDER BY btc.date ASC
        """, 
        
        "23.Ethereum and NASDAQ daily prices ": """
            SELECT 
            c.date, 
            c.price_usd AS ethereum_price, 
            s.close AS nasdaq_close
            FROM historical_Prices c
            JOIN stock_prices s ON c.date = s.date
            WHERE c.coin_id = 'ethereum' 
            AND s.ticker = 'IXIC' 
            AND YEAR(c.date) = 2025
            ORDER BY c.date;
        """,  
        "24.oil price spiked and compare with Bitcoin price change ": """
            WITH OilChanges AS (
            SELECT 
            "date", 
            Price,
            LAG(Price) OVER (ORDER BY "date") AS prev_oil_price,
            ((Price - LAG(Price) OVER (ORDER BY "date")) / LAG(Price) OVER (ORDER BY "date")) * 100 AS oil_pct_change
            FROM oil_prices
            ),
            BTCChanges AS (
            SELECT 
            "date", 
            price_usd,
            ((price_usd - LAG(price_usd) OVER (ORDER BY "date")) / LAG(price_usd) OVER (ORDER BY "date")) * 100 AS btc_pct_change
            FROM historical_Prices
            WHERE coin_id = 'bitcoin'
            )
            SELECT 
            o."date",
            o.oil_pct_change AS oil_spike_pct,
            b.btc_pct_change AS btc_response_pct
            FROM OilChanges o
            JOIN BTCChanges b ON o."date" = b."date"
            WHERE o.oil_pct_change > 5  
            ORDER BY o.oil_pct_change DESC;
            
        """,   
        "25.top 3 coins daily price trend vs Nifty ": """
            SELECT 
            h.date, 
            h.coin_id, 
            h.price_usd AS crypto_price, 
            o.Price AS oil_price, 
            s.Close AS nifty_price
            FROM historical_Prices h
            LEFT JOIN oil_prices o ON h.date = o.date
            LEFT JOIN stock_prices s ON h.date = s.date AND s.Ticker = 'NSEI'
            WHERE h.coin_id IN ('bitcoin', 'ethereum', 'tether')
            ORDER BY h.date ASC;
        """,
        "26.stock prices (^GSPC) with crude oil prices  ": """
            SELECT 
            h."date",
            h.price_usd AS btc_price,
            o.Price AS oil_price
            FROM historical_Prices h
            JOIN oil_prices o ON h."date" = o."date"
            WHERE h.coin_id = 'bitcoin'
            ORDER BY h."date" ASC;
        """,
        "27.Bitcoin closing price with crude oil closing price  ": """
            SELECT 
            h."date",
            h.price_usd AS btc_price,
            o.Price AS oil_price
            FROM historical_Prices h
            JOIN oil_prices o ON h."date" = o."date"
            WHERE h.coin_id = 'bitcoin'
            ORDER BY h.`date` ASC;
        """,
        "28.NASDAQ IXIC with Ethereum price trends  ": """
            SELECT 
            s."date",
            s.Close AS nasdaq_close,
            h.price_usd AS eth_price,
            ((s.Close - LAG(s.Close) OVER (ORDER BY s."date")) / LAG(s.Close) OVER (ORDER BY s."date")) * 100 AS nasdaq_pct_change,
            ((h.price_usd - LAG(h.price_usd) OVER (ORDER BY h."date")) / LAG(h.price_usd) OVER (ORDER BY h."date")) * 100 AS eth_pct_change
            FROM stock_prices s
            JOIN historical_Prices h ON s."date" = h."date"
            WHERE s.Ticker = 'IXIC' AND h.coin_id = 'ethereum'
            ORDER BY s."date" ASC;
        """,
        "29.top 3 crypto coins with stock indices   ": """
            SELECT 
            h."date",
            h.coin_id,
            h.price_usd AS crypto_price,
            s_nasdaq.Close AS nasdaq_close,
            s_sp500.Close AS sp500_close
            FROM historical_Prices h

            LEFT JOIN stock_prices s_nasdaq 
            ON h."date" = s_nasdaq."date" AND s_nasdaq.Ticker = 'IXIC'

            LEFT JOIN stock_prices s_sp500 
            ON h."date" = s_sp500.`date` AND s_sp500.Ticker = 'GSPC'
            WHERE h.coin_id IN ('bitcoin', 'ethereum', 'tether')
            AND h."date" BETWEEN '2025-01-01' AND '2025-12-31'
            ORDER BY h."date" ASC, h.coin_id;
            ORDER BY s."date" ASC;
        """,
        "30.Multi-join: stock prices, oil prices, and Bitcoin prices ": """
            SELECT 
            h."date",
            h.price_usd AS btc_price,
            s.Close AS sp500_close,
            o.Price AS oil_price,
    -- Calculate Daily % Change for BTC to see correlation in volatility
            ((h.price_usd - LAG(h.price_usd) OVER (PARTITION BY h.coin_id ORDER BY h."date")) 
            / LAG(h.price_usd) OVER (PARTITION BY h.coin_id ORDER BY h."date")) * 100 AS btc_daily_return
            FROM historical_Prices h
            LEFT JOIN stock_prices s 
            ON h."date"` = s."date" AND s.Ticker = 'GSPC'
            LEFT JOIN oil_prices o 
            ON h."date" = o."date"
            WHERE h.coin_id = 'bitcoin'
            AND h."date" BETWEEN '2025-01-01' AND '2025-12-31'
            ORDER BY h."date" ASC;
"""

    }
    
    selected_query_name = st.selectbox("📌 Select a Query", options=list(SAVED_QUERIES.keys()))
    query_to_run = SAVED_QUERIES[selected_query_name]
    
    if st.button("▶ Run Query"):
        try:
            result_df = duckdb.query(query_to_run).to_df()
            st.success("Query executed successfully on full dataset!")
            st.dataframe(result_df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Error: {e}")
if page == "Top 5 Crypto Analysis":
    st.title("📊 Top Crypto Analysis")


    coin_options = {"Bitcoin": "bitcoin", "Ethereum": "ethereum", "Tether": "tether"}
    selected_name = st.selectbox("Step 1: Select a Cryptocurrency", list(coin_options.keys()))
    selected_id = coin_options[selected_name]


    historical_Prices.columns = [c.lower() for c in historical_Prices.columns]
    historical_Prices['date'] = pd.to_datetime(historical_Prices['date'])


    df_coin = historical_Prices[historical_Prices['coin_id'] == selected_id].copy()

    if not df_coin.empty:
        
        st.markdown("---")
        col_start, col_end = st.columns(2)
        with col_start:
            # st.date_input needs .date() objects
            start_d = st.date_input("Start Date", value=df_coin['date'].min().date())
        with col_end:
            end_d = st.date_input("End Date", value=df_coin['date'].max().date())


        mask = (df_coin['date'].dt.date >= start_d) & (df_coin['date'].dt.date <= end_d)
        analysis_df = df_coin.loc[mask]

 
        avg_price = analysis_df['price_usd'].mean()
        max_price = analysis_df['price_usd'].max()
        
        m1, m2 = st.columns(2)
        m1.metric(f"Avg {selected_name} Price", f"${avg_price:,.2f}")
        m2.metric(f"Max {selected_name} Price", f"${max_price:,.2f}")

       
        st.markdown("### 🗓️ Daily Price Table")
        

        query = """
            SELECT 
                date AS "Date",
                coin_id AS "Coin",
                price_usd AS "Price"
            FROM analysis_df
            ORDER BY date DESC
        """

        try:
            market_snapshot = duckdb.query(query).df()
            st.dataframe(
                market_snapshot,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Price": st.column_config.NumberColumn(format="$%.2f"),
                    "Date": st.column_config.DateColumn(format="YYYY-MM-DD")
                }
            )
            

            fig = px.line(analysis_df, x="date", y="price_usd", 
                          title=f"{selected_name} Price Trend ($)",
                          labels={"price_usd": "Price (USD)", "date": "Date"})
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:        
            st.error(f"Analysis Error: {e}")
    else:
        st.warning(f"No data found in database for {selected_name}. Ensure your historical_Prices table contains data for '{selected_id}'.")