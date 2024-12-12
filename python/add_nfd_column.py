import sqlite3
import unicodedata


# Function to strip diacritics (normalize to NFD)
def strip_diacritics(text):
    if text is None:
        return None
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


# Connect to the SQLite database
db_path = "lexica.sqlite3"  # Update the path if necessary
conn = sqlite3.connect(db_path)

# Register the `strip_diacritics` function for SQLite operations
conn.create_function("strip_diacritics", 1, strip_diacritics)

try:
    cursor = conn.cursor()

    # Step 1: Add a new column to the table
    cursor.execute(
        """
    ALTER TABLE "macula-greek-SBLGNT"
    ADD COLUMN text_nfd TEXT;
    """
    )
    print("Column `text_nfd` added successfully.")

    # Step 2: Populate the new column with diacritic-free values
    cursor.execute(
        """
    UPDATE "macula-greek-SBLGNT"
    SET text_nfd = strip_diacritics(normalized);
    """
    )
    conn.commit()
    print("Column `text_nfd` populated with diacritic-free values.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()
