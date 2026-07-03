import { creditVivoBrandKit } from "../../lib/market/brandKit";

export default function BrandKitPanel() {
  return <pre>{JSON.stringify(creditVivoBrandKit, null, 2)}</pre>;
}
