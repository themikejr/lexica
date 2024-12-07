import argparse
import sqlite3
import re
import unicodedata


def strip_diacritics(text):
    """
    Remove diacritics from the given text.
    """
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def highlight_match(text, match):
    """
    Highlight the matching word in the text, ignoring diacritics.
    """
    # Strip diacritics from both text and match
    text_no_diacritics = strip_diacritics(text)
    match_no_diacritics = strip_diacritics(match)

    # Use regex for case-insensitive matching
    regex = re.compile(re.escape(match_no_diacritics), re.IGNORECASE)

    # Perform replacement using the original text for display
    start = 0
    highlighted = ""
    for match_obj in regex.finditer(text_no_diacritics):
        start_idx, end_idx = match_obj.span()
        highlighted += text[start:start_idx]  # Unmatched part
        highlighted += f"\033[93m{text[start_idx:end_idx]}\033[0m"  # Highlighted part
        start = end_idx
    highlighted += text[start:]  # Remaining unmatched part

    return highlighted


def find_words(db_path, partial_word):
    """
    Find words matching the partial query.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT DISTINCT text
    FROM "macula-greek-SBLGNT"
    WHERE text_nfd LIKE ?
    LIMIT 10
    """
    search_term = f"%{partial_word}%"
    results = cursor.execute(query, (search_term,)).fetchall()

    conn.close()

    if results:
        print(f"\nWords matching '{partial_word}':\n")
        for row in results:
            print(f"  - {highlight_match(row['text'], partial_word)}")
    else:
        print(f"\nNo matches found for '{partial_word}'.")


def search_verses(db_path, word):
    """
    Search for verses containing the given word and ensure proper spacing after tokens and punctuation.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    WITH matching_verses AS (
        SELECT DISTINCT substr(id, 1, 8) as verse_id
        FROM "macula-greek-SBLGNT"
        WHERE normalized = ?
    )
    SELECT 
        m.ref,
        m.text,
        m.after
    FROM "macula-greek-SBLGNT" m
    JOIN matching_verses mv ON substr(m.id, 1, 8) = mv.verse_id
    ORDER BY m.id
    """
    results = cursor.execute(query, (word,)).fetchall()
    conn.close()

    # Group results by verse reference
    verses = {}
    for row in results:
        ref = row["ref"].split("!")[0]
        token = row["text"]
        after = row["after"]

        # Add a space after punctuation if not already present
        if after and after[-1] in ",.;·" and not after.endswith(" "):
            after += " "

        # Add the token and the adjusted 'after' field
        token_with_after = token + after

        if ref not in verses:
            verses[ref] = []
        verses[ref].append(token_with_after)

    total_verses = len(verses)

    if verses:
        print(f"\nFound {total_verses} verse(s) containing '{word}':\n")
        for ref, tokens in verses.items():
            # Join tokens to form the verse text
            verse_text = highlight_match("".join(tokens), word)

            # Format and display the reference in bold
            print(f"\033[1m{ref}\033[0m")
            print(f"    {verse_text}\n")
    else:
        print(f"\nNo verses found containing '{word}'.")


def main():
    parser = argparse.ArgumentParser(description="Search the Greek New Testament.")
    parser.add_argument(
        "--db",
        type=str,
        default="lexica.sqlite3",
        help="Path to the SQLite database file (default: lexica.sqlite3)",
    )
    parser.add_argument(
        "--find-words",
        type=str,
        help="Partial word to search for matching words.",
    )
    parser.add_argument(
        "--search",
        type=str,
        help="Word to search for verses containing it.",
    )

    args = parser.parse_args()

    if args.find_words:
        find_words(args.db, args.find_words)
    elif args.search:
        search_verses(args.db, args.search)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
