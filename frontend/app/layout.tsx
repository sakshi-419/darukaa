import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Darukaa.Earth — Biodiversity Intelligence',
  description: 'From environmental data to evidence-backed biodiversity action. AI Environmental Scientist.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#080f0b] text-[#e4ebe6] antialiased">
        {children}
      </body>
    </html>
  );
}
