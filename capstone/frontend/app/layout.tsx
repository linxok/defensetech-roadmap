import type { Metadata } from 'next';
import 'leaflet/dist/leaflet.css';

export const metadata: Metadata = {
  title: 'Capstone GCS',
  description: 'Live drone telemetry dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uk">
      <body style={{ margin: 0, fontFamily: 'system-ui, sans-serif' }}>{children}</body>
    </html>
  );
}
