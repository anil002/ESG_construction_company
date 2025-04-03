import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import io
import requests
import base64

# Page configuration
st.set_page_config(
    page_title="Construction Co. ESG Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional and user-friendly styling
st.markdown("""
    <style>
    .main {background-color: #f5f6f5;}
    .stButton>button {background-color: #2b6cb0; color: white; border-radius: 5px; padding: 0.5rem;}
    .stDownloadButton>button {background-color: #38a169; color: white; border-radius: 5px; padding: 0.5rem;}
    .metric-card {background-color: white; padding: 1rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1rem;}
    .sidebar .sidebar-content {background-color: #edf2f7;}
    h1 {color: #2d3748;}
    h2, h3 {color: #4a5568;}
    .help-text {font-size: 0.9rem; color: #718096;}
    </style>
""", unsafe_allow_html=True)

# Title and welcome message
st.title("🏗️ Construction Company ESG Dashboard")
st.markdown(f"**Last Updated:** {datetime.now().strftime('%B %d, %Y')}")
st.info("Welcome! This dashboard helps you track Environmental, Social, and Governance (ESG) performance. Use the sidebar to choose your data and settings.")

# Synthetic data generation
@st.cache_data
def generate_synthetic_data():
    dates = pd.date_range(start="2023-01-01", end="2025-03-31", freq="M")
    np.random.seed(42)
    env_data = pd.DataFrame({
        'Date': dates,
        'CO2 Emissions (tons)': np.random.normal(1200, 150, len(dates)).cumsum() / 1000,
        'Energy Consumption (MWh)': np.random.normal(4500, 400, len(dates)).cumsum() / 1000,
        'Water Usage (m³)': np.random.normal(32000, 2500, len(dates)).cumsum() / 1000,
        'Waste Recycled (%)': np.clip(np.random.normal(78, 5, len(dates)), 0, 100),
        'Sustainable Materials (%)': np.clip(np.random.normal(65, 8, len(dates)), 0, 100)
    })
    soc_data = pd.DataFrame({
        'Date': dates,
        'Safety Incidents': np.random.poisson(0.8, len(dates)).cumsum(),
        'Employee Training (hours)': np.random.normal(2500, 300, len(dates)).cumsum() / 1000,
        'Diversity (% women)': np.clip(np.random.normal(32, 3, len(dates)), 0, 100),
        'Community Investment ($)': np.random.normal(150000, 20000, len(dates)).cumsum() / 1000,
        'Worker Satisfaction (score)': np.clip(np.random.normal(75, 5, len(dates)), 0, 100)
    })
    gov_data = pd.DataFrame({
        'Date': dates,
        'Ethics Training (%)': np.clip(np.random.normal(95, 4, len(dates)), 0, 100),
        'Supplier Audits': np.random.poisson(2.5, len(dates)).cumsum(),
        'Board Diversity (%)': np.clip(np.random.normal(45, 3, len(dates)), 0, 100),
        'Compliance Violations': np.random.poisson(0.2, len(dates)).cumsum(),
        'Transparency Score': np.clip(np.random.normal(85, 5, len(dates)), 0, 100)
    })
    targets = {
        'Environmental': {'CO2 Emissions (tons)': 1.0, 'Energy Consumption (MWh)': 4.0, 
                         'Water Usage (m³)': 30.0, 'Waste Recycled (%)': 85, 
                         'Sustainable Materials (%)': 75},
        'Social': {'Safety Incidents': 0, 'Employee Training (hours)': 3.0, 
                  'Diversity (% women)': 40, 'Community Investment ($)': 200.0, 
                  'Worker Satisfaction (score)': 80},
        'Governance': {'Ethics Training (%)': 100, 'Supplier Audits': 30, 
                      'Board Diversity (%)': 50, 'Compliance Violations': 0, 
                      'Transparency Score': 90}
    }
    return env_data, soc_data, gov_data, targets

# Function to load data from URL
def load_data_from_url(url):
    try:
        response = requests.get(url)
        if url.endswith('.csv'):
            return pd.read_csv(io.StringIO(response.text))
        elif url.endswith('.xlsx') or url.endswith('.xls'):
            return pd.read_excel(io.BytesIO(response.content))
        else:
            st.error("Unsupported file format from URL. Please use CSV or Excel.")
            return None
    except Exception as e:
        st.error(f"Error loading data from URL: {e}")
        return None

# Interactive chart function (defined early with parameters)
def create_interactive_chart(df, section_name, chart_type, show_targets, show_trend, targets):
    if chart_type == "Line":
        fig = px.line(df, x="Date", y=df.columns[1:], title=f"{section_name} Trends")
    elif chart_type == "Bar":
        fig = px.bar(df, x="Date", y=df.columns[1:], title=f"{section_name} Comparisons")
    elif chart_type == "Area":
        fig = px.area(df, x="Date", y=df.columns[1:], title=f"{section_name} Cumulative")
    else:  # Scatter
        fig = px.scatter(df, x="Date", y=df.columns[1:], title=f"{section_name} Points")
    
    if show_targets:
        for metric in df.columns[1:]:
            target_value = targets.get(section_name, {}).get(metric, 0)
            fig.add_hline(y=target_value, line_dash="dash", 
                         annotation_text=f"Goal: {metric}", annotation_position="top right")
    
    if show_trend:
        for metric in df.columns[1:]:
            z = np.polyfit(range(len(df)), df[metric], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(x=df["Date"], y=p(range(len(df))), 
                                   mode='lines', name=f"{metric} Trend", line=dict(dash='dot')))
    
    fig.update_layout(
        height=600,
        showlegend=True,
        hovermode="x unified",
        template="plotly_white",
        title_x=0.5
    )
    return fig

# Sidebar controls with help
with st.sidebar:
    st.header("Get Started")
    with st.expander("How to Use This Dashboard"):
        st.markdown("""
        - **Choose Data**: Pick where your data comes from (sample data, file upload, or URL).
        - **Select Category**: Choose Environmental, Social, or Governance.
        - **Adjust Settings**: Pick time range, metrics, and chart style.
        - **Explore**: View KPIs, charts, and data tables below.
        """)

    # Data source selection
    st.subheader("1. Choose Your Data")
    data_source = st.selectbox("Data Source", ["Sample Data", "Upload Excel", "Upload CSV", "URL"], 
                               help="Select 'Sample Data' to try it out, or upload your own file/URL.")
    
    # Data loading based on source
    if data_source == "Sample Data":
        env_data, soc_data, gov_data, targets = generate_synthetic_data()
        data_period = "Q1 2023 - Q1 2025 (Sample Data)"
    elif data_source == "Upload Excel":
        uploaded_file = st.file_uploader("Upload Your Excel File", type=['xlsx', 'xls'], 
                                        help="Upload an Excel file with sheets: Environmental, Social, Governance, Targets.")
        if uploaded_file:
            try:
                xl = pd.ExcelFile(uploaded_file)
                required_sheets = ["Environmental", "Social", "Governance", "Targets"]
                missing_sheets = [sheet for sheet in required_sheets if sheet not in xl.sheet_names]
                if missing_sheets:
                    st.error(f"Missing sheets: {', '.join(missing_sheets)}. Using sample data instead.")
                    env_data, soc_data, gov_data, targets = generate_synthetic_data()
                    data_period = "Q1 2023 - Q1 2025 (Sample Fallback)"
                else:
                    env_data = pd.read_excel(uploaded_file, sheet_name="Environmental")
                    soc_data = pd.read_excel(uploaded_file, sheet_name="Social")
                    gov_data = pd.read_excel(uploaded_file, sheet_name="Governance")
                    targets_df = pd.read_excel(uploaded_file, sheet_name="Targets")
                    targets = {
                        'Environmental': targets_df[targets_df['Environmental'].notna()].set_index('Metric')['Environmental'].to_dict(),
                        'Social': targets_df[targets_df['Social'].notna()].set_index('Metric')['Social'].to_dict(),
                        'Governance': targets_df[targets_df['Governance'].notna()].set_index('Metric')['Governance'].to_dict()
                    }
                    data_period = "Custom (Your Uploaded Data)"
            except Exception as e:
                st.error(f"Error with Excel file: {e}. Using sample data.")
                env_data, soc_data, gov_data, targets = generate_synthetic_data()
                data_period = "Q1 2023 - Q1 2025 (Sample Fallback)"
        else:
            env_data, soc_data, gov_data, targets = generate_synthetic_data()
            data_period = "Q1 2023 - Q1 2025 (Sample Fallback)"
    elif data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload Your CSV File", type=['csv'], 
                                        help="Upload a CSV with columns like 'Environmental_CO2 Emissions (tons)'.")
        if uploaded_file:
            data = pd.read_csv(uploaded_file)
            env_data = data.filter(like='Environmental', axis=1).join(data['Date'])
            soc_data = data.filter(like='Social', axis=1).join(data['Date'])
            gov_data = data.filter(like='Governance', axis=1).join(data['Date'])
            targets = generate_synthetic_data()[3]
            data_period = "Custom (Your Uploaded Data)"
        else:
            env_data, soc_data, gov_data, targets = generate_synthetic_data()
            data_period = "Q1 2023 - Q1 2025 (Sample Fallback)"
    elif data_source == "URL":
        url = st.text_input("Enter URL to CSV or Excel", 
                            help="Paste a direct link to a CSV or Excel file (e.g., from Google Drive or GitHub).")
        if url:
            data = load_data_from_url(url)
            if data is not None:
                if url.endswith('.csv'):
                    env_data = data.filter(like='Environmental', axis=1).join(data['Date'])
                    soc_data = data.filter(like='Social', axis=1).join(data['Date'])
                    gov_data = data.filter(like='Governance', axis=1).join(data['Date'])
                    targets = generate_synthetic_data()[3]
                else:
                    xl = pd.ExcelFile(io.BytesIO(requests.get(url).content))
                    required_sheets = ["Environmental", "Social", "Governance", "Targets"]
                    missing_sheets = [sheet for sheet in required_sheets if sheet not in xl.sheet_names]
                    if missing_sheets:
                        st.error(f"Missing sheets in URL Excel: {', '.join(missing_sheets)}")
                        env_data, soc_data, gov_data, targets = generate_synthetic_data()
                    else:
                        env_data = pd.read_excel(io.BytesIO(requests.get(url).content), sheet_name="Environmental")
                        soc_data = pd.read_excel(io.BytesIO(requests.get(url).content), sheet_name="Social")
                        gov_data = pd.read_excel(io.BytesIO(requests.get(url).content), sheet_name="Governance")
                        targets_df = pd.read_excel(io.BytesIO(requests.get(url).content), sheet_name="Targets")
                        targets = {
                            'Environmental': targets_df[targets_df['Environmental'].notna()].set_index('Metric')['Environmental'].to_dict(),
                            'Social': targets_df[targets_df['Social'].notna()].set_index('Metric')['Social'].to_dict(),
                            'Governance': targets_df[targets_df['Governance'].notna()].set_index('Metric')['Governance'].to_dict()
                        }
                data_period = "Custom (URL Data)"
            else:
                env_data, soc_data, gov_data, targets = generate_synthetic_data()
                data_period = "Q1 2023 - Q1 2025 (Sample Fallback)"
        else:
            env_data, soc_data, gov_data, targets = generate_synthetic_data()
            data_period = "Q1 2023 - Q1 2025 (Sample Fallback)"

    st.markdown(f"**Showing Data For:** {data_period}")

    # Category and settings
    st.subheader("2. Pick a Category")
    section = st.selectbox("Category", ["Environmental", "Social", "Governance"], 
                           help="Choose what to focus on: Environment (e.g., emissions), Social (e.g., safety), or Governance (e.g., ethics).")
    
    st.subheader("3. Customize Your View")
    time_period = st.slider("Months to Show", 1, len(env_data), len(env_data), 
                            help="Slide to choose how many months of data to display.")
    metrics = list(env_data.columns[1:]) if section == "Environmental" else \
             list(soc_data.columns[1:]) if section == "Social" else list(gov_data.columns[1:])
    selected_metrics = st.multiselect("Metrics to Show", metrics, default=metrics[:3], 
                                      help="Pick the specific measures you want to see (e.g., CO2 Emissions).")
    chart_type = st.selectbox("Chart Style", ["Line", "Bar", "Area", "Scatter"], 
                              help="Choose how to visualize your data: Line (trends), Bar (comparisons), Area (cumulative), Scatter (points).")
    show_targets = st.checkbox("Show Goals", value=True, 
                               help="Check to see target lines on the chart.")
    show_trend = st.checkbox("Show Trends", value=False, 
                             help="Check to add trend lines to the chart.")

