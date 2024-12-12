const { getDefaultConfig } = require("expo/metro-config");

const defaultConfig = getDefaultConfig(__dirname);

module.exports = {
  ...defaultConfig,
  resolver: {
    ...defaultConfig.resolver,
    assetExts: [...defaultConfig.resolver.assetExts, "db", "sqlite", "sqlite3"],
    sourceExts: [
      ...defaultConfig.resolver.sourceExts,
      "db",
      "sqlite",
      "sqlite3",
    ],
  },
};
