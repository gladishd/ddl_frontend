const path = require('path')

module.exports = {
  // drop *any* trace of public/scripts/ethernet from all server bundles
  outputFileTracingExcludes: {
    '**/*': [path.join(__dirname, 'public', 'scripts', 'ethernet')],
  },
}
