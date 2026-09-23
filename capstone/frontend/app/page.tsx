'use client';

import { useEffect, useRef, useState } from 'react';
import { MapContainer, Marker, Polyline, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

type TelemetryFrame = {
  type: string;
  lat?: number;
  lon?: number;
  alt?: number;
  relative_alt?: number;
  heading?: number;
  battery_remaining?: number;
  battery?: number;
  voltage?: number;
  airspeed?: number;
  groundspeed?: number;
};

const MAX_TRAIL_POINTS = 100;
const LINK_TIMEOUT_MS = 3000;

export default function Home() {
  const [position, setPosition] = useState<[number, number] | null>(null);
  const [trail, setTrail] = useState<[number, number][]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryFrame>({ type: '' });
  const [linkUp, setLinkUp] = useState(false);
  const lastMessageAt = useRef(0);

  useEffect(() => {
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws');

    ws.onmessage = (event) => {
      const frame: TelemetryFrame = JSON.parse(event.data);
      lastMessageAt.current = Date.now();
      setLinkUp(true);

      if (frame.type === 'GLOBAL_POSITION_INT' && typeof frame.lat === 'number' && typeof frame.lon === 'number') {
        const point: [number, number] = [frame.lat, frame.lon];
        setPosition(point);
        setTrail((previous) => [...previous, point].slice(-MAX_TRAIL_POINTS));
      }

      setTelemetry((previous) => ({ ...previous, ...frame }));
    };

    ws.onclose = () => setLinkUp(false);
    ws.onerror = () => setLinkUp(false);

    const linkTimer = setInterval(() => {
      if (Date.now() - lastMessageAt.current > LINK_TIMEOUT_MS) {
        setLinkUp(false);
      }
    }, 1000);

    return () => {
      clearInterval(linkTimer);
      ws.close();
    };
  }, []);

  const center: [number, number] = position ?? [50.45, 30.52];
  const altitude = telemetry.alt ?? telemetry.relative_alt;
  const battery = telemetry.battery_remaining ?? telemetry.battery;

  return (
    <main>
      <h1>GCS Demo</h1>
      <p>
        Link: {linkUp ? 'online' : 'offline'}
        {telemetry.type ? ` · ${telemetry.type}` : ''}
      </p>
      <p>
        Position: {position ? `${position[0].toFixed(5)}, ${position[1].toFixed(5)}` : 'waiting'}
        {typeof altitude === 'number' ? ` · altitude ${altitude.toFixed(1)} m` : ''}
      </p>
      <p>
        {typeof battery === 'number' ? `Battery: ${battery}%` : 'Battery: n/a'}
        {typeof telemetry.groundspeed === 'number' ? ` · groundspeed ${telemetry.groundspeed} m/s` : ''}
      </p>
      <MapContainer center={center} zoom={13} style={{ height: '400px' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Marker position={center} />
        <Polyline positions={trail} />
      </MapContainer>
    </main>
  );
}
