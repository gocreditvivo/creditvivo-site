import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardLayout from './components/DashboardLayout';
import { MemberShell, FounderShell } from './components/ProcessOnlyShell';
import Home from './pages/Home';
import WhyCreditVivo from './pages/WhyCreditVivo';
import Pricing from './pages/Pricing';
import FAQ from './pages/FAQ';
import Learning from './pages/Learning';
import JoinFree from './pages/JoinFree';
import Reviews from './pages/Reviews';
import Compliance from './pages/Compliance';
import Privacy from './pages/Privacy';
import Terms from './pages/Terms';
import Disclosure from './pages/Disclosure';
import InvestorDemo from './pages/InvestorDemo';
import AutoLoanDenial from './pages/AutoLoanDenial';
import MortgageReadiness from './pages/MortgageReadiness';
import ApartmentDenial from './pages/ApartmentDenial';
import CollectionNotMine from './pages/CollectionNotMine';
import Dashboard from './pages/Dashboard';
import FreeScan from './pages/FreeScan';
import Findings from './pages/Findings';
import BankLink from './pages/BankLink';
import FounderHealth from './pages/FounderHealth';
import GrowthAI from './pages/GrowthAI';
import OwnerAICommand from './pages/OwnerAICommand';
import Status from './pages/Status';
import MemberProcessPage from './pages/MemberProcessPage';
import FounderProcessPage from './pages/FounderProcessPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public pages */}
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/why" element={<WhyCreditVivo />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/learning" element={<Learning />} />
          <Route path="/join" element={<JoinFree />} />
          <Route path="/signup" element={<JoinFree />} />
          <Route path="/reviews" element={<Reviews />} />
          <Route path="/compliance" element={<Compliance />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/disclosure" element={<Disclosure />} />
          <Route path="/investor-demo" element={<InvestorDemo />} />
          <Route path="/auto-loan-denial" element={<AutoLoanDenial />} />
          <Route path="/mortgage-readiness" element={<MortgageReadiness />} />
          <Route path="/apartment-denial" element={<ApartmentDenial />} />
          <Route path="/collection-not-mine" element={<CollectionNotMine />} />
          <Route path="/status" element={<Status />} />
        </Route>


        {/* Process-only customer test pages */}
        <Route element={<MemberShell />}>
          <Route path="/member" element={<MemberProcessPage view="dashboard" />} />
          <Route path="/member/dashboard" element={<MemberProcessPage view="dashboard" />} />
          <Route path="/member/signup" element={<MemberProcessPage view="signup" />} />
          <Route path="/member/login" element={<MemberProcessPage view="login" />} />
          <Route path="/member/upload" element={<MemberProcessPage view="upload" />} />
          <Route path="/member/findings" element={<MemberProcessPage view="findings" />} />
          <Route path="/member/negative-accounts" element={<MemberProcessPage view="negative-accounts" />} />
          <Route path="/member/bureau-comparison" element={<MemberProcessPage view="bureau-comparison" />} />
          <Route path="/member/score-blockers" element={<MemberProcessPage view="score-blockers" />} />
          <Route path="/member/comeback-plan" element={<MemberProcessPage view="comeback-plan" />} />
          <Route path="/member/disputes" element={<MemberProcessPage view="disputes" />} />
          <Route path="/member/progress" element={<MemberProcessPage view="progress" />} />
          <Route path="/member/messages" element={<MemberProcessPage view="messages" />} />
        </Route>

        {/* Process-only founder/admin test pages */}
        <Route element={<FounderShell />}>
          <Route path="/founder" element={<FounderProcessPage view="dashboard" />} />
          <Route path="/founder/dashboard" element={<FounderProcessPage view="dashboard" />} />
          <Route path="/founder/customers" element={<FounderProcessPage view="customers" />} />
          <Route path="/founder/report-intake" element={<FounderProcessPage view="report-intake" />} />
          <Route path="/founder/scanner-review" element={<FounderProcessPage view="scanner-review" />} />
          <Route path="/founder/bureau-comparison" element={<FounderProcessPage view="bureau-comparison" />} />
          <Route path="/founder/negative-tradelines" element={<FounderProcessPage view="negative-tradelines" />} />
          <Route path="/founder/letter-review" element={<FounderProcessPage view="letter-review" />} />
          <Route path="/founder/approval-logs" element={<FounderProcessPage view="approval-logs" />} />
          <Route path="/founder/compliance-blocker" element={<FounderProcessPage view="compliance-blocker" />} />
          <Route path="/founder/evidence-checklist" element={<FounderProcessPage view="evidence-checklist" />} />
          <Route path="/founder/document-vault-preview" element={<FounderProcessPage view="document-vault-preview" />} />
          <Route path="/founder/signed-url-status" element={<FounderProcessPage view="signed-url-status" />} />
          <Route path="/founder/attorney-packet-preview" element={<FounderProcessPage view="attorney-packet-preview" />} />
          <Route path="/founder/crm-preview" element={<FounderProcessPage view="crm-preview" />} />
          <Route path="/founder/audit-logs" element={<FounderProcessPage view="audit-logs" />} />
          <Route path="/founder/ai-learning-events" element={<FounderProcessPage view="ai-learning-events" />} />
          <Route path="/founder/deep-learning-preview" element={<FounderProcessPage view="deep-learning-preview" />} />
          <Route path="/founder/launch-gates" element={<FounderProcessPage view="launch-gates" />} />
          <Route path="/founder/uat-1-35-report" element={<FounderProcessPage view="uat-1-35-report" />} />
        </Route>
        {/* Member pages */}
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/login" element={<Dashboard />} />
          <Route path="/scan" element={<FreeScan />} />
          <Route path="/findings" element={<Findings />} />
          <Route path="/founder-health" element={<FounderHealth />} />
          <Route path="/owner-ai" element={<OwnerAICommand />} />
          <Route path="/growth-ai" element={<GrowthAI />} />
          <Route path="/bank-link" element={<BankLink />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
