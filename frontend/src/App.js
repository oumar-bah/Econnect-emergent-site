import { useEffect } from "react";
import "@/App.css";
import "leaflet/dist/leaflet.css";
import Lenis from 'lenis';
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Services from "@/components/Services";
import BookingSection from "@/components/BookingSection";
import WhyChooseUs from "@/components/WhyChooseUs";
import Testimonials from "@/components/Testimonials";
import Footer from "@/components/Footer";
import WhatsAppButton from "@/components/WhatsAppButton";

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
    <div className="min-h-screen bg-[#0A0A0A]" data-testid="app-container">
      <Navbar />
      <Hero />
      <Services />
      <BookingSection />
      <WhyChooseUs />
      <Testimonials />
      <Footer />
      <WhatsAppButton />
    </div>
  );
}

export default App;
