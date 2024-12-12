// import DebugDatabase from "@/components/DebugDatabase";
// import { ThemedView } from "@/components/ThemedView";

// export default function ExploreScreen() {
//   return (
//     <ThemedView style={{ flex: 1 }}>
//       <DebugDatabase />
//     </ThemedView>
//   );
// }

import GreekSearch from "@/components/GreekSearch";
import { ThemedView } from "@/components/ThemedView";
// import { useDatabase } from "@/hooks/useDatabase";
import { useSQLiteContext } from "expo-sqlite";
import {
  StyleSheet,
  View,
  TextInput,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  Button, // Add this import
} from "react-native";

export default function ExploreScreen() {
  return (
    <ThemedView style={{ flex: 1 }}>
      <GreekSearch />
    </ThemedView>
  );
}
