const { greet, farewell } = require('./greeter')
const { execFileSync } = require('node:child_process')
const path = require('node:path')

function assert(cond, msg) { if (!cond) { console.error('FAIL:', msg); process.exit(1) } }

assert(greet('Alice') === 'Hello, Alice!', 'greet should keep the name as-is')
assert(greet('sAbRiNa') === 'Hello, sAbRiNa!', 'greet should keep mixed-case names as-is')
assert(greet('bob') === 'Hello, bob!', 'greet should keep lowercase names as-is')
assert(farewell('Alice') === 'Goodbye, Alice, see you!', 'farewell should include the name')

// 空名/缺名边界：模块调用与 CLI 缺参一致，回落 world（issue #33）
assert(greet('') === 'Hello, world!', 'greet should fall back to world for empty name')
assert(greet(undefined) === 'Hello, world!', 'greet should fall back to world for missing name')
assert(farewell('') === 'Goodbye, world, see you!', 'farewell should fall back to world for empty name')
assert(farewell(undefined) === 'Goodbye, world, see you!', 'farewell should fall back to world for missing name')

// --help 分支：打印用法行并 exit 0（execFileSync 在非零退出码时会抛错）
const cli = path.join(__dirname, 'greeter.js')
const helpOut = execFileSync('node', [cli, '--help'], { encoding: 'utf8' })
assert(helpOut === '用法: node greeter.js <名字>\n', '--help should print the usage line')

// 裸跑保持兼容：无参数时仍按默认名 world 输出
const bareOut = execFileSync('node', [cli], { encoding: 'utf8' })
assert(bareOut.includes('Hello, world!'), 'bare run should greet the default name world')
assert(bareOut.includes('Goodbye, world, see you!'), 'bare run should farewell the default name world')

console.log('all tests passed')
