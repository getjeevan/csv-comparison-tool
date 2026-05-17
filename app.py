import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
from utils.data_processor import DataProcessor
from utils.comparison_engine import ComparisonEngine

pd.set_option("styler.render.max_elements", 1000000)

st.set_page_config(
    page_title="CSV Comparison Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLORS = {
    "primary": "#1A73E8",
    "success": "#34A853",
    "bg": "#F8F9FA",
    "text": "#202124",
    "accent": "#EA4335",
    "border": "#DADCE0",
    "white": "#FFFFFF",
    "light_green": "#E6F4EA",
    "light_red": "#FCE8E6",
    "light_blue": "#E8F0FE",
    "muted": "#5F6368",
}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');

    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}

    .app-header {{
        background: linear-gradient(135deg, {COLORS["primary"]} 0%, #1557B0 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
    }}
    .app-header h1 {{
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0 0 0.25rem 0;
        letter-spacing: -0.5px;
    }}
    .app-header p {{
        font-family: 'Roboto', sans-serif;
        font-size: 0.95rem;
        margin: 0;
        opacity: 0.9;
        font-weight: 300;
    }}

    .card {{
        background: {COLORS["white"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    }}
    .card-title {{
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 1rem;
        font-weight: 500;
        color: {COLORS["text"]};
        margin: 0 0 0.75rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .card-title .icon {{
        width: 20px;
        height: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        font-size: 14px;
    }}

    .metric-row {{
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }}
    .metric-card {{
        flex: 1;
        background: {COLORS["white"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
        transition: box-shadow 0.2s ease;
    }}
    .metric-card:hover {{
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    .metric-card .metric-value {{
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        margin: 0.25rem 0;
        line-height: 1;
    }}
    .metric-card .metric-label {{
        font-family: 'Roboto', sans-serif;
        font-size: 0.8rem;
        color: {COLORS["muted"]};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }}
    .metric-card .metric-delta {{
        font-family: 'Roboto', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 4px;
    }}
    .metric-card.blue {{ border-top: 3px solid {COLORS["primary"]}; }}
    .metric-card.blue .metric-value {{ color: {COLORS["primary"]}; }}
    .metric-card.green {{ border-top: 3px solid {COLORS["success"]}; }}
    .metric-card.green .metric-value {{ color: {COLORS["success"]}; }}
    .metric-card.red {{ border-top: 3px solid {COLORS["accent"]}; }}
    .metric-card.red .metric-value {{ color: {COLORS["accent"]}; }}
    .metric-card.amber {{ border-top: 3px solid #F9AB00; }}
    .metric-card.amber .metric-value {{ color: #F9AB00; }}

    .section-header {{
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 1.1rem;
        font-weight: 500;
        color: {COLORS["text"]};
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {COLORS["primary"]};
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .welcome-container {{
        text-align: center;
        padding: 3rem 2rem;
    }}
    .welcome-icon {{
        width: 80px;
        height: 80px;
        background: {COLORS["light_blue"]};
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }}
    .welcome-container h2 {{
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: {COLORS["text"]};
        margin-bottom: 0.5rem;
    }}
    .welcome-container .subtitle {{
        font-family: 'Roboto', sans-serif;
        font-size: 1rem;
        color: {COLORS["muted"]};
        margin-bottom: 2rem;
    }}

    .feature-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        max-width: 900px;
        margin: 0 auto;
        text-align: left;
    }}
    .feature-item {{
        background: {COLORS["white"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
        padding: 1.25rem;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }}
    .feature-item:hover {{
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transform: translateY(-1px);
    }}
    .feature-icon {{
        width: 40px;
        height: 40px;
        background: {COLORS["light_blue"]};
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        flex-shrink: 0;
    }}
    .feature-text h4 {{
        font-family: 'Google Sans', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: {COLORS["text"]};
        margin: 0 0 4px 0;
    }}
    .feature-text p {{
        font-family: 'Roboto', sans-serif;
        font-size: 0.8rem;
        color: {COLORS["muted"]};
        margin: 0;
        line-height: 1.4;
    }}

    .status-badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        font-family: 'Roboto', sans-serif;
    }}
    .status-matched {{
        background: {COLORS["light_green"]};
        color: {COLORS["success"]};
    }}
    .status-unmatched {{
        background: {COLORS["light_red"]};
        color: {COLORS["accent"]};
    }}

    .dataset-info {{
        display: flex;
        align-items: center;
        gap: 6px;
        font-family: 'Roboto', sans-serif;
        font-size: 0.8rem;
        color: {COLORS["muted"]};
        margin-top: 4px;
    }}
    .dataset-info .dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: {COLORS["success"]};
    }}

    .sidebar .element-container {{
        margin-bottom: 0.5rem;
    }}

    div[data-testid="stSidebar"] {{
        background: {COLORS["white"]};
        border-right: 1px solid {COLORS["border"]};
    }}
    div[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
        padding-top: 1.5rem;
    }}

    .sidebar-header {{
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        color: {COLORS["text"]};
        padding: 0.5rem 0;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid {COLORS["border"]};
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        border-bottom: 2px solid {COLORS["border"]};
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Google Sans', sans-serif;
        font-weight: 500;
        font-size: 0.85rem;
        padding: 8px 20px;
        border-radius: 8px 8px 0 0;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        overflow: hidden;
    }}
</style>
""", unsafe_allow_html=True)


if 'df1' not in st.session_state:
    st.session_state.df1 = None
if 'df2' not in st.session_state:
    st.session_state.df2 = None
if 'comparison_results' not in st.session_state:
    st.session_state.comparison_results = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Compare"


def render_header():
    st.markdown("""
    <div class="app-header">
        <h1>CSV Comparison Tool</h1>
        <p>Upload two datasets and perform advanced VLOOKUP-style matching operations</p>
    </div>
    """, unsafe_allow_html=True)


def render_metrics(stats):
    total = stats['total_records']
    matched = stats['matched_count']
    unmatched = stats['unmatched_count']
    dupes = stats['duplicate_keys']
    match_pct = stats['match_percentage']
    unmatch_pct = stats['unmatch_percentage']

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card blue">
            <div class="metric-label">Total Records</div>
            <div class="metric-value">{total:,}</div>
            <div class="metric-delta" style="color:{COLORS['muted']}">processed</div>
        </div>
        <div class="metric-card green">
            <div class="metric-label">Matched</div>
            <div class="metric-value">{matched:,}</div>
            <div class="metric-delta" style="color:{COLORS['success']}">{match_pct:.1f}% match rate</div>
        </div>
        <div class="metric-card red">
            <div class="metric-label">Unmatched</div>
            <div class="metric-value">{unmatched:,}</div>
            <div class="metric-delta" style="color:{COLORS['accent']}">{unmatch_pct:.1f}% unmatched</div>
        </div>
        <div class="metric-card amber">
            <div class="metric-label">Duplicate Keys</div>
            <div class="metric-value">{dupes:,}</div>
            <div class="metric-delta" style="color:{COLORS['muted']}">in lookup dataset</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    st.sidebar.markdown('<div class="sidebar-header">Navigation</div>', unsafe_allow_html=True)
    page = st.sidebar.radio(
        "Page",
        ["Compare", "How To"],
        index=0 if st.session_state.current_page == "Compare" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    if page != st.session_state.current_page:
        st.session_state.current_page = page
        st.rerun()

    if st.session_state.current_page == "How To":
        return

    st.sidebar.markdown('<div class="sidebar-header">Upload Datasets</div>', unsafe_allow_html=True)

    uploaded_file1 = st.sidebar.file_uploader(
        "Primary Dataset (CSV)",
        type=['csv'],
        key="file1",
        help="Upload the primary dataset for comparison"
    )

    uploaded_file2 = st.sidebar.file_uploader(
        "Lookup Dataset (CSV)",
        type=['csv'],
        key="file2",
        help="Upload the lookup dataset for comparison"
    )

    data_processor = DataProcessor()

    if uploaded_file1 is not None:
        try:
            with st.spinner("Processing primary dataset..."):
                st.session_state.df1 = data_processor.load_csv(uploaded_file1)
            st.sidebar.success(f"Primary: {len(st.session_state.df1):,} rows, {len(st.session_state.df1.columns)} columns")
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")
            st.session_state.df1 = None

    if uploaded_file2 is not None:
        try:
            with st.spinner("Processing lookup dataset..."):
                st.session_state.df2 = data_processor.load_csv(uploaded_file2)
            st.sidebar.success(f"Lookup: {len(st.session_state.df2):,} rows, {len(st.session_state.df2.columns)} columns")
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")
            st.session_state.df2 = None

    if st.session_state.df1 is not None or st.session_state.df2 is not None:
        st.sidebar.markdown("---")
        if st.sidebar.button("Clear All Data", type="secondary", use_container_width=True):
            st.session_state.df1 = None
            st.session_state.df2 = None
            st.session_state.comparison_results = None
            st.rerun()


def show_welcome_screen():
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">📊</div>
        <h2>Welcome to CSV Comparison Tool</h2>
        <p class="subtitle">Upload two CSV files using the sidebar to start comparing datasets</p>
    </div>
    <div class="feature-grid">
        <div class="feature-item">
            <div class="feature-icon">🔗</div>
            <div class="feature-text">
                <h4>VLOOKUP Matching</h4>
                <p>Match records between datasets using flexible key columns</p>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <div class="feature-text">
                <h4>10 Match Methods</h4>
                <p>Exact, fuzzy, prefix, domain, contains, and more matching types</p>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📈</div>
            <div class="feature-text">
                <h4>Visual Analytics</h4>
                <p>Charts and metrics showing match distribution and statistics</p>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📤</div>
            <div class="feature-text">
                <h4>Export Results</h4>
                <p>Download comparison results as CSV or Excel files</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_single_dataset():
    st.info("Upload both CSV files to enable comparison features.")

    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.df1 is not None:
            st.markdown('<div class="section-header">Primary Dataset</div>', unsafe_allow_html=True)
            st.dataframe(st.session_state.df1.head(10), use_container_width=True)
            st.markdown(f"""
            <div class="dataset-info">
                <div class="dot"></div>
                {st.session_state.df1.shape[0]:,} rows &middot; {st.session_state.df1.shape[1]} columns
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if st.session_state.df2 is not None:
            st.markdown('<div class="section-header">Lookup Dataset</div>', unsafe_allow_html=True)
            st.dataframe(st.session_state.df2.head(10), use_container_width=True)
            st.markdown(f"""
            <div class="dataset-info">
                <div class="dot"></div>
                {st.session_state.df2.shape[0]:,} rows &middot; {st.session_state.df2.shape[1]} columns
            </div>
            """, unsafe_allow_html=True)


def show_comparison_interface():
    df1, df2 = st.session_state.df1, st.session_state.df2

    tab_config, tab_preview = st.tabs(["Comparison", "Dataset Preview"])

    with tab_config:
        st.markdown('<div class="section-header">Configuration</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            lookup_column_df1 = st.selectbox(
                "Primary Key Column",
                options=df1.columns.tolist(),
                help="Column from the primary dataset to use as the lookup key"
            )

        with col2:
            lookup_column_df2 = st.selectbox(
                "Lookup Key Column",
                options=df2.columns.tolist(),
                help="Column from the lookup dataset to match against"
            )

        with col3:
            return_columns = st.multiselect(
                "Return Columns",
                options=df2.columns.tolist(),
                default=df2.columns.tolist()[:3] if len(df2.columns) >= 3 else df2.columns.tolist(),
                help="Columns from the lookup dataset to include in results"
            )

        col1, col2 = st.columns([3, 1])

        with col1:
            match_types = st.multiselect(
                "Match Methods (applied in order)",
                [
                    "Exact Match",
                    "Case Insensitive",
                    "Domain Prefix Match",
                    "Prefix Match",
                    "Suffix Match",
                    "Contains Match",
                    "Remove Special Chars",
                    "Numbers Only",
                    "Word Order Insensitive",
                    "Fuzzy Match"
                ],
                default=["Exact Match"],
                help="Select one or more methods. They are tried in order for each record until a match is found."
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            show_unmatched = st.checkbox(
                "Include unmatched records",
                value=True,
                help="Show records from the primary dataset that have no match in the lookup dataset"
            )

        col_btn, col_spacer = st.columns([1, 2])
        with col_btn:
            run_btn = st.button("Run Comparison", type="primary", use_container_width=True)

        if run_btn:
            if lookup_column_df1 and lookup_column_df2 and return_columns and match_types:
                with st.spinner("Running comparison..."):
                    comparison_engine = ComparisonEngine()
                    st.session_state.comparison_results = comparison_engine.vlookup_comparison(
                        df1, df2, lookup_column_df1, lookup_column_df2,
                        return_columns, match_types, show_unmatched
                    )
                st.rerun()
            else:
                st.error("Please select key columns, return columns, and at least one match method.")

        if st.session_state.comparison_results is not None:
            show_comparison_results()

    with tab_preview:
        st.markdown('<div class="section-header">Primary Dataset</div>', unsafe_allow_html=True)
        st.dataframe(df1.head(50), use_container_width=True)
        st.markdown(f"""
        <div class="dataset-info">
            <div class="dot"></div>
            {df1.shape[0]:,} rows &middot; {df1.shape[1]} columns (showing first 50 rows)
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Lookup Dataset</div>', unsafe_allow_html=True)
        st.dataframe(df2.head(50), use_container_width=True)
        st.markdown(f"""
        <div class="dataset-info">
            <div class="dot"></div>
            {df2.shape[0]:,} rows &middot; {df2.shape[1]} columns (showing first 50 rows)
        </div>
        """, unsafe_allow_html=True)


def show_comparison_results():
    results = st.session_state.comparison_results
    stats = results['stats']

    st.markdown('<div class="section-header">Results</div>', unsafe_allow_html=True)
    render_metrics(stats)

    if stats['matched_count'] > 0 or stats['unmatched_count'] > 0:
        col1, col2 = st.columns(2)

        with col1:
            fig_donut = go.Figure(data=[go.Pie(
                values=[stats['matched_count'], stats['unmatched_count']],
                labels=['Matched', 'Unmatched'],
                hole=0.6,
                marker_colors=[COLORS['success'], COLORS['accent']],
                textinfo='label+percent',
                textfont_size=13,
                textfont_family='Roboto',
            )])
            fig_donut.update_layout(
                title=dict(text="Match Distribution", font=dict(size=14, family='Google Sans, Roboto')),
                height=280,
                margin=dict(t=40, b=20, l=20, r=20),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with col2:
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=['Matched', 'Unmatched'],
                    y=[stats['matched_count'], stats['unmatched_count']],
                    marker_color=[COLORS['success'], COLORS['accent']],
                    text=[f"{stats['matched_count']:,}", f"{stats['unmatched_count']:,}"],
                    textposition='outside',
                    textfont=dict(size=13, family='Roboto', color=COLORS['text']),
                    width=0.5,
                )
            ])
            fig_bar.update_layout(
                title=dict(text="Comparison Summary", font=dict(size=14, family='Google Sans, Roboto')),
                height=280,
                margin=dict(t=40, b=20, l=20, r=20),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                yaxis=dict(showgrid=True, gridcolor=COLORS['border'], zeroline=False),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('<div class="section-header">Detailed Results</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        filter_option = st.selectbox(
            "Filter",
            ["All Records", "Matched Only", "Unmatched Only"],
            label_visibility="collapsed"
        )
    with col2:
        display_rows = st.selectbox(
            "Rows",
            [50, 100, 250, 500, 1000],
            index=0,
            format_func=lambda x: f"Show {x} rows",
            label_visibility="collapsed"
        )

    filtered_data = results['combined_data'].copy()
    if filter_option == "Matched Only":
        filtered_data = filtered_data[filtered_data['_match_status'] == 'Matched']
    elif filter_option == "Unmatched Only":
        filtered_data = filtered_data[filtered_data['_match_status'] == 'Unmatched']

    display_data = filtered_data.head(display_rows)
    total_cells = len(display_data) * len(display_data.columns)

    if total_cells <= 50000 and '_match_status' in display_data.columns:
        def highlight_rows(row):
            if row.get('_match_status') == 'Matched':
                return [f'background-color: {COLORS["light_green"]}'] * len(row)
            else:
                return [f'background-color: {COLORS["light_red"]}'] * len(row)
        st.dataframe(
            display_data.style.apply(highlight_rows, axis=1),
            use_container_width=True,
            height=450
        )
    else:
        st.dataframe(display_data, use_container_width=True, height=450)

    st.markdown(f"""
    <div class="dataset-info" style="margin-bottom: 1rem;">
        <div class="dot"></div>
        Showing {len(display_data):,} of {len(filtered_data):,} filtered records ({len(results['combined_data']):,} total)
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Export</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        csv_data = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="comparison_results.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            filtered_data.to_excel(writer, sheet_name='Comparison Results', index=False)
            pd.DataFrame([stats]).to_excel(writer, sheet_name='Summary', index=False)

        st.download_button(
            label="Download Excel",
            data=excel_buffer.getvalue(),
            file_name="comparison_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


def show_how_to_page():
    st.markdown(f"""
    <div class="section-header">Getting Started</div>
    <div class="card">
        <div class="card-title"><span class="icon">1</span> Prepare Your CSV Files</div>
        <p style="font-family: Roboto, sans-serif; font-size: 0.9rem; color: {COLORS['text']}; line-height: 1.7; margin: 0;">
            You need two CSV files to compare. The <strong>Primary Dataset</strong> is your main data, 
            and the <strong>Lookup Dataset</strong> is where you want to find matching records.
            Both files should have at least one column with values that can be matched between them.
        </p>
    </div>

    <div class="card">
        <div class="card-title"><span class="icon">2</span> Upload Your Files</div>
        <p style="font-family: Roboto, sans-serif; font-size: 0.9rem; color: {COLORS['text']}; line-height: 1.7; margin: 0;">
            Use the sidebar on the left to upload your CSV files. Click <strong>"Primary Dataset (CSV)"</strong> 
            to upload your main file, and <strong>"Lookup Dataset (CSV)"</strong> to upload the file you want 
            to match against. The tool supports files with different delimiters (comma, semicolon, tab, pipe) 
            and various text encodings.
        </p>
    </div>

    <div class="card">
        <div class="card-title"><span class="icon">3</span> Configure the Comparison</div>
        <p style="font-family: Roboto, sans-serif; font-size: 0.9rem; color: {COLORS['text']}; line-height: 1.7; margin: 0;">
            Once both files are uploaded, you will see the Comparison tab. Configure these settings:
        </p>
        <ul style="font-family: Roboto, sans-serif; font-size: 0.9rem; color: {COLORS['text']}; line-height: 1.8; margin-top: 8px;">
            <li><strong>Primary Key Column</strong> &ndash; The column in your primary dataset that contains the values to look up.</li>
            <li><strong>Lookup Key Column</strong> &ndash; The column in the lookup dataset that should match the primary key.</li>
            <li><strong>Return Columns</strong> &ndash; Which columns from the lookup dataset you want to include in the results.</li>
        </ul>
    </div>

    <div class="card">
        <div class="card-title"><span class="icon">4</span> Choose Match Methods</div>
        <p style="font-family: Roboto, sans-serif; font-size: 0.9rem; color: {COLORS['text']}; line-height: 1.7; margin: 0 0 8px 0;">
            Select one or more matching methods. When you select multiple methods, the tool tries each one 
            in order for every record until it finds a match. This lets you catch different types of data variations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">Match Methods Explained</div>', unsafe_allow_html=True)

    methods = [
        ("Exact Match", "Values must be completely identical. Use this when your data is clean and consistent.",
         "ABC-123", "ABC-123", "Matched"),
        ("Case Insensitive", "Ignores uppercase and lowercase differences.",
         "John Smith", "john smith", "Matched"),
        ("Domain Prefix Match", "Extracts the part before the first dot and compares. Ideal for hostnames, domain names, and device identifiers.",
         "server01.company.com", "server01", "Matched"),
        ("Prefix Match", "Matches if either value starts with the other value.",
         "PROD-12345-A", "PROD-12345", "Matched"),
        ("Suffix Match", "Matches if either value ends with the other value.",
         "US-12345", "12345", "Matched"),
        ("Contains Match", "Matches if one value appears anywhere inside the other.",
         "John A. Smith Jr.", "Smith", "Matched"),
        ("Remove Special Chars", "Strips all non-alphanumeric characters before comparing.",
         "ABC-123-XYZ", "ABC123XYZ", "Matched"),
        ("Numbers Only", "Extracts and compares only the numeric portions of each value.",
         "INV-2024-001", "PO-2024-001", "Matched"),
        ("Word Order Insensitive", "Matches if both values contain the same words regardless of order.",
         "Smith John", "John Smith", "Matched"),
        ("Fuzzy Match", "Matches values that are at least 80% similar. Great for catching typos and minor variations.",
         "Microsoft Corp", "Microsft Corp", "Matched"),
    ]

    for name, desc, val1, val2, result in methods:
        st.markdown(f"""
        <div class="card">
            <div class="card-title" style="margin-bottom: 4px;">
                <span style="background: {COLORS['light_blue']}; color: {COLORS['primary']}; padding: 2px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 500;">{name}</span>
            </div>
            <p style="font-family: Roboto, sans-serif; font-size: 0.88rem; color: {COLORS['text']}; line-height: 1.6; margin: 4px 0 10px 0;">{desc}</p>
            <div style="display: flex; align-items: center; gap: 8px; font-family: Roboto Mono, monospace; font-size: 0.82rem;">
                <span style="background: {COLORS['bg']}; padding: 4px 12px; border-radius: 6px; border: 1px solid {COLORS['border']};">{val1}</span>
                <span style="color: {COLORS['muted']};">vs</span>
                <span style="background: {COLORS['bg']}; padding: 4px 12px; border-radius: 6px; border: 1px solid {COLORS['border']};">{val2}</span>
                <span style="color: {COLORS['muted']};">&rarr;</span>
                <span class="status-badge status-matched">{result}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="section-header">Understanding Results</div>

    <div class="card">
        <div class="card-title"><span class="icon">📊</span> Metrics</div>
        <ul style="font-family: Roboto, sans-serif; font-size: 0.9rem; color: {COLORS['text']}; line-height: 1.8; margin: 0;">
            <li><strong>Total Records</strong> &ndash; The number of records in your primary dataset that were processed.</li>
            <li><strong>Matched</strong> &ndash; Records that found a corresponding entry in the lookup dataset.</li>
            <li><strong>Unmatched</strong> &ndash; Records with no match found in the lookup dataset.</li>
            <li><strong>Duplicate Keys</strong> &ndash; How many duplicate values exist in the lookup key column. Duplicates mean only the first occurrence is used for matching.</li>
        </ul>
    </div>

    <div class="card">
        <div class="card-title"><span class="icon">📋</span> Results Table</div>
        <p style="font-family: Roboto, sans-serif; font-size: 0.9rem; color: {COLORS['text']}; line-height: 1.7; margin: 0 0 8px 0;">
            The results table shows all records with their match status. Key columns in the results:
        </p>
        <ul style="font-family: Roboto, sans-serif; font-size: 0.9rem; color: {COLORS['text']}; line-height: 1.8; margin: 0;">
            <li><strong>_match_status</strong> &ndash; Whether the record was "Matched" or "Unmatched".</li>
            <li><strong>_match_type_used</strong> &ndash; Which match method successfully found the match (useful when using multiple methods).</li>
            <li><strong>_has_duplicates</strong> &ndash; Whether the matched key had duplicates in the lookup dataset.</li>
            <li><strong>[column]_from_lookup</strong> &ndash; Values returned from the lookup dataset for matched records.</li>
        </ul>
    </div>

    <div class="card">
        <div class="card-title"><span class="icon">📤</span> Exporting</div>
        <p style="font-family: Roboto, sans-serif; font-size: 0.9rem; color: {COLORS['text']}; line-height: 1.7; margin: 0;">
            You can filter the results (All, Matched Only, Unmatched Only) and then download them as a 
            <strong>CSV</strong> or <strong>Excel</strong> file. The Excel export includes a summary sheet 
            with comparison statistics.
        </p>
    </div>

    <div class="section-header">Tips for Best Results</div>
    <div class="card">
        <ul style="font-family: Roboto, sans-serif; font-size: 0.9rem; color: {COLORS['text']}; line-height: 2; margin: 0;">
            <li>Start with <strong>Exact Match</strong> first, then add looser methods to catch remaining unmatched records.</li>
            <li>The order of match methods matters &ndash; put stricter methods first and looser ones last to avoid false positives.</li>
            <li>Use the <strong>Dataset Preview</strong> tab to inspect your data before running a comparison.</li>
            <li>For hostname/device matching, <strong>Domain Prefix Match</strong> combined with <strong>Case Insensitive</strong> works well.</li>
            <li>If you have dirty data with typos, add <strong>Fuzzy Match</strong> as the last method in your list.</li>
            <li>Check the <strong>_match_type_used</strong> column in results to see which method caught each match.</li>
            <li>Use the <strong>"Include unmatched records"</strong> checkbox to see which records still need attention.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def main():
    render_header()
    render_sidebar()

    if st.session_state.current_page == "How To":
        show_how_to_page()
    elif st.session_state.df1 is not None and st.session_state.df2 is not None:
        show_comparison_interface()
    elif st.session_state.df1 is not None or st.session_state.df2 is not None:
        show_single_dataset()
    else:
        show_welcome_screen()


if __name__ == "__main__":
    main()
