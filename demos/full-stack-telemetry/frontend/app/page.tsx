'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function Home() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws');
    ws.onmessage = (e) => setData(JSON.parse(e.data));
    return () => ws.close();
  }, []);

  const position: [number, number] = data ? [data.lat, data.lon] : [50.45, 30.52];

  return (
    <main>
      <h1>GCS Demo</h1>
      <p>Altitude: {data?.alt} m</p>
      <p>Battery: {data?.battery}%</p>
      <MapContainer center={position} zoom={13} style={{ height: '400px' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Marker position={position} />
      </MapContainer>
    </main>
  );
}
