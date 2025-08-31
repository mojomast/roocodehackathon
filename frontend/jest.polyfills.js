const { TextEncoder, TextDecoder } = require('util');

Object.assign(global, { TextDecoder, TextEncoder });
const { TransformStream } = require('node:stream/web');
Object.assign(global, { TransformStream });
const { BroadcastChannel } = require('node:worker_threads');
Object.assign(global, { BroadcastChannel });