# Filter data
data_dict = {"Environmental": env_data, "Social": soc_data, "Governance": gov_data}
filtered_df = data_dict[section].tail(time_period)[['Date'] + selected_metrics]

# KPI card with help
def display_kpi_card(metric, value, target, trend):
    status = "✅" if (value <= target and ("Emissions" in metric or "Usage" in metric or "Violations" in metric)) or \
                     (value >= target and not ("Emissions" in metric or "Usage" in metric or "Violations" in metric)) else "⚠️"
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Value", f"{value:.1f}", help="This is the latest value for this metric.")
    with col2:
        st.metric("Goal", f"{target:.1f}", status, help="This is the target we aim for. ✅ means we met it, ⚠️ means we didn’t.")
    with col3:
        st.metric("Change (%)", f"{trend:+.1f}%", help="This shows how much it changed over the selected time (positive = increase, negative = decrease).")

# Main content
st.header(f"{section} Overview")

# KPIs
st.subheader("Key Numbers")
with st.expander("What are Key Numbers?"):
    st.markdown("""
    These show the most important metrics at a glance:
    - **Current Value**: The latest number.
    - **Goal**: What we’re aiming for (✅ = met, ⚠️ = not met).
    - **Change**: How it’s changed over time.
    """)
for metric in selected_metrics:
    latest_value = filtered_df[metric].iloc[-1]
    first_value = filtered_df[metric].iloc[0]
    trend = ((latest_value - first_value) / first_value * 100) if first_value != 0 else 0
    target_value = targets.get(section, {}).get(metric, 0)
    
    with st.container():
        st.markdown(f"<div class='metric-card'><b>{metric}</b></div>", unsafe_allow_html=True)
        display_kpi_card(metric, latest_value, target_value, trend)

