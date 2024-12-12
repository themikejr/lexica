import React, { useState } from "react";
import {
  StyleSheet,
  View,
  TextInput,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Platform,
  Pressable,
} from "react-native";
import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useDatabase } from "@/hooks/useDatabase";
import { X } from "lucide-react-native";

type Word = {
  text: string;
};

type Verse = {
  ref: string;
  text: string;
};

const SearchInput = ({
  value,
  onChangeText,
  placeholder,
}: {
  value: string;
  onChangeText: (text: string) => void;
  placeholder: string;
}) => {
  const handleClear = () => {
    onChangeText("");
  };

  return (
    <View style={styles.inputWrapper}>
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor="#666"
        autoCapitalize="none"
        clearButtonMode={Platform.OS === "ios" ? "while-editing" : "never"} // iOS native clear button
      />
      {Platform.OS === "android" && value !== "" && (
        <Pressable
          onPress={handleClear}
          style={styles.clearButton}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <X size={16} color="#666" />
        </Pressable>
      )}
    </View>
  );
};

const HighlightedText = ({
  text,
  highlightWord,
}: {
  text: string;
  highlightWord: string;
}) => {
  if (!highlightWord) return <ThemedText>{text}</ThemedText>;

  const parts = text.split(new RegExp(`(${highlightWord})`, "gi"));

  return (
    <ThemedText>
      {parts.map((part, i) =>
        part.toLowerCase() === highlightWord.toLowerCase() ? (
          <ThemedText key={i} style={styles.highlightedText}>
            {part}
          </ThemedText>
        ) : (
          <ThemedText key={i}>{part}</ThemedText>
        ),
      )}
    </ThemedText>
  );
};

const EmptyState = () => (
  <View style={styles.emptyState}>
    <ThemedText style={styles.emptyStateTitle}>
      Greek New Testament Search
    </ThemedText>
    <ThemedText style={styles.emptyStateDescription}>
      Type Greek text above to search for words and their occurrences in the New
      Testament.
    </ThemedText>
  </View>
);

export default function GreekSearch() {
  const insets = useSafeAreaInsets();
  const { error, findWords, findVerses, isReady } = useDatabase();
  const [searchTerm, setSearchTerm] = useState("");
  const [wordResults, setWordResults] = useState<Word[]>([]);
  const [verses, setVerses] = useState<Verse[]>([]);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async (text: string) => {
    setSearchTerm(text);

    // Reset everything if the input is cleared
    if (!text) {
      setWordResults([]);
      setVerses([]);
      setSelectedWord(null);
      return;
    }

    setIsLoading(true);
    try {
      const results = await findWords(text.toLowerCase());
      console.log("Word search results:", results);
      setWordResults(results);
    } catch (err) {
      console.error("Word search failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleWordSelect = async (word: string) => {
    setSelectedWord(word);
    setWordResults([]); // Clear the dropdown
    setSearchTerm(word); // Set the search input to the selected word
    setIsLoading(true);
    try {
      const results = await findVerses(word);
      console.log("Verse search results:", results);
      setVerses(results);
    } catch (err) {
      console.error("Verse search failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isReady) {
    return (
      <View style={[styles.centered, { paddingTop: insets.top }]}>
        <ActivityIndicator size="large" />
        <ThemedText>Loading database...</ThemedText>
      </View>
    );
  }

  if (error) {
    return (
      <View style={[styles.centered, { paddingTop: insets.top }]}>
        <ThemedText>Error: {error}</ThemedText>
      </View>
    );
  }

  return (
    <ThemedView style={[styles.container, { paddingTop: insets.top + 16 }]}>
      <SearchInput
        value={searchTerm}
        onChangeText={handleSearch}
        placeholder="Type Greek text..."
      />

      {isLoading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" />
        </View>
      )}

      {wordResults.length > 0 && (
        <FlatList
          data={wordResults}
          keyExtractor={(item) => item.text}
          style={styles.wordList}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.wordItem}
              onPress={() => handleWordSelect(item.text)}
            >
              <ThemedText>{item.text}</ThemedText>
            </TouchableOpacity>
          )}
        />
      )}

      {verses.length > 0 ? (
        <FlatList
          data={verses}
          keyExtractor={(item) => item.ref}
          style={styles.verseList}
          contentContainerStyle={{ paddingBottom: insets.bottom + 16 }}
          renderItem={({ item }) => (
            <View style={styles.verseItem}>
              <ThemedText style={styles.verseRef}>
                {item.ref.split("!")[0]}
              </ThemedText>
              <HighlightedText
                text={item.text}
                highlightWord={selectedWord || ""}
              />
            </View>
          )}
        />
      ) : (
        !isLoading && !wordResults.length && <EmptyState />
      )}
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  // ... existing styles ...
  container: {
    flex: 1,
    paddingHorizontal: 16,
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loadingContainer: {
    padding: 16,
    alignItems: "center",
  },
  inputWrapper: {
    position: "relative",
    marginBottom: 8,
  },
  input: {
    height: 40,
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingRight: Platform.OS === "android" ? 32 : 8, // Make room for clear button on Android
    color: "#000",
    backgroundColor: "#fff",
  },
  clearButton: {
    position: "absolute",
    right: 8,
    top: "50%",
    transform: [{ translateY: -8 }], // Half the icon size
    padding: 4,
  },
  wordList: {
    maxHeight: 200,
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    backgroundColor: "#fff",
  },
  wordItem: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  verseList: {
    flex: 1,
    marginTop: 16,
  },
  verseItem: {
    marginBottom: 16,
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 8,
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
    elevation: 2,
  },
  verseRef: {
    fontWeight: "bold",
    marginBottom: 4,
  },
  highlightedText: {
    backgroundColor: "#FFEB3B",
    color: "#000000",
  },
  // New empty state styles
  emptyState: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 32,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 12,
    textAlign: "center",
  },
  emptyStateDescription: {
    fontSize: 16,
    textAlign: "center",
    color: "#666",
  },
});
