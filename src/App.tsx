import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardLayout from './components/DashboardLayout';
import Home from './pages/Home';
import HomeAnimated from './pages/landing/HomeAnimated';
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
import AdminReview from './pages/AdminReview';
import BankLink from './pages/BankLink';
import FounderHealth from './pages/FounderHealth';
import GrowthAI from './pages/GrowthAI';
import OwnerAICommand from './pages/OwnerAICommand';
import Status from './pages/Status';
import Member from './pages/Member';
import Login from './pages/Login';
import ProtectedRoute from './auth/ProtectedRoute';
import { getAssignedVariant, type VariantId } from './config/landingPages';
import type { ComponentType } from 'react';

const homeVariants: Record<VariantId, ComponentType> = {
  classic: Home,
  animated: HomeAnimated,
  dovly: HomeAnimated,
};

function HomeRouter() {
  const variant = getAssignedVariant();
  const Component = homeVariants[variant] ?? HomeAnimated;
  return <Component />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public pages */}
        <Route element={<Layout />}>
          <Route path="/" element={<HomeRouter />} />
          {/* Direct variant access via URL */}
          <Route path="/lp/classic" element={<Home />} />
          <Route path="/lp/animated" element={<HomeAnimated />} />
          <Route path="/lp/dovly" element={<HomeAnimated />} />
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
          <Route path="/member" element={<Member />} />
          <Route path="/login" element={<Login />} />
        </Route>

        {/* Member pages */}
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/scan" element={<FreeScan />} />
            <Route path="/findings" element={<Findings />} />
            <Route path="/founder-health" element={<FounderHealth />} />
            <Route path="/owner-ai" element={<OwnerAICommand />} />
            <Route path="/growth-ai" element={<GrowthAI />} />
            <Route path="/admin-review" element={<AdminReview />} />
            <Route path="/bank-link" element={<BankLink />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
