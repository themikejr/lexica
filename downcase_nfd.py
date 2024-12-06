import sqlite3
import unicodedata


# Function to strip diacritics and downcase text
def preprocess_text(text):
    if text is None:
        return None
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    ).lower()


# Connect to the SQLite database
db_path = "lexica.sqlite3"  # Update the path if necessary
conn = sqlite3.connect(db_path)

try:
    cursor = conn.cursor()

    # Fetch all rows that need preprocessing
    cursor.execute("SELECT id, normalized FROM 'macula-greek-SBLGNT'")
    rows = cursor.fetchall()

    # Preprocess and update the `text_nfd` column
    for row in rows:
        row_id, normalized = row
        processed_text = preprocess_text(normalized)
        cursor.execute(
            "UPDATE 'macula-greek-SBLGNT' SET text_nfd = ? WHERE id = ?",
            (processed_text, row_id),
        )

    conn.commit()
    print("Data preprocessed and `text_nfd` column updated successfully.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()
