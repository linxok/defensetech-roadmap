'use client';

import { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import { appendTrail, formatTelemetry, isValidTelemetry } from './telemetry-format.mjs';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8000/ws';

interface Telemetry {
  drone_id?: string;
  lat: number;
  lon: number;
  alt: number;
  battery: number;
}

export default function GCSPage() {
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);
  const [trail, setTrail] = useState<[number, number][]>([]);
  const [status, setStatus] = useState('connecting');

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    ws.onopen = () => setStatus('live');
    ws.onclose = () => setStatus('disconnected');
    ws.onmessage = (event) => {
      let payload: unknown;
      try {
        payload = JSON.parse(event.data);
      } catch {
        setStatus('bad-json');
        return;
      }
      if (!isValidTelemetry(payload)) {
        return;
      }
      const frame = payload as Telemetry;
      setTelemetry(frame);
      setTrail((current) => appendTrail(current, [frame.lat, frame.lon]));
    };
    return () => ws.close();
  }, []);

  const view = useMemo(() => (telemetry ? formatTelemetry(telemetry) : null), [telemetry]);
  const position: [number, number] = view ? view.position : [50.45, 30.52];

  return (
    <main style={{ padding: 16 }}>
      <h1>Ground Control Station</h1>
      <p>Status: {status}</p>
      {view && (
        <div>
          <p>Drone: {view.droneId}</p>
          <p>Altitude: {view.altitude}</p>
          <p>Battery: {view.battery}</p>
        </div>
      )}
      <MapContainer center={position} zoom={13} style={{ height: '500px' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Marker position={position}>
          <Popup>Drone position</Popup>
        </Marker>
        {trail.length > 1 && <Polyline positions={trail} />}
      </MapContainer>
    </main>
  );
}
