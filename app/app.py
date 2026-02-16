"""
Financial LLM Copilot - Main Streamlit Application
===================================================
AI-powered macroeconomic analysis for 80+ countries with 12 indicators.
"""

import streamlit as st
from datetime import datetime

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Financial LLM Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import application modules
from config import app_config, model_config, validate_config
from countries import COUNTRIES, REGIONS, get_country_count
from indicators import INDICATORS, get_indicator_options
from data_fetcher import data_fetcher, get_data
from model_loader import model_loader
from chat_engine import chat_engine
from visualizations import (
    create_region_bar_chart,
    create_global_ranking_chart,
    create_comparison_chart,
    create_multi_indicator_radar,
)
from utils import (
    get_confidence_emoji,
    get_region_emoji,
    get_income_level_display,
    format_percentage,
)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False

if "selected_region" not in st.session_state:
    st.session_state.selected_region = app_config.default_region

if "compare_countries" not in st.session_state:
    st.session_state.compare_countries = app_config.default_countries_compare.copy()


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.title("📊 Financial Copilot")
    st.caption(f"v{app_config.app_version} | {get_country_count()} Countries | 12 Indicators")
    
    st.divider()
    
    # Model Status Section
    st.subheader("AI Model Status")
    
    if st.session_state.model_loaded:
        st.success("Model Ready")
    else:
        st.warning("Model Not Loaded")
        
        if st.button("Load AI Model", type="primary", use_container_width=True):
            with st.spinner("Downloading and loading model (this may take 2-5 minutes)..."):
                try:
                    model_loader.load_model()
                    st.session_state.model_loaded = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load model: {e}")
    
    st.divider()
    
    # Region Selection
    st.subheader("Region Selection")
    
    selected_region = st.selectbox(
        "Select Region",
        options=list(REGIONS.keys()),
        index=list(REGIONS.keys()).index(st.session_state.selected_region),
        format_func=lambda x: f"{get_region_emoji(x)} {x}",
        key="region_selector"
    )
    st.session_state.selected_region = selected_region
    
    # Display region info
    region_codes = REGIONS[selected_region]
    st.caption(f"{len(region_codes)} countries in this region")
    
    # Country Selection
    country_options = {
        code: COUNTRIES[code].name 
        for code in region_codes 
        if code in COUNTRIES
    }
    
    selected_country = st.selectbox(
        "Select Country",
        options=list(country_options.keys()),
        format_func=lambda x: f"{COUNTRIES[x].flag_emoji} {country_options[x]}",
        key="country_selector"
    )
    
    # Indicator Selection
    indicator_options = get_indicator_options()
    selected_indicator = st.selectbox(
        "Select Indicator",
        options=list(indicator_options.keys()),
        format_func=lambda x: indicator_options[x],
        key="indicator_selector"
    )
    
    # Quick Data Fetch Button
    if st.button("Fetch Data", use_container_width=True):
        with st.spinner("Fetching data..."):
            data = get_data(selected_indicator, selected_country)
            
            if data.consensus_value is not None:
                st.metric(
                    label=f"{data.country_name} - {data.indicator_name}",
                    value=format_percentage(data.consensus_value) if data.unit == "%" else f"${data.consensus_value:,.0f}",
                )
                st.caption(f"{get_confidence_emoji(data.confidence_level)} {data.confidence_level.title()} confidence")
                st.caption(f"Assessment: {data.assessment_label}")
            else:
                st.warning("No data available")
    
    st.divider()
    
    # Clear Chat Button
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        chat_engine.clear_history()
        st.rerun()
    
    st.divider()
    
    # Footer
    st.caption("Powered by QLoRA Fine-tuned Mistral-7B")
    st.caption("Data: FRED | World Bank | OECD")


# =============================================================================
# MAIN CONTENT
# =============================================================================
st.title("📊 Financial LLM Copilot")
st.markdown(
    f"*AI-powered macroeconomic analysis covering **{get_country_count()} countries** "
    f"across **{len(REGIONS)} regions** with **{len(INDICATORS)} indicators***"
)

