import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import snowflake.connector
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
            
            /* Metric label (title) */
[data-testid="stMetricLabel"] {
    color: #1f2937 !important;  /* Dark slate */
    font-weight: 600;
}

/* Metric value */
[data-testid="stMetricValue"] {
    color: #111827 !important;  /* Almost black */
    font-weight: 800;
}

/* Metric delta */
[data-testid="stMetricDelta"] {
    color: #2563eb !important;  /* Blue */
    font-weight: 600;
}
/* Main page padding */
.main {
    padding: 0.5rem 1.5rem;
    background-color: #f7f9fc;
}

/* Metric card container */
.metric-card {
    background: linear-gradient(135deg, #ffffff, #f1f5fb);
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
    border-left: 6px solid #2563eb; /* Primary Blue */
}

/* Streamlit metric styling */
.stMetric {
    background-color: #ffffff;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* Title */
h1 {
    color: #1e40af; /* Deep Blue */
    font-weight: 800;
    letter-spacing: 0.3px;
}

/* Section headers */
h2 {
    color: #334155; /* Slate */
    font-weight: 600;
    margin-top: 1.5rem;
}

/* Optional: subtitles / captions */
h3 {
    color: #475569;
    font-weight: 500;
}

/* Success / Low Risk */
.success {
    color: #16a34a;
}

/* Warning / Medium Risk */
.warning {
    color: #f59e0b;
}

/* Danger / High Risk */
.danger {
    color: #dc2626;
}
</style>

    """, unsafe_allow_html=True)

# Snowflake connection function with better error handling
@st.cache_resource
def init_connection():
    """Initialize Snowflake connection with error handling"""
    try:
        conn = snowflake.connector.connect(
            account=st.secrets["snowflake"]["account"],
            user=st.secrets["snowflake"]["user"],
            password=st.secrets["snowflake"]["password"],
            warehouse=st.secrets["snowflake"]["warehouse"],
            database=st.secrets["snowflake"]["database"],
            schema=st.secrets["snowflake"]["schema"],
            client_session_keep_alive=True  # Keep connection alive
        )
        return conn
    except Exception as e:
        st.error(f"❌ Connection Error: {str(e)}")
        st.info("💡 Please check your Snowflake credentials in .streamlit/secrets.toml")
        st.stop()

# Get connection
def get_connection():
    """Get or create Snowflake connection"""
    if 'snowflake_conn' not in st.session_state or st.session_state.snowflake_conn is None:
        st.session_state.snowflake_conn = init_connection()
    
    # Check if connection is still valid
    try:
        st.session_state.snowflake_conn.cursor().execute("SELECT 1")
    except:
        # Reconnect if connection is dead
        st.session_state.snowflake_conn = init_connection()
    
    return st.session_state.snowflake_conn

# Query execution function with better error handling
@st.cache_data(ttl=600, show_spinner=False)
def run_query(query):
    """Execute query and return results as DataFrame"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Fetch column names and data
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
        cursor.close()
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=columns)
        return df
    except Exception as e:
        st.error(f"Query Error: {str(e)}")
        st.code(query, language='sql')
        # Clear cache and try again
        st.cache_data.clear()
        st.cache_resource.clear()
        return pd.DataFrame()

# Sidebar navigation
st.sidebar.title("🔒 Fraud Detection System")
st.sidebar.markdown("---")

# Connection status indicator
try:
    test_conn = get_connection()
    st.sidebar.success("Connected to Snowflake")
except:
    st.sidebar.error("❌ Not Connected")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Executive Dashboard", "🔍 Transaction Analysis", "👥 Customer Risk", 
     "🚨 Alert Management", "📍 Geographic Analysis", "⏰ Time Patterns"]
)

