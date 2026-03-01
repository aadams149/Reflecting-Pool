"""
Help & FAQ plugin for Reflecting Pool.

Provides a user-friendly guide for non-technical users.  Designed to
be the first place new users look when they're unsure how things work.
"""

from plugin_loader import register


@register(
    "Help & FAQ",
    order=200,
    needs_df=False,
    description="Plain-language guide and frequently asked questions",
)
def render(ctx):
    import streamlit as st

    st.markdown(
        "Welcome to **Reflecting Pool**!  This guide answers the most "
        "common questions about how the app works.  Click any section "
        "below to expand it."
    )
    st.divider()

    # ------------------------------------------------------------------
    # 1. Getting Started
    # ------------------------------------------------------------------
    with st.expander("Getting Started", expanded=False):
        st.markdown("""
**What is Reflecting Pool?**

Reflecting Pool turns your handwritten journal into a searchable,
analysable digital archive.  You take photos of your journal pages,
the app reads the handwriting (using OCR - optical character
recognition), and then you can search, browse, and explore your
entries right here in the dashboard.

**Quick-start checklist**

1. Take clear photos of your journal pages (see *Adding Journal
   Entries* below for tips).
2. Place the photos in a folder on your computer.
3. Run the OCR pipeline to convert the photos into text - you can use
   the batch processor or the built-in **OCR Watcher** in the sidebar.
4. Open this dashboard and make sure the *OCR Output Directory* in the
   sidebar points to the folder that contains the processed text.
5. Start exploring!
""")

    # ------------------------------------------------------------------
    # 2. Adding Journal Entries
    # ------------------------------------------------------------------
    with st.expander("Adding Journal Entries", expanded=False):
        st.markdown("""
**Taking good photos**

- Use natural, even lighting - avoid harsh shadows across the page.
- Hold the camera directly above the page so the text isn't skewed.
- Make sure the full page is visible and in focus.
- Supported image formats: **JPG**, **JPEG**, **PNG**, and **HEIC**.

**Processing photos**

There are two ways to turn photos into text:

| Method | How it works |
|--------|-------------|
| **Batch processing** | Place all photos in a folder, then run the OCR command once.  Best for a large backlog of photos. |
| **OCR Watcher** | Use the *OCR Watcher* section in the sidebar to watch a folder.  Every time you add a new photo, it's processed automatically. |

After processing, each entry gets a date (extracted from the filename
or the photo's creation date) and a plain-text file.
""")

    # ------------------------------------------------------------------
    # 3. Searching Your Journal
    # ------------------------------------------------------------------
    with st.expander("Searching Your Journal", expanded=False):
        st.markdown("""
**How search works**

Reflecting Pool uses *semantic search*, which means you can search by
meaning rather than exact words.  For example, searching for
"feeling stressed about deadlines" will find entries that talk about
work pressure even if those exact words don't appear.

**Two ways to search**

- **Sidebar search** - type a query in the *Search* box on the left
  and click **Search**.  Results appear right in the sidebar.
- **Chat tab** - open the **Chat** tab and have a conversation about
  your journal.  The AI assistant can pull relevant entries into its
  answers.

**Tips for better results**

- Use descriptive phrases rather than single words.
- Try different angles: "hiking" vs. "time spent outdoors".
- The search looks at *all* entries, not just the ones visible in the
  current date filter.
""")

    # ------------------------------------------------------------------
    # 4. Understanding Analytics
    # ------------------------------------------------------------------
    with st.expander("Understanding the Analytics", expanded=False):
        if ctx.df.empty:
            st.info(
                "Once you add journal entries, the **Analytics** tab will "
                "show charts and statistics about your writing."
            )
        else:
            st.markdown(f"You currently have **{len(ctx.df)}** entries loaded.")

        st.markdown("""
**Sentiment analysis**

Each entry is given a *sentiment score* between -1 (very negative) and
+1 (very positive).  This is calculated automatically using a tool
called VADER, which looks at the words you used.  It's a rough guide
to the emotional tone - not a clinical assessment.

- Scores above **+0.3** are considered positive.
- Scores below **-0.3** are considered negative.
- Everything in between is neutral.

**Charts you'll see**

| Chart | What it shows |
|-------|--------------|
| Sentiment over time | A timeline of how your mood trends across entries |
| Word count over time | How much you wrote in each entry |
| Common words | The words that appear most frequently |
| Entry length distribution | A histogram of entry lengths |
""")

    # ------------------------------------------------------------------
    # 5. Music Connections
    # ------------------------------------------------------------------
    with st.expander("Music Connections", expanded=False):
        st.markdown("""
**What the Music tab does**

If you have Spotify listening data, Reflecting Pool can show what you
were listening to around the time of each journal entry.  This can
surface interesting connections between your mood and your music.

**How to add Spotify data**

1. Request your data from Spotify (Account > Privacy > Download your data).
2. Place the exported JSON files in the expected location.
3. The **Music** tab will automatically pick them up.

If you don't use Spotify or haven't added the data yet, the Music tab
will simply let you know.
""")

    # ------------------------------------------------------------------
    # 6. Customizing Appearance
    # ------------------------------------------------------------------
    with st.expander("Customizing Appearance", expanded=False):
        st.markdown("""
**Themes and colours**

Open the **Appearance** tab to change the look of the dashboard.  You
can adjust:

- **Primary colour** - the accent colour used on buttons and highlights
- **Background colour** - the main background of the page
- **Text colour** - the default text colour
- **Font family** and **font size**

Changes are saved automatically and will persist the next time you open
the dashboard.

**Resetting to defaults**

Use the *Reset to Defaults* button on the Appearance tab to go back to
the original look.
""")

    # ------------------------------------------------------------------
    # 7. Troubleshooting
    # ------------------------------------------------------------------
    with st.expander("Troubleshooting", expanded=False):
        st.markdown("""
**"No journal entries found"**

- Make sure the *OCR Output Directory* in the sidebar points to the
  correct folder (it should contain `text/` and `metadata/`
  sub-folders).
- Confirm that you've run the OCR pipeline at least once so there are
  processed text files.

**Search returns no results**

- If you just processed new photos, click *Ingest to RAG* in the
  sidebar to update the search database.
- Try broader search terms.

**OCR Watcher isn't detecting new photos**

- Verify the *Watch Folder* path in the sidebar is correct.
- Make sure the watcher shows a green **Running** indicator.
- The watcher only picks up newly created files - it won't
  reprocess files that were already there when it started.
- Supported formats: JPG, JPEG, PNG, HEIC.

**The app feels slow**

- Large numbers of entries can take a moment to load.  Try narrowing
  the date range in the sidebar.
- The first search after starting the app may be slower while the
  database loads into memory.

**Something else?**

Check the project's GitHub page for open issues, or create a new
issue describing what you're experiencing.
""")
