const webpack = require('webpack');
const {
  resolve
} = require('path');
const VueLoaderPlugin = require('vue-loader/lib/plugin');

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
          'vue-style-loader',
          'css-loader'
        ]
      }
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
  },
  output: {
    filename: '[name].bundle.js',
    path: resolve(__dirname, '..', '..', './static/js'),
  },
  plugins: [
    new VueLoaderPlugin(),
    new webpack.HotModuleReplacementPlugin(),
  ]
};
