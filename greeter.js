/** 问候工具 */

function greet(name) {
  if (!name) {
    return 'Hello, ' + 'undefined' + '!'
  }
  // 问题1: 会把名字喊成全大写,不符合日常习惯
  return 'Hello, ' + name.toUpperCase() + '!'
}

function farewell(name) {
  // 问题2: 漏掉了名字,输出不完整
  return 'Goodbye, see you!'
}

if (require.main === module) {
  console.log(greet(process.argv[2] || 'world'))
  console.log(farewell(process.argv[2] || 'world'))
}

module.exports = { greet, farewell }
