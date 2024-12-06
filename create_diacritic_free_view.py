import sqlite3
import unicodedata


# Function to strip diacritics
def strip_diacritics(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


# Connect to the SQLite database
db_path = "lexica.sqlite3"  # Update the path if necessary
conn = sqlite3.connect(db_path)

# Register the `strip_diacritics` function for use in SQL
conn.create_function("strip_diacritics", 1, strip_diacritics)

# Create the view with diacritic-free `normalized` column
create_view_sql = """
CREATE VIEW IF NOT EXISTS macula_greek_normalized AS
SELECT 
    *,
    strip_diacritics(normalized) AS normalized_no_diacritics
FROM "macula-greek-SBLGNT";
"""

# Execute the SQL to create the view
try:
    cursor = conn.cursor()
    cursor.execute(create_view_sql)
    conn.commit()
    print("View `macula_greek_normalized` created successfully.")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()
