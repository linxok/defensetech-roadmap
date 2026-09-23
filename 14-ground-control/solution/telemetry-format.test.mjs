import test from 'node:test';
import assert from 'node:assert/strict';

import { appendTrail, formatTelemetry, isValidTelemetry } from './telemetry-format.mjs';

const VALID = { drone_id: 'd1', lat: 50.45, lon: 30.52, alt: 120.4, battery: 87 };

test('accepts a valid telemetry frame', () => {
  assert.equal(isValidTelemetry(VALID), true);
});

test('rejects out-of-range battery and coordinates', () => {
  assert.equal(isValidTelemetry({ ...VALID, battery: 150 }), false);
  assert.equal(isValidTelemetry({ ...VALID, lat: 100 }), false);
  assert.equal(isValidTelemetry(null), false);
  assert.equal(isValidTelemetry({ lat: 'x' }), false);
});

test('formats telemetry for the UI', () => {
  const view = formatTelemetry(VALID);
  assert.deepEqual(view.position, [50.45, 30.52]);
  assert.equal(view.altitude, '120.4 m');
  assert.equal(view.battery, '87%');
});

test('caps the trail length', () => {
  let trail = [];
  for (let i = 0; i < 150; i += 1) {
    trail = appendTrail(trail, [i, i], 100);
  }
  assert.equal(trail.length, 100);
  assert.deepEqual(trail[0], [50, 50]);
});
