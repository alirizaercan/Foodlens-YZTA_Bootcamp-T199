const { override, addWebpackModuleRule } = require('customize-cra');

module.exports = override(
  // Fix for webpack dev server allowedHosts issue
  (config) => {
    if (config.devServer) {
      config.devServer.allowedHosts = 'all';
    }
    return config;
  }
);
