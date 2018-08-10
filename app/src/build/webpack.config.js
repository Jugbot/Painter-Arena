const webpack = require('webpack');
const {
  resolve
} = require('path');
const VueLoaderPlugin = require('vue-loader/lib/plugin');
var MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  mode: 'development',
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.(png|jpg|gif)$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: 8192
            }
          }
        ]
      },
      // this will apply to both plain `.js` files
      // AND `<script>` blocks in `.vue` files
      // {
      //   test: /\.js$/,
      //   loader: 'babel-loader'
      // },
      // this will apply to both plain `.css` files
      // AND `<style>` blocks in `.vue` files
      {
        test: /\.css$/,
        use: [
          // 'vue-style-loader',
          MiniCssExtractPlugin.loader,
          'css-loader'
        ]
      },
      // FA:
      {
        test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        loader: "url-loader?limit=10000&mimetype=application/font-woff&name=../fonts/[hash].[ext]"
      },
      {
        test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        loader: "file-loader?name=../fonts/[hash].[ext]"
      },
    ]
  },
  resolve: {
    extensions: ['.js', '.vue', '.json', '.png'],
    alias: {
      'vue$': 'vue/dist/vue.esm.js',
    },
    modules: [
      resolve(__dirname, '..', '../src'),
      'node_modules'
    ]
  },
  context: resolve(__dirname, '../'),
  entry: {
    app: './main.js',
    board: './drawingboard/drawingboard.js'
  },
  output: {
    filename: '[name].bundle.js',
    path: resolve(__dirname, '..', '..', './static/js'),
  },
  externals: {
    vue: 'Vue',
    jquery: 'jQuery'
  },
  optimization: {
    // splitChunks: {
    //   chunks: 'all'
    // }
  },
  plugins: [
    new VueLoaderPlugin(),
    new MiniCssExtractPlugin({
      filename: '../css/style.css'
    }),
    //new webpack.HotModuleReplacementPlugin(),
  ]
};
