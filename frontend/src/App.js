import { useEffect } from "react";
import "@/App.css";
import "leaflet/dist/leaflet.css";
import Lenis from 'lenis';
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";

// Public pages
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";

// Client pages
import ClientDashboard from "@/pages/client/ClientDashboard";
import ClientBookings from "@/pages/client/ClientBookings";
import NewBooking from "@/pages/client/NewBooking";

// Driver pages
import DriverDashboard from "@/pages/driver/DriverDashboard";

// Admin pages
import AdminDashboard from "@/pages/admin/AdminDashboard";
import AdminBookings from "@/pages/admin/AdminBookings";
import AdminDrivers from "@/pages/admin/AdminDrivers";
import AdminClients from "@/pages/admin/AdminClients";

function App() {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      direction: 'vertical',
      gestureDirection: 'vertical',
      smooth: true,
      smoothTouch: false,
      touchMultiplier: 2,
    });

    function raf(time) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, []);

  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Client routes */}
          <Route path="/client" element={<ProtectedRoute role="client"><ClientDashboard /></ProtectedRoute>} />
          <Route path="/client/bookings" element={<ProtectedRoute role="client"><ClientBookings /></ProtectedRoute>} />
          <Route path="/client/new-booking" element={<ProtectedRoute role="client"><NewBooking /></ProtectedRoute>} />
          
          {/* Driver routes */}
          <Route path="/driver" element={<ProtectedRoute role="driver"><DriverDashboard /></ProtectedRoute>} />
          
          {/* Admin routes */}
          <Route path="/admin" element={<ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/bookings" element={<ProtectedRoute role="admin"><AdminBookings /></ProtectedRoute>} />
          <Route path="/admin/drivers" element={<ProtectedRoute role="admin"><AdminDrivers /></ProtectedRoute>} />
          <Route path="/admin/clients" element={<ProtectedRoute role="admin"><AdminClients /></ProtectedRoute>} />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
