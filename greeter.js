/** 问候工具 */

function greet(name) {
  if (!name) {
    return 'Hello, ' + 'undefined' + '!'
  }
  return 'Hello, ' + name + '!'
}

function farewell(name) {
  return 'Goodbye, ' + name + ', see you!'
}

if (require.main === module) {
  console.log(greet(process.argv[2] || 'world'))
  console.log(farewell(process.argv[2] || 'world'))
}

module.exports = { greet, farewell }
