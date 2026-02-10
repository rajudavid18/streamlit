# 🔒 Fraud Detection Dashboard

A comprehensive Streamlit dashboard for real-time fraud detection and monitoring built on Snowflake data warehouse.

## 📊 Features

- **Executive Dashboard**: High-level KPIs and fraud metrics overview
- **Transaction Analysis**: Detailed transaction filtering and analysis
- **Customer Risk**: Risk segmentation and KYC compliance monitoring
- **Alert Management**: Real-time fraud alert tracking and prioritization
- **Geographic Analysis**: Location-based fraud pattern detection
- **Time Patterns**: Temporal fraud analysis (hourly, daily, weekend patterns)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Snowflake account with the GOLD schema tables
- Git (for deployment)

### Local Installation

1. **Clone or download this repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Snowflake credentials**
   
   Create a `.streamlit/secrets.toml` file in the project root:
   
```toml
[snowflake]
account = "your_account_identifier"
user = "your_username"
password = "your_password"
warehouse = "your_warehouse"
database = "your_database"
schema = "GOLD"
```

4. **Run the dashboard**
```bash
streamlit run app.py
```

5. **Access the dashboard**
   
   Open your browser to `http://localhost:8501`

## 🌐 Deployment Options

### Option 1: Streamlit Community Cloud (Recommended - FREE)

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fraud-dashboard.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Click "Deploy"

3. **Add Secrets**
   - In Streamlit Cloud dashboard, go to App Settings
   - Click "Secrets"
   - Paste your `secrets.toml` content
   - Save

### Option 2: Heroku Deployment

1. **Create a `setup.sh` file**:
```bash
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

2. **Create a `Procfile`**:
```
web: sh setup.sh && streamlit run app.py
```

3. **Deploy to Heroku**:
```bash
heroku login
heroku create your-fraud-dashboard
git push heroku main
```

4. **Set environment variables** in Heroku dashboard or CLI

### Option 3: AWS EC2 Deployment

1. **Launch EC2 instance** (Ubuntu 22.04 recommended)

2. **Connect via SSH and install dependencies**:
```bash
sudo apt update
sudo apt install python3-pip -y
git clone YOUR_REPO_URL
cd fraud-dashboard
pip3 install -r requirements.txt
```

3. **Configure secrets** as shown above

4. **Run with nohup**:
```bash
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
```

5. **Access via**: `http://YOUR_EC2_IP:8501`

### Option 4: Docker Deployment

1. **Create Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Build and run**:
```bash
docker build -t fraud-dashboard .
docker run -p 8501:8501 fraud-dashboard
```

## 📁 Project Structure

```
fraud-dashboard/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── secrets.toml           # Snowflake credentials (DO NOT COMMIT)
├── README.md                   # This file
└── .gitignore                 # Git ignore file
```

## 🔐 Security Best Practices

1. **Never commit secrets.toml** to Git
2. Add `.streamlit/secrets.toml` to `.gitignore`
3. Use environment variables for production deployments
4. Enable MFA on Snowflake accounts
5. Use read-only database roles for the dashboard

## 📝 Dashboard Pages

### 1. Executive Dashboard
- Total transaction metrics
- Fraud detection rate
- Daily trends visualization
- Alert type distribution
- Customer segment performance
- Geographic risk heatmap

### 2. Transaction Analysis
- Filterable transaction list
- Amount distribution charts
- Account type breakdowns
- Real-time filtering by date, amount, alert status

### 3. Customer Risk
- Risk category segmentation
- KYC compliance analysis
- Customer fraud rate metrics
- Interactive risk visualizations

### 4. Alert Management
- Alert severity filtering
- Alert type distribution
- Transaction exposure tracking
- Critical alert highlighting

### 5. Geographic Analysis
- Location-based fraud rates
- Regional performance comparison
- Geographic heatmaps
- High-risk location identification

### 6. Time Patterns
- Hourly transaction patterns
- Peak fraud hours identification
- Weekend vs weekday analysis
- Time-based risk scoring

## 🛠️ Customization

### Modify Color Schemes
Edit the Plotly color schemes in `app.py`:
```python
color_discrete_sequence=px.colors.qualitative.Set3
```

### Add New Pages
Add a new page option in the sidebar radio button and create the corresponding section.

### Adjust Refresh Rate
Modify the cache TTL in the `run_query` decorator:
```python
@st.cache_data(ttl=600)  # 600 seconds = 10 minutes
```

## 🐛 Troubleshooting

### Connection Issues
- Verify Snowflake credentials in `secrets.toml`
- Check network connectivity to Snowflake
- Ensure warehouse is running

### Missing Data
- Verify GOLD schema views exist in Snowflake
- Check data permissions for the user
- Run the SQL queries manually to verify data

### Performance Issues
- Increase cache TTL for less frequent updates
- Add query result limits
- Optimize Snowflake warehouse size

## 📊 Data Requirements

The dashboard expects these Snowflake views in the GOLD schema:
- `VW_TABLEAU_FRAUD_SUMMARY`
- `VW_TABLEAU_DAILY_TRENDS`
- `VW_TABLEAU_ALERT_DISTRIBUTION`
- `VW_TABLEAU_CUSTOMER_SEGMENTS`
- `VW_TABLEAU_GEOGRAPHIC_RISK`
- `VW_TABLEAU_TIME_PATTERNS`
- `VW_KYC_RISK_ANALYSIS`
- `FACT_TRANSACTIONS`
- `FACT_ALERTS`
- `DIM_CUSTOMER`
- `DIM_ACCOUNT`
- `DIM_LOCATION`
- `DIM_ALERT_TYPE`

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is proprietary and confidential.

## 👥 Support

For questions or support, contact the Data Analytics Team.

---

**Built with ❤️ using Streamlit & Snowflake**
