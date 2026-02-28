"""Read Entries - Full-text journal entry reader with navigation."""
from plugin_loader import register


@register(
    "Read Entries",
    order=140,
    description="Full-text entry viewer with prev/next navigation",
)
def render(ctx):
    import streamlit as st

    ctx.section_header("Read Entries", "Read your full journal entries one at a "
                       "time. Navigate with previous/next or jump to any date.")

    if ctx.df.empty:
        st.info("No entries to display.")
        return

    df = ctx.df.sort_values("date").reset_index(drop=True)
    n_entries = len(df)

    # Session state for current entry index
    if "fev_index" not in st.session_state:
        st.session_state.fev_index = n_entries - 1  # Start at most recent

    # Clamp index in case data changed
    idx = min(st.session_state.fev_index, n_entries - 1)
    idx = max(idx, 0)

    # Date selector
    all_dates = df["date"].dt.date.tolist()
    current_date = all_dates[idx]

    selected_date = st.selectbox(
        "Jump to date",
        all_dates,
        index=idx,
        format_func=lambda d: d.strftime("%A, %B %d, %Y"),
        key="fev_date_select",
    )

    # Find the index for the selected date
    if selected_date != current_date:
        for i, d in enumerate(all_dates):
            if d == selected_date:
                idx = i
                st.session_state.fev_index = idx
                break

    # Navigation buttons
    col_prev, col_counter, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("< Previous", key="fev_prev", disabled=(idx == 0),
                      use_container_width=True):
            st.session_state.fev_index = idx - 1
            st.rerun()

    with col_counter:
        st.markdown(
            f"<div style='text-align:center; padding-top:8px;'>"
            f"Entry {idx + 1} of {n_entries}</div>",
            unsafe_allow_html=True,
        )

    with col_next:
        if st.button("Next >", key="fev_next", disabled=(idx >= n_entries - 1),
                      use_container_width=True):
            st.session_state.fev_index = idx + 1
            st.rerun()

    # Display the entry
    row = df.iloc[idx]
    entry_date = row["date"]
    text = row["text"]
    word_count = row["word_count"]
    sentiment = row.get("sentiment", None)

    st.divider()

    # Metadata line
    meta_parts = [
        entry_date.strftime("%A, %B %d, %Y"),
        f"{word_count:,} words",
    ]
    if sentiment is not None:
        label = "positive" if sentiment > 0.05 else ("negative" if sentiment < -0.05 else "neutral")
        meta_parts.append(f"Sentiment: {sentiment:.2f} ({label})")

    st.caption(" | ".join(meta_parts))

    # Render full entry text with theme styling
    theme = ctx.load_theme()
    body_font = theme.get("body_font", "sans-serif")
    font_size = theme.get("font_size", 15)
    line_height = theme.get("line_height", 1.5)
    text_color = theme.get("text_color", "#111111")
    bg_color = theme.get("bg_color", "#ffffff")
    border_radius = theme.get("border_radius", 2)

    # Split into paragraphs for readability
    paragraphs = text.split("\n")
    formatted = "".join(
        f"<p style='margin-bottom: 0.8em;'>{p}</p>" if p.strip() else "<br/>"
        for p in paragraphs
    )

    st.markdown(
        f"""<div style="
            font-family: '{body_font}', serif;
            font-size: {font_size}px;
            line-height: {line_height};
            color: {text_color};
            background-color: {bg_color};
            padding: 1.5rem;
            border-radius: {border_radius}px;
            border: 1px solid #ddd;
            max-height: 600px;
            overflow-y: auto;
        ">{formatted}</div>""",
        unsafe_allow_html=True,
    )

    # Quick stats at bottom
    st.divider()
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Words", f"{word_count:,}")
    s2.metric("Characters", f"{row['char_count']:,}")
    if sentiment is not None:
        s3.metric("Sentiment", f"{sentiment:.2f}")
    else:
        s3.metric("Sentiment", "N/A")
    s4.metric("Date", entry_date.strftime("%Y-%m-%d"))
