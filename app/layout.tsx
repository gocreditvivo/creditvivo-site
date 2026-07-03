import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { StagingBanner } from "@/components/credit-vivo/StagingBanner";

export const metadata: Metadata = {
  title: "Credit Vivo",
  description: "Credit Vivo credit report review and progress portal preview.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <StagingBanner />
        {children}
      </body>
    </html>
  );
}
