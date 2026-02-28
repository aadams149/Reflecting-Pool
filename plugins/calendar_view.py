"""Calendar View - Monthly calendar grid with entry navigation."""
from plugin_loader import register


@register(
    "Calendar",
    order=120,
    description="Monthly calendar grid highlighting journal entry days",
)
def render(ctx):
    import calendar
    import streamlit as st

    ctx.section_header("Calendar View", "Browse your journal entries on a monthly "
                       "calendar. Days with entries are highlighted; click to preview.")

    if ctx.df.empty:
        st.info("No entries to display.")
        return

    df = ctx.df.copy()
    df["date_only"] = df["date"].dt.date

    # Build lookup: date -> list of row dicts
    entries_by_date = {}
    for _, row in df.iterrows():
        d = row["date"].date()
        entries_by_date.setdefault(d, []).append(row)

    # Month/year selector
    all_months = sorted(df["date"].dt.to_period("M").unique())
    if not all_months:
        st.info("No entries found.")
        return

    month_labels = [str(m) for m in all_months]
    default_idx = len(month_labels) - 1

    selected_label = st.selectbox(
        "Select month", month_labels, index=default_idx, key="cal_month"
    )

    # Parse selection
    year, month = map(int, selected_label.split("-"))

    # Count entries this month
    month_entries = [d for d in entries_by_date if d.year == year and d.month == month]
    st.caption(f"{len(month_entries)} entry day{'s' if len(month_entries) != 1 else ''} "
               f"in {calendar.month_name[month]} {year}")

    # Build calendar grid
    cal = calendar.Calendar(firstweekday=0)  # Monday start
    weeks = cal.monthdayscalendar(year, month)

    theme = ctx.load_theme()
    link_color = theme.get("link_color", "#0066cc")
    bg_color = theme.get("bg_color", "#ffffff")
    text_color = theme.get("text_color", "#111111")

    # Determine a subtle highlight for entry days
    highlight_bg = link_color + "22"  # 13% opacity hex
    header_bg = link_color + "11"

    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Render as an HTML table for clean calendar look
    html = f"""
    <style>
    .rp-cal {{ border-collapse: collapse; width: 100%; table-layout: fixed; }}
    .rp-cal th {{ background: {header_bg}; color: {text_color}; padding: 6px 4px;
                  text-align: center; font-size: 13px; font-weight: 600; }}
    .rp-cal td {{ border: 1px solid {link_color}22; padding: 8px 4px;
                  text-align: center; vertical-align: top; height: 52px;
                  font-size: 14px; color: {text_color}; }}
    .rp-cal .has-entry {{ background: {highlight_bg}; font-weight: 700; }}
    .rp-cal .empty {{ color: transparent; }}
    .rp-cal .entry-dot {{ display: block; width: 6px; height: 6px;
                          border-radius: 50%; background: {link_color};
                          margin: 4px auto 0; }}
    </style>
    <table class="rp-cal">
    <tr>{"".join(f'<th>{d}</th>' for d in day_names)}</tr>
    """

    import datetime

    for week in weeks:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += '<td class="empty">.</td>'
            else:
                d = datetime.date(year, month, day)
                has = d in entries_by_date
                cls = ' class="has-entry"' if has else ""
                dot = '<span class="entry-dot"></span>' if has else ""
                html += f"<td{cls}>{day}{dot}</td>"
        html += "</tr>"

    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

    # Day selector for preview
    st.divider()
    entry_days = sorted(month_entries)
    if not entry_days:
        st.info(f"No entries in {calendar.month_name[month]} {year}.")
        return

    selected_day = st.selectbox(
        "Preview entry",
        entry_days,
        format_func=lambda d: d.strftime("%A, %B %d"),
        key="cal_day_select",
    )

    if selected_day and selected_day in entries_by_date:
        for row in entries_by_date[selected_day]:
            sentiment = row.get("sentiment", None)
            sent_str = f" | Sentiment: {sentiment:.2f}" if sentiment is not None else ""
            st.caption(f"{row['date'].strftime('%Y-%m-%d')} - "
                       f"{row['word_count']} words{sent_str}")
            st.text(row["text"][:600] + ("..." if len(row["text"]) > 600 else ""))
