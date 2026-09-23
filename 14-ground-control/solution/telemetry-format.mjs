// Чисті функції GCS: валідація кадру, форматування, траєкторія.
// Тестуються без React і браузера: node --test telemetry-format.test.mjs

export function isValidTelemetry(payload) {
  if (payload === null || typeof payload !== 'object') {
    return false;
  }
  const { lat, lon, alt, battery } = payload;
  return (
    Number.isFinite(lat) && lat >= -90 && lat <= 90 &&
    Number.isFinite(lon) && lon >= -180 && lon <= 180 &&
    Number.isFinite(alt) && alt >= -500 &&
    Number.isFinite(battery) && battery >= 0 && battery <= 100
  );
}

export function formatTelemetry(payload) {
  return {
    position: [payload.lat, payload.lon],
    altitude: `${payload.alt.toFixed(1)} m`,
    battery: `${Math.round(payload.battery)}%`,
    droneId: payload.drone_id ?? 'unknown',
  };
}

export function appendTrail(trail, point, maxPoints = 100) {
  const next = [...trail, point];
  return next.length > maxPoints ? next.slice(next.length - maxPoints) : next;
}
