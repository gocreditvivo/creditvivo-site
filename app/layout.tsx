import AnalyticsScripts from '../components/AnalyticsScripts'
import ComplianceFooter from '../components/ComplianceFooter'
import './globals.css'

export const metadata = {
  title: {
    default: 'CreditVivo | Credit improvement you can track',
    template: '%s | CreditVivo',
  },
  description: 'Review possible credit-report inaccuracies, organize evidence, prepare dispute support, and track responses in one secure portal.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <ComplianceFooter />
        <AnalyticsScripts />
      </body>
    </html>
  )
}

