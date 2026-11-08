#!/usr/bin/env node
/**
 * greeter verification gate: run the project's tests and check CLI output shape.
 *
 * Exit codes: 0 = all gates pass; 1 = a gate failed; 2 = usage error.
 *
 * This is the deterministic proof script referenced in the delivery prompts:
 * a worker claims a ticket done only after this passes and the output is pasted
 * into the PR description.
 */

const { execFileSync } = require('node:child_process')
const path = require('node:path')
const fs = require('node:fs')

const root = path.resolve(__dirname, '..')

function fail(msg) {
  console.error('FAIL:', msg)
  process.exit(1)
}

console.log('[1/3] running greeter.test.js')
try {
  execFileSync('node', [path.join(root, 'greeter.test.js')], { stdio: 'inherit' })
} catch {
  fail('greeter.test.js failed')
}

console.log('[2/3] checking CLI output shape')
const out = execFileSync('node', [path.join(root, 'greeter.js'), 'Alice'], { encoding: 'utf8' })
if (!out.includes('Hello, Alice!')) fail('greet output missing "Hello, Alice!"')
if (!out.includes('Goodbye, Alice, see you!')) fail('farewell output missing "Goodbye, Alice, see you!"')

console.log('[3/3] checking module exports')
const mod = require(path.join(root, 'greeter.js'))
if (typeof mod.greet !== 'function') fail('module.exports.greet is not a function')
if (typeof mod.farewell !== 'function') fail('module.exports.farewell is not a function')
if (mod.greet('Bob') !== 'Hello, Bob!') fail('greet("Bob") mismatch')
if (mod.farewell('Bob') !== 'Goodbye, Bob, see you!') fail('farewell("Bob") mismatch')

console.log('greeter-check: all gates pass')
process.exit(0)
