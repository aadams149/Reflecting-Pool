"""Word Cloud - Visual word frequency display."""
from plugin_loader import register


@register(
    "Word Cloud",
    order=110,
    description="Visual word cloud from your journal entries",
)
def render(ctx):
    import streamlit as st

    ctx.section_header("Word Cloud", "A visual representation of your most "
                       "frequently used words. Larger words appear more often.")

    if ctx.df.empty:
        st.info("No entries to display.")
        return

    n_words = st.slider("Number of words", 20, 200, 80, key="wc_n_words")
    word_freq = ctx.extract_common_words(ctx.df["text"].tolist(), n_words=n_words)

    if not word_freq:
        st.info("Not enough text to generate a word cloud.")
        return

    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt

        freq_dict = dict(word_freq)
        theme = ctx.load_theme()
        bg = theme.get("bg_color", "#ffffff")

        wc = WordCloud(
            width=1200, height=600,
            background_color=bg,
            colormap="viridis",
            max_words=n_words,
            prefer_horizontal=0.7,
        ).generate_from_frequencies(freq_dict)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
        plt.close(fig)

    except ImportError:
        st.info(
            "Install the `wordcloud` package for a visual word cloud:\n\n"
            "```\npip install wordcloud\n```\n\n"
            "Showing text-based fallback below."
        )
        # Fallback: HTML-based sized word display
        max_count = word_freq[0][1] if word_freq else 1
        html_parts = []
        for word, count in word_freq:
            size = 14 + int(36 * (count / max_count))
            opacity = 0.4 + 0.6 * (count / max_count)
            html_parts.append(
                f'<span style="font-size:{size}px; opacity:{opacity}; '
                f'margin:4px; display:inline-block;">{word}</span>'
            )
        st.markdown(
            f'<div style="line-height:2.5;">{"  ".join(html_parts)}</div>',
            unsafe_allow_html=True,
        )
