import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Goal Tactics",
  description: "Football manager game – build your club, dominate the league.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-gt-bg text-gt-text">
        {children}
      </body>
    </html>
  );
}
