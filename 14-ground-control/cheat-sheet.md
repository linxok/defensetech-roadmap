# Cheat Sheet 14: Наземна станція (GCS)

- `new WebSocket(process.env.NEXT_PUBLIC_WS_URL)`
- `useEffect(() => { ...; return () => ws.close(); }, [])`
- `<MapContainer center={[lat, lon]} zoom={13}>`
- `appendTrail(trail, point, 100)` — ring buffer
- `node --test telemetry-format.test.mjs`
