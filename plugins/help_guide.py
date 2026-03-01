"""
Help & FAQ plugin for Reflecting Pool.

Provides a user-friendly usage guide and FAQ for non-technical users.
Designed to be the first place new users look when they're unsure how
things work.
"""

from plugin_loader import register

GITHUB_REPO = "https://github.com/aadams149/Reflecting-Pool"
GITHUB_PROFILE = "https://github.com/aadams149"


@register(
    "Help & FAQ",
    order=200,
    needs_df=False,
    description="Plain-language usage guide and frequently asked questions",
)
def render(ctx):
    import streamlit as st

    st.markdown(
        "Welcome to **Reflecting Pool**! This guide covers how to use "
        "the app and answers frequently asked questions. Pick a section "
        "below to get started."
    )

    # GitHub links
    st.markdown(
        f'<a href="{GITHUB_REPO}" target="_blank" title="View on GitHub">'
        '<img src="https://github.githubassets.com/favicons/favicon-dark.svg" '
        'width="20" style="vertical-align: middle; margin-right: 6px;" />'
        "Reflecting Pool on GitHub</a>"
        "&nbsp;&nbsp;|&nbsp;&nbsp;"
        f'<a href="{GITHUB_PROFILE}" target="_blank">@aadams149</a>',
        unsafe_allow_html=True,
    )
    st.divider()

    # ==================================================================
    # USAGE GUIDE
    # ==================================================================
    st.subheader("Usage Guide")

    # ------------------------------------------------------------------
    # 1. Getting Started
    # ------------------------------------------------------------------
    with st.expander("Getting Started", expanded=False):
        st.markdown("""
**What is Reflecting Pool?**

Reflecting Pool turns your handwritten journal into a searchable,
analyzable digital archive. You take photos of your journal pages,
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
| **Batch processing** | Place all photos in a folder, then run the OCR command once. Best for a large backlog of photos. |
| **OCR Watcher** | Use the *OCR Watcher* section in the sidebar to watch a folder. Every time you add a new photo, it's processed automatically. |

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
meaning rather than exact words. For example, searching for
"feeling stressed about deadlines" will find entries that talk about
work pressure even if those exact words don't appear.

**Two ways to search**

- **Sidebar search** - type a query in the *Search* box on the left
  and click **Search**. Results appear right in the sidebar.
- **Chat tab** - open the **Chat** tab and have a conversation about
  your journal. The AI assistant can pull relevant entries into its
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
+1 (very positive). This is calculated automatically using a tool
called VADER, which looks at the words you used. It's a rough guide
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

Reflecting Pool scans your journal entries for mentions of songs and
artists, then looks them up on Apple Music / iTunes to show album
artwork, track details, and preview links. It's a fun way to see
what music was on your mind while you were writing.

**How to get the best results**

The detection works best when you're specific in your journal:

- **Use quotes** - *listened to "Everlong" by Foo Fighters*
- **Mention artists** - *been listening to a lot of Radiohead lately*
- **Use colons** - *Song: "Karma Police"*

If the Music tab says no mentions were detected, try writing about
songs or artists in your entries and they'll appear next time.
""")

    # ------------------------------------------------------------------
    # 6. Customizing Appearance
    # ------------------------------------------------------------------
    with st.expander("Customizing Appearance", expanded=False):
        st.markdown("""
**Themes and colors**

Open the **Appearance** tab to change the look of the dashboard. You
can adjust:

- **Primary color** - the accent color used on buttons and highlights
- **Background color** - the main background of the page
- **Text color** - the default text color
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
  subfolders).
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

- Large numbers of entries can take a moment to load. Try narrowing
  the date range in the sidebar.
- The first search after starting the app may be slower while the
  database loads into memory.
""")

    # ==================================================================
    # FAQ
    # ==================================================================
    st.divider()
    st.subheader("Frequently Asked Questions")

    with st.expander("Does Reflecting Pool share my data with anyone?", expanded=False):
        st.markdown("""
**No.** Reflecting Pool runs entirely on your own computer. Your
journal text, photos, and search database all stay on your machine.
Nothing is uploaded to the cloud or shared with third parties.

The only network calls the app makes are:

- **Apple Music / iTunes lookups** when the Music tab searches for
  song metadata (only the song or artist name is sent, not your
  journal text).
- **Chat tab** requests, if you've configured an AI provider - only
  the specific journal excerpts relevant to your question are sent.

You can use the app completely offline if you skip the Music and Chat
features.
""")

    with st.expander("I think I've found a bug. How can I report it?", expanded=False):
        st.markdown(f"""
The best way to report a bug is to open an issue on GitHub:

1. Go to the [Reflecting Pool Issues page]({GITHUB_REPO}/issues).
2. Click **New Issue**.
3. Describe what happened, what you expected, and any error messages
   you saw.

If you're not comfortable with GitHub, you can also reach the
developer at their [GitHub profile]({GITHUB_PROFILE}).
""")

    with st.expander("What languages does Reflecting Pool support?", expanded=False):
        st.markdown("""
Currently, Reflecting Pool is optimized for **English** handwriting.
The OCR engine (Tesseract) supports many languages, but the sentiment
analysis and text processing features are English-focused.

Support for additional languages is something we'd like to add in the
future.
""")

    with st.expander("Can I use typed/printed text instead of handwriting?", expanded=False):
        st.markdown("""
Yes! The OCR engine works with both handwritten and printed text.
In fact, printed text tends to be recognized more accurately. Just
take a photo of the page the same way you would for handwriting.
""")

    with st.expander("How accurate is the sentiment analysis?", expanded=False):
        st.markdown("""
Sentiment analysis provides a general sense of the emotional tone of
each entry, but it's not perfect. The tool (VADER) was designed for
social media text, so it works best with straightforward language.

Things to keep in mind:

- **Sarcasm and irony** are often misread.
- **Mixed entries** (good and bad things in one entry) may average out
  to neutral.
- The scores are most useful as a **general trend** over time rather
  than a precise measurement of any single entry.
""")

    with st.expander("Can I back up my data?", expanded=False):
        st.markdown("""
Yes. Your data lives in a few places on your computer:

| What | Where |
|------|-------|
| Original photos | Wherever you saved them |
| OCR output (text + metadata) | The *OCR Output Directory* shown in the sidebar |
| Search database | The *RAG Database Path* shown in the sidebar |
| Theme settings | `theme.json` in the project folder |

To back up, simply copy these folders to an external drive or cloud
storage. The search database can also be rebuilt at any time by
clicking *Ingest to RAG* in the sidebar.
""")

    with st.expander("Can I add plugins or extend the app?", expanded=False):
        st.markdown(f"""
Yes! Reflecting Pool has a plugin system. You can add new tabs by
dropping a Python file into the `plugins/` folder. Each plugin is a
small script that uses the `@register` decorator to add itself to the
dashboard.

For details on how to write a plugin, see the
[plugins README]({GITHUB_REPO}/tree/main/plugins) on GitHub.
""")

    with st.expander("Do I need an internet connection?", expanded=False):
        st.markdown("""
For most features, **no**. The OCR processing, analytics, search, and
appearance customization all work offline.

You will need an internet connection for:

- **Music tab** - looks up song info on Apple Music / iTunes.
- **Chat tab** - sends queries to an AI provider (if configured).
""")
