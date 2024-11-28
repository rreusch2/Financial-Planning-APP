const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const Dotenv = require("dotenv-webpack"); // Add dotenv-webpack

module.exports = {
  mode: "development",
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "bundle.js",
    publicPath: "/",
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader", "postcss-loader"],
      },
    ],
  },
  resolve: {
    extensions: [".js", ".jsx"],
  },
  devServer: {
    port: 3000,
    static: {
      directory: path.join(__dirname, "public"),
    },
    historyApiFallback: {
      rewrites: [
        { from: /^\/api\/.*$/, to: (context) => context.parsedUrl.path },
        { from: /./, to: "/index.html" },
      ],
    },
    hot: true,
    proxy: [
      {
        context: ["/api"],
        target: "http://localhost:5028",
        secure: false,
        changeOrigin: true,
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: "./public/index.html",
    }),
    new Dotenv({
      // Add dotenv-webpack plugin here
      path: "./.env", // Specify the path to your .env file
      safe: true, // Ensures all variables are defined
    }),
  ],
};
