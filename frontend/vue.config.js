/* eslint-disable unicorn/prefer-module */
const BundleTracker = require("webpack-bundle-tracker");
const path = require("path");

const DEV = process.env.NODE_ENV === "development";
process.env.VUE_APP_PACKAGE_VERSION = require("./package.json").version;

module.exports = {
  productionSourceMap: DEV,
  configureWebpack: {
    plugins: [new BundleTracker()],
    entry: {
      browserChoices: "./src/choices/browserChoices.json",
      readerChoices: "./src/choices/readerChoices.json",
      websocketMessages: "./src/choices/websocketMessages.json",
    },
    devServer: {
      writeToDisk: true, // Write files to disk in dev mode, so Django can serve the assets
    },
  },
  transpileDependencies: ["vuetify"],
  publicPath: "static/",
  filenameHashing: false, // Let Django do it
  outputDir: path.resolve(__dirname, "../codex/static_build"),
};
/* eslint-enable unicorn/prefer-module */
