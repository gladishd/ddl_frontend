const path = require('path');

module.exports = {
  experimental: {
    outputFileTracingExcludes: {
      '**/*': [path.join(__dirname, 'public/scripts/ethernet')]
    },
  },
};
