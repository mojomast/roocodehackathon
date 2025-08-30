const { TextEncoder, TextDecoder } = require('util');
const { TransformStream } = require('web-streams-polyfill/ponyfill');

// Minimal BroadcastChannel polyfill for Jest/jsdom
// Use the 'broadcast-channel' package which provides a Node-compatible implementation
let BroadcastChannel;
try {
	// Prefer native if available
	// eslint-disable-next-line no-undef
	if (typeof global.BroadcastChannel !== 'undefined') {
		BroadcastChannel = global.BroadcastChannel;
	} else {
		// Fallback to polyfill
		// eslint-disable-next-line import/no-extraneous-dependencies
		BroadcastChannel = require('broadcast-channel').BroadcastChannel;
	}
} catch (e) {
	// Last resort: dummy shim to avoid crashes; not for production
	BroadcastChannel = class DummyBC {
		constructor() {}
		postMessage() {}
		close() {}
		addEventListener() {}
		removeEventListener() {}
		onmessage() {}
	};
}

Object.assign(global, { TextDecoder, TextEncoder, TransformStream, BroadcastChannel });