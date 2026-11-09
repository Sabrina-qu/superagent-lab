/** 问候工具 */

function greet(name) {
  // 空/缺名与 CLI 缺参行为一致：回落 world
  return 'Hello, ' + (name || 'world') + '!'
}

function farewell(name) {
  // 空/缺名与 CLI 缺参行为一致：回落 world
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
