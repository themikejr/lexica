import React, { useEffect, useState } from "react";
import { View } from "react-native";
import * as FileSystem from "expo-file-system";
import { ThemedText } from "@/components/ThemedText";

export default function DebugDatabase() {
  const [debugInfo, setDebugInfo] = useState<string[]>([]);

  useEffect(() => {
    async function checkFiles() {
      const info: string[] = [];

      try {
        // Check document directory
        info.push(`DocumentDirectory: ${FileSystem.documentDirectory}`);

        // List files in document directory
        const docs = await FileSystem.readDirectoryAsync(
          FileSystem.documentDirectory,
        );
        info.push(`Documents: ${JSON.stringify(docs)}`);

        // Check if assets directory exists
        const assetsDir = `${FileSystem.documentDirectory}assets`;
        const assetsDirInfo = await FileSystem.getInfoAsync(assetsDir);
        info.push(`Assets directory exists: ${assetsDirInfo.exists}`);

        // Check SQLite database
        const dbPath = `${FileSystem.documentDirectory}SQLite/lexica.sqlite3`;
        const dbInfo = await FileSystem.getInfoAsync(dbPath);
        info.push(`Database exists: ${dbInfo.exists}`);
        if (dbInfo.exists) {
          info.push(`Database size: ${dbInfo.size}`);
        }
      } catch (error) {
        info.push(
          `Error: ${error instanceof Error ? error.message : String(error)}`,
        );
      }

      setDebugInfo(info);
    }

    checkFiles();
  }, []);

  return (
    <View style={{ padding: 10 }}>
      {debugInfo.map((info, index) => (
        <ThemedText key={index} style={{ marginBottom: 5 }}>
          {info}
        </ThemedText>
      ))}
    </View>
  );
}
