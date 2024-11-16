const { defineConfig } = require("cypress");
const webpackConfig = require('./webpack.config.js');

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      return {
        webpackConfig,
        webpackDevServer: {
          static: {
            directory: 'build',
          },
          // other Webpack dev server options
        },
      };
    },
  },
});