const { greet, farewell } = require('./greeter')

function assert(cond, msg) { if (!cond) { console.error('FAIL:', msg); process.exit(1) } }

assert(greet('Alice') === 'Hello, Alice!', 'greet should keep the name as-is')
assert(greet('sAbRiNa') === 'Hello, sAbRiNa!', 'greet should keep mixed-case names as-is')
assert(greet('bob') === 'Hello, bob!', 'greet should keep lowercase names as-is')
assert(farewell('Alice') === 'Goodbye, Alice, see you!', 'farewell should include the name')
console.log('all tests passed')
