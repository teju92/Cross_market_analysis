# Cross-Market Analysis: Crypto, Oil & Stocks

A data analysis application that provides insights into the relationships between cryptocurrency, oil, and stock markets using SQL database integration and an interactive Streamlit dashboard.

## Overview

This project enables users to analyze and visualize correlations and trends across different financial markets, helping identify potential market interdependencies and trading opportunities.

## Features

- **Multi-Market Data Analysis**: Compare trends across cryptocurrency, oil, and stock markets
- **SQL Database Integration**: Efficient data storage and retrieval using MySQL
- **Interactive Dashboard**: User-friendly Streamlit interface for data exploration
- **Data Processing**: Powered by Pandas for robust data manipulation and analysis

## Tech Stack

- **Python**: Core programming language
- **MySQL**: Database management
- **Pandas**: Data manipulation and analysis
- **Streamlit**: Interactive web application framework

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

### Crypto Table
```sql
CREATE TABLE crypto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    symbol VARCHAR(10),
    price DECIMAL(15, 2),
    volume BIGINT,
    market_cap DECIMAL(20, 2)
);
```

### Oil Table
```sql
CREATE TABLE oil (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    price DECIMAL(10, 2),
    volume BIGINT
);
```

### Stocks Table
```sql
CREATE TABLE stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    symbol VARCHAR(10),
    open_price DECIMAL(10, 2),
    close_price DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    volume BIGINT
);
```

### Relationships
- All tables are linked by the `date` field for cross-market analysis
- Indexes are created on `date` and `symbol` columns for optimized queries
## Acknowledgments

- Data sources for cryptocurrency, oil, and stock market information
- Streamlit community for the excellent framework
- Contributors and users of this project
