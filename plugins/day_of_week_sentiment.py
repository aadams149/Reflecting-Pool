"""Day-of-Week Sentiment - Analyze mood patterns by weekday."""
from plugin_loader import register


@register(
    "Day-of-Week",
    order=130,
    description="Sentiment and writing patterns broken down by day of the week",
)
def render(ctx):
    import streamlit as st

    ctx.section_header("Day-of-Week Analysis", "See how your mood and writing "
                       "habits vary across the week. Are Mondays really that bad?")

    if ctx.df.empty:
        st.info("No entries to display.")
        return

    import pandas as pd

    df = ctx.df.copy()

    if "sentiment" not in df.columns:
        st.warning("Sentiment data not available.")
        return

    df["day_name"] = df["date"].dt.day_name()
    df["day_num"] = df["date"].dt.dayofweek  # Monday=0

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]

    # --- Sentiment by day ---
    day_sentiment = (
        df.groupby("day_name")["sentiment"]
        .agg(["mean", "std", "count"])
        .reindex(day_order)
        .fillna(0)
    )

    try:
        import plotly.graph_objects as go

        theme = ctx.load_theme()
        link_color = theme.get("link_color", "#0066cc")

        # Bar chart: average sentiment per weekday
        fig = go.Figure()
        colors = [link_color if v >= 0 else "#e74c3c"
                  for v in day_sentiment["mean"]]
        fig.add_trace(go.Bar(
            x=day_order,
            y=day_sentiment["mean"],
            marker_color=colors,
            text=[f"{v:.3f}" for v in day_sentiment["mean"]],
            textposition="outside",
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.update_layout(
            title="Average Sentiment by Day of Week",
            xaxis_title="Day",
            yaxis_title="Avg Sentiment",
            yaxis_range=[
                min(-0.3, day_sentiment["mean"].min() - 0.1),
                max(0.3, day_sentiment["mean"].max() + 0.1),
            ],
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Bar chart: writing volume per weekday
        day_volume = (
            df.groupby("day_name")["word_count"]
            .agg(["mean", "sum", "count"])
            .reindex(day_order)
            .fillna(0)
        )

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=day_order,
            y=day_volume["mean"],
            marker_color=link_color,
            text=[f"{int(v)}" for v in day_volume["mean"]],
            textposition="outside",
            name="Avg words",
        ))
        fig2.update_layout(
            title="Average Words per Entry by Day",
            xaxis_title="Day",
            yaxis_title="Avg Word Count",
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)

    except ImportError:
        st.warning("Install `plotly` for charts. Showing table only.")

    # --- Summary metrics ---
    st.divider()
    st.subheader("Weekly Patterns")

    best_day_idx = day_sentiment["mean"].idxmax()
    worst_day_idx = day_sentiment["mean"].idxmin()
    busiest_day = df.groupby("day_name").size().reindex(day_order).idxmax()

    m1, m2, m3 = st.columns(3)
    m1.metric("Happiest Day", best_day_idx,
              delta=f"{day_sentiment.loc[best_day_idx, 'mean']:.3f}")
    m2.metric("Toughest Day", worst_day_idx,
              delta=f"{day_sentiment.loc[worst_day_idx, 'mean']:.3f}")
    m3.metric("Most Entries On", busiest_day,
              delta=f"{int(df.groupby('day_name').size().reindex(day_order).loc[busiest_day])} entries")

    # --- Breakdown table ---
    st.divider()
    st.subheader("Detailed Breakdown")

    table_data = []
    for day in day_order:
        day_df = df[df["day_name"] == day]
        if day_df.empty:
            table_data.append({
                "Day": day, "Entries": 0, "Avg Sentiment": "-",
                "Avg Words": "-", "Total Words": 0,
            })
        else:
            table_data.append({
                "Day": day,
                "Entries": len(day_df),
                "Avg Sentiment": f"{day_df['sentiment'].mean():.3f}",
                "Avg Words": f"{int(day_df['word_count'].mean()):,}",
                "Total Words": f"{int(day_df['word_count'].sum()):,}",
            })

    st.dataframe(
        pd.DataFrame(table_data).set_index("Day"),
        use_container_width=True,
    )