# Create tabs
tab_chat, tab_region, tab_ranking, tab_compare = st.tabs([
    "💬 Chat",
    "🌍 Regional Analysis",
    "🏆 Global Rankings",
    "📊 Country Comparison"
])


# =============================================================================
# TAB 1: CHAT
# =============================================================================
with tab_chat:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show data expander if available
            if message.get("data"):
                with st.expander("View Source Data"):
                    for d in message["data"]:
                        if d.consensus_value is not None:
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.write(f"**{d.country_name}** - {d.indicator_name}")
                            with col2:
                                st.write(f"{d.consensus_value:.2f}{d.unit}")
                            with col3:
                                st.write(f"{get_confidence_emoji(d.confidence_level)} {d.confidence_level}")
    
    # Chat input
    if prompt := st.chat_input("Ask about any country's economy..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            if not st.session_state.model_loaded:
                response = "Please load the AI model first using the sidebar button."
                st.warning(response)
                data = []
            else:
                try:
                    # Create a placeholder for the streaming response
                    response_placeholder = st.empty()
                    full_response = ""
                    data = []
                    
                    # Generate streaming response
                    for chunk, final_data in chat_engine.generate_response(prompt):
                        if chunk:
                            full_response += chunk
                            response_placeholder.markdown(full_response + "▌")
                        if final_data is not None:
                            data = final_data
                    
                    # Final update without cursor
                    response_placeholder.markdown(full_response)
                    
                    if data:
                        with st.expander("View Source Data"):
                            for d in data:
                                if d.consensus_value is not None:
                                    col1, col2, col3 = st.columns([2, 1, 1])
                                    with col1:
                                        st.write(f"**{d.country_name}** - {d.indicator_name}")
                                    with col2:
                                        st.write(f"{d.consensus_value:.2f}{d.unit}")
                                    with col3:
                                        st.write(f"{get_confidence_emoji(d.confidence_level)} {d.confidence_level}")
                    
                    # Store in history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                        "data": data
                    })
                except Exception as e:
                    response = f"Error generating response: {e}"
                    st.error(response)
                    data = []
    
    # Show suggested questions if no messages
    if not st.session_state.messages:
        st.markdown("### Suggested Questions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **GDP & Growth:**
            - What is India's GDP growth rate?
            - Compare USA and China GDP
            - Which Asian countries are growing fastest?
            """)
        
        with col2:
            st.markdown("""
            **Inflation & Rates:**
            - What is Brazil's inflation rate?
            - Compare European interest rates
            - Which countries have high inflation?
            """)
        
        with col3:
            st.markdown("""
            **Other Indicators:**
            - What is Japan's government debt?
            - Compare Germany and France unemployment
            - What is Nigeria's FDI inflows?
            """)


# =============================================================================
# TAB 2: REGIONAL ANALYSIS
# =============================================================================
with tab_region:
    st.subheader(f"{get_region_emoji(st.session_state.selected_region)} {st.session_state.selected_region}")
    
    # Indicator selection for regional analysis
    region_indicator = st.selectbox(
        "Select Indicator for Regional Analysis",
        options=list(INDICATORS.keys()),
        format_func=lambda x: f"{INDICATORS[x].icon} {INDICATORS[x].display_name}",
        key="region_indicator"
    )
    
    if st.button("Load Regional Data", key="load_region_btn"):
        with st.spinner(f"Fetching data for {st.session_state.selected_region}..."):
            region_data = data_fetcher.get_region_data(
                region_indicator,
                st.session_state.selected_region
            )
            
            if region_data:
                # Create and display chart
                chart = create_region_bar_chart(region_data, region_indicator)
                st.plotly_chart(chart, use_container_width=True)
                
                # Display data table
                st.markdown("### Data Table")
                
                table_data = []
                for d in region_data:
                    table_data.append({
                        "Country": d.country_name,
                        "Value": f"{d.consensus_value:.2f}{d.unit}",
                        "FRED": f"{d.fred_value:.2f}" if d.fred_value else "N/A",
                        "World Bank": f"{d.worldbank_value:.2f}" if d.worldbank_value else "N/A",
                        "OECD": f"{d.oecd_value:.2f}" if d.oecd_value else "N/A",
                        "Confidence": f"{get_confidence_emoji(d.confidence_level)} {d.confidence_level.title()}",
                        "Assessment": d.assessment_label,
                    })
                
                st.dataframe(table_data, use_container_width=True, hide_index=True)
            else:
                st.warning("No data available for this region")


# =============================================================================
# TAB 3: GLOBAL RANKINGS
# =============================================================================
with tab_ranking:
    st.subheader("Global Rankings")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ranking_indicator = st.selectbox(
            "Rank by Indicator",
            options=list(INDICATORS.keys()),
            format_func=lambda x: f"{INDICATORS[x].icon} {INDICATORS[x].display_name}",
            key="ranking_indicator"
        )
    
    with col2:
        top_n = st.slider("Number of Countries", min_value=5, max_value=30, value=15)
    
    if st.button("Load Global Rankings", key="load_ranking_btn"):
        with st.spinner("Fetching global data..."):
            ranking_data = data_fetcher.get_global_ranking(ranking_indicator, limit=top_n)
            
            if ranking_data:
                # Create and display chart
                chart = create_global_ranking_chart(ranking_data, ranking_indicator, top_n)
                st.plotly_chart(chart, use_container_width=True)
                
                # Display podium for top 3
                st.markdown("### Top 3")
                cols = st.columns(3)
                medals = ["🥇", "🥈", "🥉"]
                
                for i, (col, medal) in enumerate(zip(cols, medals)):
                    if i < len(ranking_data):
                        with col:
                            d = ranking_data[i]
                            st.markdown(f"### {medal} {d.country_name}")
                            st.metric(
                                label=d.region,
                                value=f"{d.consensus_value:.2f}{d.unit}"
                            )
            else:
                st.warning("No ranking data available")


# =============================================================================
# TAB 4: COUNTRY COMPARISON
# =============================================================================
with tab_compare:
    st.subheader("Country Comparison")
    
    # Country selection for comparison
    all_countries = {
        code: f"{info.flag_emoji} {info.name}"
        for code, info in COUNTRIES.items()
        if code != "EUU"
    }
    
    compare_countries = st.multiselect(
        "Select Countries to Compare (max 6)",
        options=list(all_countries.keys()),
        default=st.session_state.compare_countries[:3],
        format_func=lambda x: all_countries[x],
        max_selections=6,
        key="compare_countries_select"
    )
    
    compare_indicator = st.selectbox(
        "Compare by Indicator",
        options=list(INDICATORS.keys()),
        format_func=lambda x: f"{INDICATORS[x].icon} {INDICATORS[x].display_name}",
        key="compare_indicator"
    )
    
    if compare_countries and st.button("Compare Countries", key="compare_btn"):
        with st.spinner("Fetching comparison data..."):
            comparison_data = []
            for code in compare_countries:
                data = get_data(compare_indicator, code)
                comparison_data.append(data)
            
            if comparison_data:
                # Create and display chart
                chart = create_comparison_chart(comparison_data, compare_indicator)
                st.plotly_chart(chart, use_container_width=True)
                
                # Display comparison table
                st.markdown("### Comparison Table")
                
                table_data = []
                for d in comparison_data:
                    table_data.append({
                        "Country": d.country_name,
                        "Region": d.region,
                        "Consensus": f"{d.consensus_value:.2f}{d.unit}" if d.consensus_value else "N/A",
                        "FRED": f"{d.fred_value:.2f}" if d.fred_value else "N/A",
                        "World Bank": f"{d.worldbank_value:.2f}" if d.worldbank_value else "N/A",
                        "OECD": f"{d.oecd_value:.2f}" if d.oecd_value else "N/A",
                        "Confidence": d.confidence_level.title(),
                        "Assessment": d.assessment_label,
                    })
                
                st.dataframe(table_data, use_container_width=True, hide_index=True)


# =============================================================================
# FOOTER
# =============================================================================
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption(f"📊 Financial LLM Copilot v{app_config.app_version}")

with col2:
    st.caption(f"{get_country_count()} Countries | {len(INDICATORS)} Indicators")

with col3:
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")