st.sidebar.markdown("---")
st.sidebar.info("**Last Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Add a refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Main content based on page selection
if page == "📊 Executive Dashboard":
    st.title("📊 Executive Fraud Detection Dashboard")
    st.markdown("### Real-time Fraud Monitoring & Analytics")
    
    with st.spinner("Loading dashboard data..."):
        # Fetch summary metrics
        summary_query = "SELECT * FROM GOLD.VW_TABLEAU_FRAUD_SUMMARY"
        summary_df = run_query(summary_query)
    
    if summary_df.empty:
        st.error("No data available. Please check your database connection and views.")
        st.stop()
    
    # Display KPI metrics
    col1, col2, col3, col4 = st.columns(4)
    
    metrics_dict = dict(zip(summary_df['METRIC_NAME'], summary_df['METRIC_VALUE']))
    
    with col1:
        total_txn = int(metrics_dict.get('Total Transactions', 0))
        st.metric("Total Transactions", f"{total_txn:,}")
    
    with col2:
        flagged_txn = int(metrics_dict.get('Flagged Transactions', 0))
        st.metric("Flagged Transactions", f"{flagged_txn:,}", 
                 delta=f"{(flagged_txn/total_txn*100):.1f}%" if total_txn > 0 else "0%")
    
    with col3:
        fraud_rate = metrics_dict.get('Fraud Detection Rate', 0)
        st.metric("Fraud Detection Rate", f"{fraud_rate:.2f}%")
    
    with col4:
        high_risk = int(metrics_dict.get('High Risk Customers', 0))
        st.metric("High Risk Customers", f"{high_risk:,}")
    
    st.markdown("---")
    
    # Daily trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily Transaction Trends")
        with st.spinner("Loading trends..."):
            daily_query = "SELECT * FROM GOLD.VW_TABLEAU_DAILY_TRENDS ORDER BY DATE_VALUE"
            daily_df = run_query(daily_query)
        
        if not daily_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_df['DATE_VALUE'], 
                y=daily_df['TRANSACTION_COUNT'],
                name='Total Transactions',
                line=dict(color='#1f77b4', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=daily_df['DATE_VALUE'], 
                y=daily_df['FLAGGED_COUNT'],
                name='Flagged Transactions',
                line=dict(color='#ff7f0e', width=2)
            ))
            fig.update_layout(
                height=350,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No daily trend data available")
    
    with col2:
        st.subheader("🎯 Alert Type Distribution")
        with st.spinner("Loading alerts..."):
            alert_query = "SELECT * FROM GOLD.VW_TABLEAU_ALERT_DISTRIBUTION"
            alert_df = run_query(alert_query)
        
        if not alert_df.empty:
            fig = px.pie(
                alert_df, 
                values='ALERT_COUNT', 
                names='ALERT_TYPE',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No alert data available")
    
    st.markdown("---")
    
    # Customer segments and geographic risk
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Customer Segment Performance")
        with st.spinner("Loading segments..."):
            segment_query = "SELECT * FROM GOLD.VW_TABLEAU_CUSTOMER_SEGMENTS"
            segment_df = run_query(segment_query)
        
        if not segment_df.empty:
            fig = px.bar(
                segment_df,
                x='CUSTOMER_SEGMENT',
                y='FRAUD_RATE_PCT',
                color='RISK_CATEGORY',
                text='FRAUD_RATE_PCT',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=350, xaxis_title="", yaxis_title="Fraud Rate (%)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No customer segment data available")
    
    with col2:
        st.subheader("📍 Geographic Risk Distribution")
        with st.spinner("Loading geographic data..."):
            geo_query = "SELECT * FROM GOLD.VW_TABLEAU_GEOGRAPHIC_RISK ORDER BY FRAUD_RATE DESC LIMIT 10"
            geo_df = run_query(geo_query)
        
        if not geo_df.empty:
            fig = px.bar(
                geo_df,
                x='LOCATION',
                y='FRAUD_RATE',
                color='REGION',
                text='FRAUD_RATE',
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=350, xaxis_title="", yaxis_title="Fraud Rate (%)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No geographic data available")

elif page == "🔍 Transaction Analysis":
    st.title("🔍 Transaction Analysis")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
    
    with col2:
        amount_filter = st.slider(
            "Minimum Transaction Amount",
            min_value=0,
            max_value=100000,
            value=0,
            step=5000
        )
    
    with col3:
        alert_filter = st.selectbox(
            "Alert Status",
            ["All", "Flagged Only", "Clean Only"]
        )
    
    # Build dynamic query based on filters
    base_query = """
    SELECT 
        ft.TXN_ID,
        ft.TXN_TIMESTAMP,
        dc.CUSTOMER_ID,
        dc.RISK_SCORE,
        da.ACCOUNT_TYPE,
        ft.AMOUNT,
        dl.LOCATION,
        ft.HAS_ALERT,
        ft.ALERT_COUNT
    FROM GOLD.FACT_TRANSACTIONS ft
    JOIN GOLD.DIM_CUSTOMER dc ON ft.CUSTOMER_KEY = dc.CUSTOMER_KEY
    JOIN GOLD.DIM_ACCOUNT da ON ft.ACCOUNT_KEY = da.ACCOUNT_KEY
    JOIN GOLD.DIM_LOCATION dl ON ft.LOCATION_KEY = dl.LOCATION_KEY
    WHERE ft.AMOUNT >= {amount}
    """
    
    if alert_filter == "Flagged Only":
        base_query += " AND ft.HAS_ALERT = TRUE"
    elif alert_filter == "Clean Only":
        base_query += " AND ft.HAS_ALERT = FALSE"
    
    base_query += " ORDER BY ft.TXN_TIMESTAMP DESC LIMIT 1000"
    
    with st.spinner("Loading transactions..."):
        txn_df = run_query(base_query.format(amount=amount_filter))
    
    if txn_df.empty:
        st.warning("No transactions found with the selected filters")
        st.stop()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Transactions", f"{len(txn_df):,}")
    with col2:
        flagged = txn_df['HAS_ALERT'].sum()
        st.metric("Flagged", f"{flagged:,}")
    with col3:
        total_value = txn_df['AMOUNT'].sum()
        st.metric("Total Value", f"₹{total_value:,.0f}")
    with col4:
        avg_amount = txn_df['AMOUNT'].mean()
        st.metric("Avg Amount", f"₹{avg_amount:,.0f}")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Transaction Amount Distribution")
        fig = px.histogram(
            txn_df,
            x='AMOUNT',
            nbins=30,
            color='HAS_ALERT',
            color_discrete_map={True: '#ff7f0e', False: '#1f77b4'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Transactions by Account Type")
        account_summary = txn_df.groupby('ACCOUNT_TYPE').agg({
            'TXN_ID': 'count',
            'AMOUNT': 'sum'
        }).reset_index()
        
        fig = px.bar(
            account_summary,
            x='ACCOUNT_TYPE',
            y='TXN_ID',
            text='TXN_ID',
            color='ACCOUNT_TYPE'
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Transaction table
    st.subheader("📋 Transaction Details")
    st.dataframe(
        txn_df,
        use_container_width=True,
        height=400
    )

elif page == "👥 Customer Risk":
    st.title("👥 Customer Risk Analysis")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        risk_category = st.multiselect(
            "Risk Category",
            ["High Risk", "Medium Risk", "Low Risk"],
            default=["High Risk", "Medium Risk", "Low Risk"]
        )
    
    with col2:
        kyc_status = st.multiselect(
            "KYC Status",
            ["Verified", "Pending", "Expired"],
            default=["Verified", "Pending", "Expired"]
        )
    
    if not risk_category or not kyc_status:
        st.warning("Please select at least one option from each filter")
        st.stop()
    
    # Customer risk query
    risk_query = f"""
    SELECT * FROM GOLD.VW_KYC_RISK_ANALYSIS
    WHERE RISK_CATEGORY IN ('{"','".join(risk_category)}')
    AND KYC_STATUS IN ('{"','".join(kyc_status)}')
    """
    
    with st.spinner("Loading customer risk data..."):
        risk_df = run_query(risk_query)
    
    if risk_df.empty:
        st.warning("No data available for selected filters")
        st.stop()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = risk_df['CUSTOMER_COUNT'].sum()
        st.metric("Total Customers", f"{total_customers:,}")
    
    with col2:
        total_txns = risk_df['TOTAL_TRANSACTIONS'].sum()
        st.metric("Total Transactions", f"{total_txns:,}")
    
    with col3:
        flagged = risk_df['FLAGGED_TRANSACTIONS'].sum()
        st.metric("Flagged Transactions", f"{flagged:,}")
    
    with col4:
        avg_fraud_rate = risk_df['FRAUD_RATE_PCT'].mean()
        st.metric("Avg Fraud Rate", f"{avg_fraud_rate:.2f}%")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Category Distribution")
        fig = px.sunburst(
            risk_df,
            path=['RISK_CATEGORY', 'KYC_STATUS'],
            values='CUSTOMER_COUNT',
            color='FRAUD_RATE_PCT',
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Fraud Rate by Segment")
        fig = px.scatter(
            risk_df,
            x='TOTAL_TRANSACTIONS',
            y='FRAUD_RATE_PCT',
            size='CUSTOMER_COUNT',
            color='RISK_CATEGORY',
            hover_data=['KYC_STATUS'],
            size_max=50
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.subheader("📊 Detailed Risk Analysis")
    st.dataframe(risk_df, use_container_width=True, height=300)

elif page == "🚨 Alert Management":
    st.title("🚨 Alert Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        severity_filter = st.multiselect(
            "Alert Severity",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High"]
        )
    
    with col2:
        alert_type_filter = st.multiselect(
            "Alert Type",
            ["High Value", "Rapid Velocity", "Foreign Location", "Multiple Failures"],
            default=["High Value", "Rapid Velocity", "Foreign Location", "Multiple Failures"]
        )
    
    with col3:
        min_amount = st.number_input(
            "Min Transaction Amount",
            min_value=0,
            value=35000,
            step=5000
        )
    
    if not severity_filter or not alert_type_filter:
        st.warning("Please select at least one option from each filter")
        st.stop()
    
    # Alert query
    alert_query = f"""
    SELECT 
        fa.ALERT_ID,
        fa.ALERT_TIMESTAMP,
        dc.CUSTOMER_ID,
        dc.RISK_SCORE,
        dat.ALERT_TYPE,
        dat.ALERT_SEVERITY,
        dat.ALERT_CATEGORY,
        fa.TRANSACTION_AMOUNT,
        fa.CUSTOMER_RISK_SCORE
    FROM GOLD.FACT_ALERTS fa
    JOIN GOLD.DIM_CUSTOMER dc ON fa.CUSTOMER_KEY = dc.CUSTOMER_KEY
    JOIN GOLD.DIM_ALERT_TYPE dat ON fa.ALERT_TYPE_KEY = dat.ALERT_TYPE_KEY
    WHERE dat.ALERT_SEVERITY IN ('{"','".join(severity_filter)}')
    AND dat.ALERT_TYPE IN ('{"','".join(alert_type_filter)}')
    AND fa.TRANSACTION_AMOUNT >= {min_amount}
    ORDER BY fa.ALERT_TIMESTAMP DESC
    LIMIT 500
    """
    
    with st.spinner("Loading alerts..."):
        alert_df = run_query(alert_query)
    
    if alert_df.empty:
        st.warning("No alerts found with the selected filters")
        st.stop()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Alerts", f"{len(alert_df):,}")
    
    with col2:
        critical_alerts = (alert_df['ALERT_SEVERITY'] == 'Critical').sum()
        st.metric("Critical Alerts", f"{critical_alerts:,}", delta="High Priority")
    
    with col3:
        total_exposure = alert_df['TRANSACTION_AMOUNT'].sum()
        st.metric("Total Exposure", f"₹{total_exposure:,.0f}")
    
    with col4:
        avg_risk = alert_df['CUSTOMER_RISK_SCORE'].mean()
        st.metric("Avg Risk Score", f"{avg_risk:.0f}")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Alert Severity Breakdown")
        severity_count = alert_df['ALERT_SEVERITY'].value_counts().reset_index()
        severity_count.columns = ['Severity', 'Count']
        
        fig = px.bar(
            severity_count,
            x='Severity',
            y='Count',
            color='Severity',
            text='Count',
            color_discrete_map={
                'Critical': '#d62728',
                'High': '#ff7f0e',
                'Medium': '#ffbb78',
                'Low': '#98df8a'
            }
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Alert Type Distribution")
        type_data = alert_df.groupby('ALERT_TYPE').agg({
            'ALERT_ID': 'count',
            'TRANSACTION_AMOUNT': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=type_data['ALERT_TYPE'],
            y=type_data['ALERT_ID'],
            name='Alert Count',
            marker_color='indianred'
        ))
        fig.update_layout(height=350, xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Alert details table
    st.subheader("📋 Alert Details")
    st.dataframe(alert_df, use_container_width=True, height=400)

elif page == "📍 Geographic Analysis":
    st.title("📍 Geographic Risk Analysis")
    
    # Geographic query
    geo_query = "SELECT * FROM GOLD.VW_TABLEAU_GEOGRAPHIC_RISK ORDER BY FRAUD_RATE DESC"
    
    with st.spinner("Loading geographic data..."):
        geo_df = run_query(geo_query)
    
    if geo_df.empty:
        st.warning("No geographic data available")
        st.stop()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_locations = len(geo_df)
        st.metric("Total Locations", f"{total_locations:,}")
    
    with col2:
        high_risk_locations = (geo_df['FRAUD_RATE'] > 5).sum()
        st.metric("High Risk Locations", f"{high_risk_locations:,}")
    
    with col3:
        total_value = geo_df['TOTAL_VALUE'].sum()
        st.metric("Total Transaction Value", f"₹{total_value:,.0f}")
    
    with col4:
        avg_fraud_rate = geo_df['FRAUD_RATE'].mean()
        st.metric("Avg Fraud Rate", f"{avg_fraud_rate:.2f}%")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Geographic Fraud Heatmap")
        fig = px.bar(
            geo_df.head(15),
            x='LOCATION',
            y='FRAUD_RATE',
            color='FRAUD_RATE',
            text='FRAUD_RATE',
            color_continuous_scale='Reds',
            hover_data=['TRANSACTION_COUNT', 'TOTAL_VALUE']
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400, xaxis_title="", yaxis_title="Fraud Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Region Distribution")
        region_data = geo_df.groupby('REGION').agg({
            'TRANSACTION_COUNT': 'sum',
            'FLAGGED_COUNT': 'sum'
        }).reset_index()
        
        fig = px.pie(
            region_data,
            values='TRANSACTION_COUNT',
            names='REGION',
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.subheader("📊 Location Performance Details")
    st.dataframe(geo_df, use_container_width=True, height=400)

elif page == "⏰ Time Patterns":
    st.title("⏰ Time-based Fraud Patterns")
    
    # Time patterns query
    time_query = "SELECT * FROM GOLD.VW_TABLEAU_TIME_PATTERNS ORDER BY TXN_HOUR"
    daily_query = "SELECT * FROM GOLD.VW_TABLEAU_DAILY_TRENDS ORDER BY DATE_VALUE"
    
    with st.spinner("Loading time pattern data..."):
        time_df = run_query(time_query)
        daily_df = run_query(daily_query)
    
    if time_df.empty:
        st.warning("No time pattern data available")
        st.stop()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        peak_hour = time_df.loc[time_df['TRANSACTION_COUNT'].idxmax(), 'TXN_HOUR']
        st.metric("Peak Transaction Hour", f"{int(peak_hour)}:00")
    
    with col2:
        risky_hour = time_df.loc[time_df['FRAUD_RATE'].idxmax(), 'TXN_HOUR']
        st.metric("Highest Risk Hour", f"{int(risky_hour)}:00")
    
    with col3:
        if not daily_df.empty:
            weekend_txns = daily_df[daily_df['IS_WEEKEND'] == True]['TRANSACTION_COUNT'].sum()
            st.metric("Weekend Transactions", f"{weekend_txns:,}")
        else:
            st.metric("Weekend Transactions", "N/A")
    
    with col4:
        night_fraud = time_df[time_df['TIME_PERIOD'] == 'Night']['FRAUD_RATE'].mean()
        st.metric("Night Fraud Rate", f"{night_fraud:.2f}%")
    
    st.markdown("---")
    
    # Hourly analysis
    st.subheader("📊 Hourly Transaction Patterns")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(
            x=time_df['TXN_HOUR'],
            y=time_df['TRANSACTION_COUNT'],
            name="Transaction Count",
            marker_color='lightblue'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=time_df['TXN_HOUR'],
            y=time_df['FRAUD_RATE'],
            name="Fraud Rate (%)",
            line=dict(color='red', width=3),
            mode='lines+markers'
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Hour of Day")
    fig.update_yaxes(title_text="Transaction Count", secondary_y=False)
    fig.update_yaxes(title_text="Fraud Rate (%)", secondary_y=True)
    fig.update_layout(height=400, hovermode='x unified')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Time period breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Time Period Analysis")
        period_data = time_df.groupby('TIME_PERIOD').agg({
            'TRANSACTION_COUNT': 'sum',
            'FLAGGED_COUNT': 'sum',
            'FRAUD_RATE': 'mean'
        }).reset_index()
        
        fig = px.bar(
            period_data,
            x='TIME_PERIOD',
            y='TRANSACTION_COUNT',
            color='FRAUD_RATE',
            text='TRANSACTION_COUNT',
            color_continuous_scale='Reds'
        )
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Weekend vs Weekday")
        if not daily_df.empty:
            weekend_data = daily_df.groupby('IS_WEEKEND').agg({
                'TRANSACTION_COUNT': 'sum',
                'FLAGGED_COUNT': 'sum'
            }).reset_index()
            weekend_data['IS_WEEKEND'] = weekend_data['IS_WEEKEND'].map({True: 'Weekend', False: 'Weekday'})
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=weekend_data['IS_WEEKEND'],
                y=weekend_data['TRANSACTION_COUNT'],
                name='Total',
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                x=weekend_data['IS_WEEKEND'],
                y=weekend_data['FLAGGED_COUNT'],
                name='Flagged',
                marker_color='coral'
            ))
            fig.update_layout(height=350, barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No weekend/weekday data available")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Fraud Detection Dashboard v1.0</strong> | Built with Streamlit & Snowflake</p>
        <p>© 2026 Financial Analytics Team | Confidential</p>
    </div>
    """,
    unsafe_allow_html=True
)