# Chart
st.subheader("Chart")
with st.expander("How to Read the Chart"):
    st.markdown("""
    - **X-Axis**: Dates over time.
    - **Y-Axis**: Values of your selected metrics.
    - **Lines/Bars**: Show how metrics change.
    - **Goals**: Dashed lines (if checked) show targets.
    - **Trends**: Dotted lines (if checked) show the direction of change.
    Hover over points for details!
    """)
fig = create_interactive_chart(filtered_df, section, chart_type, show_targets, show_trend, targets)
st.plotly_chart(fig, use_container_width=True)

# Data Table
st.subheader("Data Table")
with st.expander("What’s in the Table?"):
    st.markdown("This shows all the raw data for your selected metrics and time period. Each row is a month, and each column is a metric.")
st.dataframe(filtered_df.style.format("{:.1f}"), use_container_width=True)

# Export Options
st.subheader("Save Your Work")
with st.expander("How to Save"):
    st.markdown("""
    - **CSV**: Save the table as a simple text file (good for spreadsheets).
    - **Excel**: Save the table in Excel format (with formatting).
    - **Chart**: Save the chart as an image (great for reports).
    Click a button to download!
    """)
col1, col2, col3 = st.columns(3)
with col1:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Save as CSV", data=csv, 
                       file_name=f"{section.lower()}_esg_{datetime.now().strftime('%Y%m%d')}.csv", 
                       mime="text/csv", help="Download the table as a CSV file.")
with col2:
    excel_buffer = io.BytesIO()
    filtered_df.to_excel(excel_buffer, index=False)
    st.download_button(label="Save as Excel", data=excel_buffer, 
                       file_name=f"{section.lower()}_esg_{datetime.now().strftime('%Y%m%d')}.xlsx", 
                       mime="application/vnd.ms-excel", help="Download the table as an Excel file.")
with col3:
    buffer = io.BytesIO()
    fig.write_image(buffer, format="png", engine="kaleido")
    st.download_button(label="Save Chart", data=buffer, 
                       file_name=f"{section.lower()}_chart_{datetime.now().strftime('%Y%m%d')}.png", 
                       mime="image/png", help="Download the chart as an image.")

# Footer
st.markdown("---")
st.markdown("*Need help? Check the expanders above or try the sample data to get started!*")