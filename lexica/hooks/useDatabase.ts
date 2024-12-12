import { useEffect, useState } from "react";
import * as SQLite from "expo-sqlite";
import * as FileSystem from "expo-file-system";
import { Asset } from "expo-asset";
import { useSQLiteContext } from "expo-sqlite";

export function useDatabase() {
  const db = useSQLiteContext();
  // const [db, setDb] = useState<SQLite.SQLiteDatabase | null>(null);
  const [isReady, setIsReady] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const clearDatabase = async () => {
    const dbName = "lexica.sqlite3";
    const dbUri = `${FileSystem.documentDirectory}${dbName}`;

    try {
      console.log("Attempting to delete database at:", dbUri);
      const fileInfo = await FileSystem.getInfoAsync(dbUri);

      if (fileInfo.exists) {
        await FileSystem.deleteAsync(dbUri);
        console.log("Database deleted successfully");
      } else {
        console.log("No database file found to delete");
      }

      // Also clear the SQLite directory if it exists
      const sqliteDir = `${FileSystem.documentDirectory}SQLite`;
      const dirInfo = await FileSystem.getInfoAsync(sqliteDir);

      if (dirInfo.exists) {
        await FileSystem.deleteAsync(sqliteDir, { idempotent: true });
        console.log("SQLite directory cleared");
      }
    } catch (err) {
      console.error("Error clearing database:", err);
    }
  };

  const findWords = async (
    partialWord: string,
  ): Promise<Array<{ text: string }>> => {
    if (!db) {
      throw new Error("Database not ready");
    }
    console.log("Finding words for:", partialWord);

    return await db.getAllAsync<{ text: string }>(
      `SELECT DISTINCT text
       FROM "macula_greek_sblgnt"
       WHERE text_nfd LIKE ?
       LIMIT 10`,
      [`%${partialWord}%`],
    );
  };

  const findVerses = async (
    word: string,
  ): Promise<Array<{ ref: string; text: string }>> => {
    if (!db || !isReady) {
      throw new Error("Database not ready");
    }
    console.log("Finding verses for:", word);

    console.log("exec");
    return await db.getAllAsync<{ ref: string; text: string }>(
      `WITH matching_verses AS (
          SELECT DISTINCT substr(id, 1, 9) as verse_id
          FROM "macula_greek_sblgnt"
          WHERE text = ?
        )
        SELECT 
          m.ref,
          GROUP_CONCAT(m.text || COALESCE(m.after, ''), '') as text
        FROM "macula_greek_sblgnt" m
        JOIN matching_verses mv ON substr(m.id, 1, 9) = mv.verse_id
        GROUP BY substr(m.id, 1, 8)
        ORDER BY m.id`,
      [word],
    );
  };

  return {
    db,
    isReady,
    error,
    findWords,
    findVerses,
    clearDatabase,
  };
}
