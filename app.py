"""Customer Segmentation & Churn Pattern Analytics in European Banking.

Run locally with: streamlit run app.py
Expected data file: European_Bank.csv in the same directory as this script.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ----------------------------- Page setup ------------------------------------
st.set_page_config(
    page_title="European Bank | Churn Analytics",
    page_icon="ðŸ“Š",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).resolve().parent / "European_Bank.csv"
REQUIRED_COLUMNS = {
    "Geography",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "IsActiveMember",
    "Exited",
}
NAVY = "#16324F"
TEAL = "#138A8A"
CORAL = "#E76F51"

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.5rem; padding-bottom: 2.5rem;}
      [data-testid="stMetric"] {background:#F4F7FA; padding:16px 18px; border-radius:10px; border:1px solid #E4EAF0;}
      [data-testid="stMetricLabel"] {color:#536477;}
      .subtitle {color:#536477; font-size:1.02rem; margin-top:-0.4rem;}
      .note {background:#F4F7FA; border-left:4px solid #138A8A; padding:0.8rem 1rem; border-radius:4px;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------- Data loading ---------------------------------
@st.cache_data(show_spinner="Loading and checking the customer dataâ€¦")
def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    # Remove common exported-index columns without altering customer variables.
    df = df.loc[:, ~df.columns.astype(str).str.match(r"^Unnamed: ?\d*$")]
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    numeric_columns = [
        "Age", "Tenure", "Balance", "NumOfProducts", "IsActiveMember", "Exited"
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=numeric_columns + ["Geography"]).copy()
    df["Geography"] = df["Geography"].astype(str)
    df = df[df["Exited"].isin([0, 1])].copy()
    df["Exited"] = df["Exited"].astype(int)
    df["IsActiveMember"] = df["IsActiveMember"].astype(int)
    df["Age group"] = pd.cut(
        df["Age"],
        bins=[0, 29, 39, 49, 59, float("inf")],
        labels=["Under 30", "30â€“39", "40â€“49", "50â€“59", "60+"],
        include_lowest=True,
    )
    df["Tenure group"] = pd.cut(
        df["Tenure"],
        bins=[-1, 2, 5, 8, 10],
        labels=["0â€“2 years", "3â€“5 years", "6â€“8 years", "9â€“10 years"],
    )
    df["Credit score band"] = pd.cut(
        pd.to_numeric(df["CreditScore"], errors="coerce")
        if "CreditScore" in df.columns else pd.Series(float("nan"), index=df.index),
        bins=[-float("inf"), 579, 669, 739, 799, float("inf")],
        labels=["Up to 579", "580â€“669", "670â€“739", "740â€“799", "800+"],
    )
    return df


if not DATA_FILE.exists():
    st.error(
        "Could not find `European_Bank.csv`. Upload it to the same GitHub repository "
        "folder as `app.py`, then redeploy the app."
    )
    st.stop()

try:
    data = load_data(str(DATA_FILE))
except Exception as exc:
    st.error(f"Could not read the dataset: {exc}")
    st.stop()

if data.empty:
    st.error("The dataset has no usable customer rows after basic validation.")
    st.stop()


# ----------------------------- Header ---------------------------------------
st.title("Customer Segmentation & Churn Pattern Analytics")
st.markdown(
    '<div class="subtitle">European banking portfolio | Descriptive customer churn analysis</div>',
    unsafe_allow_html=True,
)
st.write("")


# ----------------------------- Sidebar filters -----------------------------
st.sidebar.header("Explore the portfolio")
all_geographies = sorted(data["Geography"].dropna().unique().tolist())
selected_geographies = st.sidebar.multiselect(
    "Geography", all_geographies, default=all_geographies
)
age_min, age_max = int(data["Age"].min()), int(data["Age"].max())
age_range = st.sidebar.slider("Age range", age_min, age_max, (age_min, age_max))
all_products = sorted(data["NumOfProducts"].dropna().unique().tolist())
selected_products = st.sidebar.multiselect(
    "Number of products", all_products, default=all_products
)
activity_labels = {0: "Inactive", 1: "Active"}
selected_activity_labels = st.sidebar.multiselect(
    "Activity status", ["Inactive", "Active"], default=["Inactive", "Active"]
)
selected_activity = [key for key, label in activity_labels.items() if label in selected_activity_labels]

filtered = data[
    data["Geography"].isin(selected_geographies)
    & data["Age"].between(age_range[0], age_range[1])
    & data["NumOfProducts"].isin(selected_products)
    & data["IsActiveMember"].isin(selected_activity)
].copy()

if filtered.empty:
    st.warning("No customers match these filters. Adjust one or more filters to continue.")
    st.stop()


# ----------------------------- KPI row --------------------------------------
customer_count = len(filtered)
churned_count = int(filtered["Exited"].sum())
retained_count = customer_count - churned_count
churn_rate = churned_count / customer_count if customer_count else 0
balance_total = filtered["Balance"].sum()
churned_balance = filtered.loc[filtered["Exited"] == 1, "Balance"].sum()
balance_share = churned_balance / balance_total if balance_total else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers in view", f"{customer_count:,}")
k2.metric("Churned customers", f"{churned_count:,}")
k3.metric("Churn rate", f"{churn_rate:.2%}")
k4.metric("Retained customers", f"{retained_count:,}")
k5.metric("Churned balance share", f"{balance_share:.2%}")

st.caption(
    "Balance figures are in unspecified dataset currency units. The balance share is not revenue, profit, or a measure of financial loss."
)


# ----------------------------- Aggregation helpers -------------------------
def summarize(frame: pd.DataFrame, group_col: str) -> pd.DataFrame:
    out = (
        frame.groupby(group_col, observed=False, dropna=False)
        .agg(customers=("Exited", "size"), churned=("Exited", "sum"))
        .reset_index()
    )
    out = out[out[group_col].notna()].copy()
    out["churn_rate"] = out["churned"] / out["customers"].replace(0, pd.NA)
    return out


def bar_rate(frame: pd.DataFrame, category: str, title: str, color: str = TEAL):
    stats = summarize(frame, category)
    if stats.empty:
        st.info("No data available for this selection.")
        return
    fig = px.bar(
        stats,
        x=category,
        y="churn_rate",
        text=stats["churn_rate"].map(lambda value: f"{value:.1%}"),
        hover_data={"customers": True, "churned": True, "churn_rate": ":.1%"},
        labels={category: category, "churn_rate": "Churn rate", "customers": "Customers", "churned": "Churned"},
        title=title,
        color_discrete_sequence=[color],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        yaxis_tickformat=".0%",
        yaxis_title="Churn rate",
        xaxis_title="",
        margin=dict(l=10, r=10, t=55, b=10),
        height=350,
        title_font_color=NAVY,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ----------------------------- Tabs -----------------------------------------
tab_overview, tab_segments, tab_detail = st.tabs(
    ["Portfolio overview", "Segment analysis", "Definitions & limitations"]
)

with tab_overview:
    left, right = st.columns(2)
    with left:
        geo_stats = summarize(filtered, "Geography")
        fig_geo = px.bar(
            geo_stats,
            x="Geography",
            y="churn_rate",
            text=geo_stats["churn_rate"].map(lambda value: f"{value:.1%}"),
            hover_data={"customers": True, "churned": True, "churn_rate": ":.1%"},
            labels={"churn_rate": "Churn rate", "customers": "Customers", "churned": "Churned"},
            title="Churn rate by geography",
            color_discrete_sequence=[TEAL],
        )
        fig_geo.update_traces(textposition="outside", cliponaxis=False)
        fig_geo.update_layout(yaxis_tickformat=".0%", yaxis_title="Churn rate", xaxis_title="", height=370, margin=dict(l=10,r=10,t=55,b=10), title_font_color=NAVY, showlegend=False)
        st.plotly_chart(fig_geo, use_container_width=True)
    with right:
        age_geo = (
            filtered.dropna(subset=["Age group"])
            .groupby(["Geography", "Age group"], observed=False)
            .agg(customers=("Exited", "size"), churned=("Exited", "sum"))
            .reset_index()
        )
        age_geo["churn_rate"] = age_geo["churned"] / age_geo["customers"].replace(0, pd.NA)
        heat = age_geo.pivot(index="Geography", columns="Age group", values="churn_rate")
        fig_heat = px.imshow(
            heat,
            text_auto=".1%",
            color_continuous_scale="Tealrose",
            aspect="auto",
            labels={"x": "Age group", "y": "Geography", "color": "Churn rate"},
            title="Churn rate by geography and age",
        )
        fig_heat.update_layout(height=370, margin=dict(l=10,r=10,t=55,b=10), title_font_color=NAVY, coloraxis_colorbar_tickformat=".0%")
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown(
        '<div class="note"><b>How to read this:</b> Compare each churn rate with the customer count behind it. A high rate in a small segment may be less stable than a similar rate in a large group.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("View geography summary"):
        geo_table = summarize(filtered, "Geography").rename(
            columns={"Geography": "Geography", "customers": "Customers", "churned": "Churned", "churn_rate": "Churn rate"}
        )
        if not geo_table.empty:
            geo_table["Churn rate"] = geo_table["Churn rate"].map(lambda value: f"{value:.2%}")
        st.dataframe(geo_table, hide_index=True, use_container_width=True)

with tab_segments:
    st.subheader("Churn across customer segments")
    col1, col2 = st.columns(2)
    with col1:
        bar_rate(filtered, "Age group", "Churn rate by age group")
        bar_rate(filtered, "NumOfProducts", "Churn rate by product count", CORAL)
        if "Credit score band" in filtered.columns and filtered["Credit score band"].notna().any():
            bar_rate(filtered, "Credit score band", "Churn rate by credit score band")
    with col2:
        bar_rate(filtered, "Tenure group", "Churn rate by tenure")
        activity_summary = filtered.copy()
        activity_summary["Activity status"] = activity_summary["IsActiveMember"].map(activity_labels)
        bar_rate(activity_summary, "Activity status", "Churn rate by activity status", CORAL)
        balance_data = filtered.copy()
        balance_data["Balance group"] = pd.cut(
            balance_data["Balance"],
            bins=[-0.01, 0, 50000, 100000, float("inf")],
            labels=["Zero", "1â€“50,000", "50,001â€“100,000", "Above 100,000"],
        )
        bar_rate(balance_data, "Balance group", "Churn rate by recorded balance band")

    st.markdown("#### Segment table")
    available_segments = [
        col for col in ["Geography", "Age group", "Tenure group", "NumOfProducts", "IsActiveMember", "Credit score band"]
        if col in filtered.columns and filtered[col].notna().any()
    ]
    chosen_segment = st.selectbox("Choose a segment for the table", available_segments)
    segment_table = summarize(filtered, chosen_segment).rename(
        columns={chosen_segment: "Segment", "customers": "Customers", "churned": "Churned", "churn_rate": "Churn rate"}
    )
    segment_table["Churn rate"] = segment_table["Churn rate"].map(lambda value: f"{value:.2%}")
    st.dataframe(segment_table, hide_index=True, use_container_width=True)

    if "NumOfProducts" in filtered.columns:
        three_four = filtered[filtered["NumOfProducts"].isin([3, 4])]
        if not three_four.empty:
            st.warning(
                "Product-count results for 3 or 4 products are based on much smaller groups than the 1- and 2-product groups. Treat the observed rates as a signal to investigateâ€”not evidence that product count causes churn."
            )

with tab_detail:
    st.subheader("Metric definitions")
    st.markdown(
        "- **Churn rate:** customers with `Exited = 1` divided by all customers in the displayed segment.\n"
        "- **Churned balance share:** the sum of recorded `Balance` for churned customers divided by the total recorded `Balance` in the current filtered view.\n"
        "- **Age groups:** Under 30, 30â€“39, 40â€“49, 50â€“59, and 60+.\n"
        "- **Tenure groups:** 0â€“2, 3â€“5, 6â€“8, and 9â€“10 years.\n"
        "- **Credit score bands:** up to 579, 580â€“669, 670â€“739, 740â€“799, and 800+ (when `CreditScore` is present)."
    )
    st.subheader("Interpretation and limitations")
    st.markdown(
        "This dashboard summarizes observed patterns in the supplied records. It does not establish causation, forecast future churn, or score individual customers. "
        "The data's currency, time period, sampling method, and business definitions are not confirmed. Balance values are dataset currency units and must not be described as euros, revenue, profit, or realized losses. "
        "Small segment sizes can produce volatile rates; always review counts alongside percentages. Any retention action should be tested with an appropriate comparison group and evaluated for incremental retention and cost."
    )
    st.subheader("Data checks")
    dup_count = int(data.duplicated().sum())
    missing_count = int(data.isna().sum().sum())
    d1, d2, d3 = st.columns(3)
    d1.metric("Rows loaded", f"{len(data):,}")
    d2.metric("Duplicate rows", f"{dup_count:,}")
    d3.metric("Missing cells after required-field validation", f"{missing_count:,}")

st.divider()
st.caption("Built with Streamlit, pandas, and Plotly. This dashboard is for descriptive analysis and educational purposes.")