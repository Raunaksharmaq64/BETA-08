import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'RightFit — Dashboard & Opportunity Intelligence',
  description:
    'Sleek, minimal, high-fidelity decision engine & career intelligence platform.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-black selection:text-white">
        {children}
      </body>
    </html>
  );
}
