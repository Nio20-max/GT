import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Goal Tactics",
  description: "Goal Tactics web client scaffold",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
