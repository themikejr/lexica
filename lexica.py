from textual.app import App, ComposeResult
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Container
from textual.reactive import Reactive
import sqlite3


class GreekLexicon(App):
    CSS = """
    Screen {
        layout: vertical;
        align: center middle;
    }
    Container {
        layout: vertical;
        align: center middle;
        width: 80%;
        margin: 1 1;
        padding: 1;
    }
    Label.title {
        text-align: center;
        margin: 1;
        text-style: bold;
    }
    Label.subtitle {
        text-align: center;
        margin: 1;
        text-style: italic;
        color: grey;
    }
    Input {
        margin: 1;
        width: 100%;
    }
    ListView {
        height: auto;
        max-height: 20;
        width: 100%;
    }
    Label.results {
        width: 100%;
    }
    """

    def __init__(self):
        super().__init__()
        # Initialize the database connection and cursor
        self.conn = sqlite3.connect("lexica.sqlite3")
        self.cursor = self.conn.cursor()

    def compose(self) -> ComposeResult:
        # Title and subtitle
        yield Container(
            Label("Lexica", classes="title"),
            Label("Search the GNT", classes="subtitle"),
            Input(placeholder="Type Greek word..."),
            ListView(),
            Label(classes="results"),
        )

    highlighted_word = Reactive("")

    def on_input_changed(self, event: Input.Changed) -> None:
        if len(event.value) < 2:
            return

        query = """
        SELECT DISTINCT text
        FROM "macula-greek-SBLGNT"
        WHERE text_nfd LIKE ?
        LIMIT 10
        """

        # Store the highlighted word for later use
        self.highlighted_word = event.value.lower()
        search = f"%{self.highlighted_word}%"
        matches = self.cursor.execute(query, (search,)).fetchall()

        # Clear existing items and populate the ListView with clickable items
        list_view = self.query_one(ListView)
        list_view.clear()
        if not matches:
            list_view.append(ListItem(Label("No matches found")))
        else:
            for match in matches:
                list_view.append(ListItem(Label(match[0])))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """
        Handle selection of an item from the ListView.
        """
        selected_item = event.item.query_one(
            Label
        )  # Get the Label widget in the selected ListItem
        selected_word = selected_item.renderable  # Access the text content of the Label

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
        self.query_one(".results").update(result_text)

    def on_key(self, event) -> None:
        """
        Handle the Enter key to select the currently focused item in the ListView.
        """
        if event.key == "enter":
            list_view = self.query_one(ListView)
            if list_view.index is not None:  # Check if an item is focused
                selected_item = list_view.children[list_view.index]
                self.on_list_view_selected(ListView.Selected(item=selected_item))

    def _highlight_word(self, verse_text: str) -> str:
        """
        Highlight the currently selected word in the verse text.
        """
        word = self.highlighted_word
        if not word:
            return verse_text
        return verse_text.replace(word, f"[bold yellow]{word}[/bold yellow]")

    def on_exit(self):
        # Close the database connection when exiting the app
        self.conn.close()


if __name__ == "__main__":
    app = GreekLexicon()
    app.run()
