/** 问候工具 */

function greet(name) {
  return 'Hello, ' + (name || 'world') + '!'
}

function farewell(name) {
  return 'Goodbye, ' + (name || 'world') + ', see you!'
}

if (require.main === module) {
  if (process.argv[2] === '--help') {
    console.log('用法: node greeter.js <名字>')
    process.exit(0)
  }
  console.log(greet(process.argv[2] || 'world'))
  console.log(farewell(process.argv[2] || 'world'))
}

module.exports = { greet, farewell }
