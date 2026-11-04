const { greet, farewell } = require('./greeter')

function assert(cond, msg) { if (!cond) { console.error('FAIL:', msg); process.exit(1) } }

assert(greet('Alice') === 'Hello, Alice!', 'greet should keep the name as-is')
assert(farewell('Alice') === 'Goodbye, Alice, see you!', 'farewell should include the name')
console.log('all tests passed')
