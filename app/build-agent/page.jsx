import BuildAgentClient from "../../components/BuildAgentClient";

export const metadata = {
  title: "Build & Compliance Copilot",
  description: "Internal, approval-controlled Credit Vivo build and compliance workspace.",
  robots: {
    index: false,
    follow: false,
  },
};

export default function BuildAgentPage() {
  return <BuildAgentClient />;
}
