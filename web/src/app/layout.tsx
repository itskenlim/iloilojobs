import type { Metadata } from "next";
import { Open_Sans, Poppins } from "next/font/google";

import "./globals.css";

const display = Poppins({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-display",
});

const body = Open_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-body",
});

export const metadata: Metadata = {
  title: "Iloilo Jobs — BPO openings in one place",
  description:
    "Centralized Iloilo BPO career listings from Carelon, iQor, TELUS, and more.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${display.variable} ${body.variable}`}>{children}</body>
    </html>
  );
}
