//const { defineConfig } = require('@vue/cli-service')
//module.exports = defineConfig({
//  transpileDependencies: true
//})
const path = require('path');

module.exports = {
  transpileDependencies: true,
  chainWebpack: (config) => {
    config.module
      .rule('txt')
      .test(/\.txt$/i)
      .use('raw-loader')
      .loader('raw-loader')
      .end();
  },
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
  },
};
