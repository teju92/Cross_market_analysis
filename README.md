# Cross-Market Analysis: Crypto, Oil & Stocks

A data analysis application that provides insights into the relationships between cryptocurrency, oil, and stock markets using SQL database integration and an interactive Streamlit dashboard.

## Overview

This project enables users to analyze and visualize correlations and trends across different financial markets, helping identify potential market interdependencies and trading opportunities.

## Features

- **Multi-Market Data Analysis**: Compare trends across cryptocurrency, oil, and stock markets
- **SQL Database Integration**: Efficient data storage and retrieval using MySQL
- **Interactive Dashboard**: User-friendly Streamlit interface for data exploration
- **Data Processing**: Powered by Pandas for robust data manipulation and analysis

### Core Technologies
- **Python**: Core programming language
- **MySQL**: Relational database management
- **Pandas**: Data manipulation and analysis
- **Streamlit**: Interactive web application framework

### Data Sources & APIs
- **CoinGecko API**: Cryptocurrency market data
- **Yahoo Finance API**: Stock market indices (S&P 500, NASDAQ, NSEI)
- **Oil Prices Dataset**: Historical daily oil price data (2020-2026)

### Data Sources & APIs
- **CoinGecko API**: Cryptocurrency market data
- **Yahoo Finance API**: Stock market indices (S&P 500, NASDAQ, NSEI)
- **Oil Prices Dataset**: Historical daily oil price data (2020-2026)

### Technical Concepts
- Data Collection & ETL
- Database Design & Query Optimization
- Relational Databases
- Data Integration & Cleaning
- Financial Data Analysis

## Prerequisites

Before running this application, ensure you have the following installed:

- Python 3.7 or higher
- MySQL Server
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cross-market-analysis.git
cd cross-market-analysis
```

2. Install required Python libraries:
```bash
pip install pandas
mysql-connector-python
streamlit

```

3. Set up your MySQL database:
   - Create a database for the project
   - Update database connection settings in the configuration file

## Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided local URL (typically `http://localhost:8501`)

3. Use the interactive interface to:
   - Query market data
   - Visualize trends and correlations
   - Analyze cross-market relationships

## Project Structure
```
cross-market-analysis/
├── app.py                 # Main Streamlit application
├── database/              
│   ├── connection.py      # MySQL connection handler
│   ├── queries.py         # SQL query functions
│   └── schema.sql         # Database schema definitions
├── data/                  # Data storage and processing
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Database Schema

The MySQL database consists of the following tables:

### Cryptocurrencies table
```sql
CREATE TABLE cryptocurrencies (
        id VARCHAR(50) PRIMARY KEY,
        `rank` INT,
        symbol VARCHAR(10),
        name VARCHAR(100),
        current_price DECIMAL(18, 6),
        market_cap BIGINT,
        total_volume BIGINT,
        circulating_supply DECIMAL(38, 6),
        total_supply DECIMAL(38, 6),
        ath DECIMAL(18, 6),
        atl DECIMAL(18, 6),
        `date` DATE
);
```

###Historical Prices Table
```sql
CREATE TABLE historical_Prices (
        coin_id VARCHAR(50),
        `date` DATE,
        price_usd DECIMAL(18, 6),
        PRIMARY KEY (coin_id, `date`), 
        CONSTRAINT fk_coin 
            FOREIGN KEY (coin_id) 
            REFERENCES Cryptocurrencies(id)
);
```

### Oil Table
```sql
CREATE TABLE oil_prices(
        `date` DATE PRIMARY KEY,
        Price DECIMAL(18, 6)
);
```

### Stocks Table
```sql
 CREATE TABLE stock_prices(
        `date` DATE ,
        Ticker VARCHAR(20),
        Open DECIMAL(18, 6),
        High DECIMAL(18, 6),
        Low DECIMAL(18, 6),
        Close DECIMAL(18, 6),
        Volume BIGINT
);
```

### Relationships
- All tables are linked by the `date` field for cross-market analysis
- Indexes are created on `date` and `symbol` columns for optimized queries
## Acknowledgments

- Data sources for cryptocurrency, oil, and stock market information
- Streamlit community for the excellent framework
- Contributors and users of this project
