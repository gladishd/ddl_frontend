const path = require('path')

module.exports = {
  outputFileTracingExcludes: {
    '**/*': [path.join(__dirname, 'public/scripts/ethernet')],
  },
}
