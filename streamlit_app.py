"""
Sugar Trap — Market Gap Analysis Dashboard
Helix CPG Partners | Open Food Facts Data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sugar Trap — Market Gap Analysis", layout="wide")

# ── Load pre-processed data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/dashboard_data.csv")
    protein_src = pd.read_csv("data/protein_sources.csv", index_col=0)
    return df, protein_src


df, protein_sources = load_data()

# ── Constants ────────────────────────────────────────────────────────────────
SUGAR_THRESHOLD = 20
PROTEIN_THRESHOLD = 10
SCORE_MAP = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
NS_COLORS = {"a": "#2d9e2d", "b": "#85bb2f", "c": "#fecb02", "d": "#ee8100", "e": "#e63e11"}

# ── Sidebar filters ─────────────────────────────────────────────────────────
st.sidebar.title("🔍 Filters")
categories = sorted(df["primary_category"].unique())
selected_cats = st.sidebar.multiselect(
    "Select Categories", categories, default=categories
)
filtered = df[df["primary_category"].isin(selected_cats)]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🍬 The Sugar Trap — Market Gap Analysis")
st.markdown(
    "Identifying **Blue Ocean** opportunities in the snack aisle: "
    "categories where demand for healthy products (High Protein, Low Sugar) "
    "isn't met by current offerings."
)

# ── Row 1: Nutrient Matrix + Blue Ocean Table ────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Nutrient Matrix: Sugar vs Protein")
    fig_scatter = px.scatter(
        filtered,
        x="sugars_100g",
        y="proteins_100g",
        color="primary_category",
        hover_data=["product_name", "brands"],
        opacity=0.35,
        labels={
            "sugars_100g": "Sugar (g / 100 g)",
            "proteins_100g": "Protein (g / 100 g)",
            "primary_category": "Category",
        },
    )
    # Quadrant lines
    fig_scatter.add_hline(y=PROTEIN_THRESHOLD, line_dash="dash", line_color="grey")
    fig_scatter.add_vline(x=SUGAR_THRESHOLD, line_dash="dash", line_color="grey")
    # Blue Ocean shading
    fig_scatter.add_shape(
        type="rect",
        x0=0, x1=SUGAR_THRESHOLD,
        y0=PROTEIN_THRESHOLD, y1=filtered["proteins_100g"].max(),
        fillcolor="green", opacity=0.06, line_width=0,
    )
    fig_scatter.update_layout(height=520, margin=dict(t=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    st.subheader("Blue Ocean %")
    gap = (
        filtered.groupby("primary_category")
        .apply(
            lambda g: pd.Series({
                "total": len(g),
                "BO %": round(
                    ((g["sugars_100g"] <= SUGAR_THRESHOLD) & (g["proteins_100g"] >= PROTEIN_THRESHOLD)).sum()
                    / len(g) * 100, 1
                ),
            })
        )
        .sort_values("BO %", ascending=True)
    )
    gap["total"] = gap["total"].astype(int)
    st.dataframe(gap, use_container_width=True)

# ── Row 2: Key Insight ───────────────────────────────────────────────────────
# Compute opportunity from FULL (unfiltered) data so insight stays stable
full_gap = (
    df.groupby("primary_category")
    .apply(
        lambda g: pd.Series({
            "total": len(g),
            "bo_pct": round(
                ((g["sugars_100g"] <= SUGAR_THRESHOLD) & (g["proteins_100g"] >= PROTEIN_THRESHOLD)).sum()
                / len(g) * 100, 1
            ),
        })
    )
)
full_gap["total"] = full_gap["total"].astype(int)
opportunity = full_gap[full_gap["total"] >= 500].sort_values("bo_pct")
top = opportunity.iloc[0]
top_cat = top.name

bo_products = df[
    (df["primary_category"] == top_cat)
    & (df["sugars_100g"] <= SUGAR_THRESHOLD)
    & (df["proteins_100g"] >= PROTEIN_THRESHOLD)
]
if len(bo_products) > 5:
    target_protein = round(bo_products["proteins_100g"].quantile(0.75))
    target_sugar = max(5, round(bo_products["sugars_100g"].quantile(0.25)))
else:
    target_protein = PROTEIN_THRESHOLD
    target_sugar = SUGAR_THRESHOLD // 2

st.success(
    f"🔑 **Key Insight:** The biggest market opportunity is in **{top_cat}**, "
    f"targeting products with **{target_protein} g of protein** and less than "
    f"**{target_sugar} g of sugar** per 100 g. Only **{top.bo_pct}%** of "
    f"{int(top.total):,} products in this category sit in the Blue Ocean quadrant."
)

# ── Row 3: Protein Sources + NutriScore ──────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Top Protein Sources (Blue Ocean)")
    top_src = protein_sources.head(10).sort_values("count")
    fig_prot = px.bar(
        top_src,
        x="count",
        y=top_src.index,
        orientation="h",
        labels={"count": "# Products Containing Ingredient", "index": ""},
        color_discrete_sequence=["#2d9e2d"],
    )
    fig_prot.update_layout(height=400, margin=dict(t=10))
    st.plotly_chart(fig_prot, use_container_width=True)

with col4:
    st.subheader("NutriScore Distribution by Category")
    scored = filtered[filtered["nutriscore_grade"].isin(SCORE_MAP.keys())].copy()
    if not scored.empty:
        grade_dist = (
            pd.crosstab(scored["primary_category"], scored["nutriscore_grade"], normalize="index") * 100
        )
        # Ensure columns in order a-e
        for g in ["a", "b", "c", "d", "e"]:
            if g not in grade_dist.columns:
                grade_dist[g] = 0.0
        grade_dist = grade_dist[["a", "b", "c", "d", "e"]]

        fig_ns = go.Figure()
        for grade in ["a", "b", "c", "d", "e"]:
            fig_ns.add_trace(go.Bar(
                y=grade_dist.index,
                x=grade_dist[grade],
                name=grade.upper(),
                orientation="h",
                marker_color=NS_COLORS[grade],
            ))
        fig_ns.update_layout(barmode="stack", height=400, margin=dict(t=10),
                             xaxis_title="% of Products", legend_title="NutriScore")
        st.plotly_chart(fig_ns, use_container_width=True)
    else:
        st.info("No NutriScore data for the selected categories.")
