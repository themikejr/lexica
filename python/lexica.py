from textual.app import App, ComposeResult
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Container, Vertical
from textual.reactive import Reactive
import sqlite3
import re


class GreekLexicon(App):
    CSS = """

    Screen {
        layout: vertical;
        align: center middle;
    }
    Vertical.header {
        width: 80%;
        align: center middle;
    }
    Label.title {
        text-align: center;
        margin: 0;
        text-style: bold;
        color: white; /* To make the title stand out */
    }
    Label.subtitle {
        text-align: center;
        margin: 0;
        text-style: italic;
        color: grey;
    }
    Vertical.search-section {
        width: 80%;
        height: auto;
        align: left top;
        margin: 1 0;
    }
    Label.input-label, Label.matching-words-label {
        margin: 0 0 1 0; /* Reduced spacing for tighter layout */
        text-align: left;
        text-style: bold;
    }
    Input {
        width: 100%;
        height: 2;
        padding: 0 1;
        border: solid white;
        color: white; /* Changed from text-color */
        background: black;
    }
    ListView.matching-words {
        width: 100%;
        height: 10;
        border: solid white;
        padding: 1;
        overflow: auto;
    }
    Label.results {
        width: 80%;
        height: 12;
        overflow: auto;
        border: solid white;
        padding: 1;
    }
    """

    highlighted_word = Reactive("")  # The selected word for highlighting

    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect("lexica.sqlite3")
        self.cursor = self.conn.cursor()

    def compose(self) -> ComposeResult:
        # Header section
        yield Vertical(
            Label("Lexica", classes="title"),
            Label("Search the GNT", classes="subtitle"),
            classes="header",
        )
        # Search section: Input + Matching Words
        yield Vertical(
            Label("Search Input:", classes="input-label"),
            Input(placeholder="Type Greek word..."),
            Label("Matched Words:", classes="matching-words-label"),
            ListView(classes="matching-words"),
            classes="search-section",
        )
        # Results section
        yield Label(classes="results")

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Update autocomplete options based on the input text.
        """
        if len(event.value) < 2:
            self.query_one(".matching-words", ListView).clear()
            return

        query = """
        SELECT DISTINCT text
        FROM "macula-greek-SBLGNT"
        WHERE text_nfd LIKE ?
        LIMIT 10
        """
        search = f"%{event.value.lower()}%"
        matches = self.cursor.execute(query, (search,)).fetchall()

        list_view = self.query_one(".matching-words", ListView)
        list_view.clear()
        if matches:
            for match in matches:
                list_view.append(ListItem(Label(match[0])))
            list_view.index = 0  # Automatically focus the first item
        else:
            list_view.append(ListItem(Label("No matches found")))

    def on_key(self, event) -> None:
        """
        Handle key events to navigate between Input and ListView like a combobox.
        """
        input_widget = self.query_one(Input)
        list_view = self.query_one(".matching-words", ListView)

        if input_widget.has_focus:
            if event.key == "down":
                # Move focus to the ListView
                list_view.focus()
                if list_view.children:
                    list_view.index = 0
        elif list_view.has_focus:
            if event.key == "up" and list_view.index == 0:
                # Move focus back to Input
                input_widget.focus()
            elif event.key == "enter" and list_view.index is not None:
                # Trigger selection on Enter
                selected_item = list_view.children[list_view.index]
                self.on_list_view_selected(
                    ListView.Selected(list_view=list_view, item=selected_item)
                )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """
        Display verses for the selected word.
        """
        selected_label = event.item.query_one(Label)
        selected_word = selected_label.renderable

        # Update highlighted_word with the selected word
        self.highlighted_word = selected_word.lower()

        query = """
        WITH matching_verses AS (
            SELECT DISTINCT substr(id, 1, 8) as verse_id
            FROM "macula-greek-SBLGNT" 
            WHERE normalized = ?
        )
        SELECT 
            substr(m.id, 1, 2) as book,
            substr(m.id, 3, 3) as chapter,
            substr(m.id, 6, 3) as verse,
            group_concat(m.text || m.after, '') as verse_text
        FROM "macula-greek-SBLGNT" m
        JOIN matching_verses mv ON substr(m.id, 1, 8) = mv.verse_id
        GROUP BY substr(m.id, 1, 8)
        """

        # Fetch matching verses
        verses = self.cursor.execute(query, (selected_word,)).fetchall()

        # Format the results for display
        result_text = "\n".join(
            f"{v[0]}:{v[1]}:{v[2]} - {self._highlight_word(v[3])}" for v in verses
        )
        self.query_one(".results", Label).update(result_text)

    def _highlight_word(self, verse_text: str) -> str:
        """
        Highlight the selected word in the verse text, case-insensitively.
        """
        word = self.highlighted_word
        if not word:
            return verse_text

        # Use a regex for case-insensitive replacement
        regex = re.compile(re.escape(word), re.IGNORECASE)
        return regex.sub(f"[bold yellow]{word}[/bold yellow]", verse_text)

    def on_exit(self):
        """
        Close the database connection on exit.
        """
        self.conn.close()


if __name__ == "__main__":
    app = GreekLexicon()
    app.run()
