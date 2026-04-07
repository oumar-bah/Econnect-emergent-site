import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { List, X, CaretDown } from '@phosphor-icons/react';
import { Link } from 'react-router-dom';

const LANGUAGES = [
  { code: 'fr', flag: '🇫🇷' },
  { code: 'en', flag: '🇬🇧' },
  { code: 'es', flag: '🇪🇸' },
];

const GAMME_ITEMS = [
  'Comfort Classique',
  'Comfort Premium',
  'Prestige',
  'Van',
];

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isGammeOpen, setIsGammeOpen] = useState(false);
  const [activeLang, setActiveLang] = useState('fr');

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Accueil', href: '#accueil' },
    { name: 'Services', href: '#services' },
    { name: 'À propos', href: '#apropos' },
    { name: 'Contact', href: '#contact' },
  ];

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? 'glass' : 'bg-transparent'
      }`}
      data-testid="navbar"
    >
      <nav className="max-w-7xl mx-auto px-6 md:px-12 py-4 flex items-center justify-between">
        {/* Logo */}
        <a href="#accueil" className="flex items-center gap-2" data-testid="logo">
          <span className="text-2xl md:text-3xl font-bold font-['Cormorant_Garamond'] gold-text">
            Econnect VTC
          </span>
        </a>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              className="text-[#A1A1AA] hover:text-[#D4AF37] transition-colors duration-300 text-sm tracking-wide uppercase"
              data-testid={`nav-link-${link.name.toLowerCase()}`}
            >
              {link.name}
            </a>
          ))}

          {/* Gamme dropdown */}
          <div
            className="relative"
            onMouseEnter={() => setIsGammeOpen(true)}
            onMouseLeave={() => setIsGammeOpen(false)}
          >
            <button
              className="flex items-center gap-1 text-[#A1A1AA] hover:text-[#D4AF37] transition-colors duration-300 text-sm tracking-wide uppercase"
              data-testid="nav-link-gamme"
            >
              Gamme <CaretDown size={14} className={`transition-transform duration-200 ${isGammeOpen ? 'rotate-180' : ''}`} />
            </button>

            <AnimatePresence>
              {isGammeOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.18 }}
                  className="absolute top-full left-0 mt-2 w-48 rounded-lg overflow-hidden shadow-xl"
                  style={{ background: '#181818', border: '1px solid rgba(212,175,55,0.15)' }}
                >
                  {GAMME_ITEMS.map((item) => (
                    <a
                      key={item}
                      href="#gammes"
                      className="block px-4 py-3 text-sm transition-colors duration-200 hover:bg-[#232323]"
                      style={{ color: '#C7B588' }}
                      onClick={() => setIsGammeOpen(false)}
                    >
                      {item}
                    </a>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Right-side actions (desktop) */}
        <div className="hidden md:flex items-center gap-3">
          {/* Language flags */}
          <div className="flex items-center gap-1 mr-2">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => setActiveLang(lang.code)}
                className="text-2xl leading-none p-1 rounded transition-opacity duration-200"
                style={{ opacity: activeLang === lang.code ? 1 : 0.5, background: 'none', border: 'none', cursor: 'pointer', fontFamily: "'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif" }}
                title={lang.code.toUpperCase()}
                data-testid={`lang-${lang.code}`}
              >
                {lang.flag}
              </button>
            ))}
          </div>

          {/* Réserver button */}
          <a
            href="#reserver"
            className="font-semibold px-5 py-2 rounded-lg transition-all duration-300 hover:scale-105 text-sm"
            style={{ background: '#D4AF37', color: '#0A0A0A' }}
            data-testid="cta-reserver"
          >
            Réserver
          </a>

          {/* Connexion button */}
          <Link
            to="/login"
            className="font-semibold px-5 py-2 rounded-lg transition-all duration-300 text-sm"
            style={{
              background: 'transparent',
              border: '1.5px solid #D4AF37',
              color: '#D4AF37',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = '#D4AF37'; e.currentTarget.style.color = '#232323'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#D4AF37'; }}
            data-testid="btn-connexion"
          >
            Connexion
          </Link>

          {/* S'inscrire button */}
          <Link
            to="/register"
            className="font-semibold px-5 py-2 rounded-lg transition-all duration-300 text-sm"
            style={{ background: '#D4AF37', color: '#232323' }}
            onMouseEnter={e => { e.currentTarget.style.background = '#F0C74A'; }}
            onMouseLeave={e => { e.currentTarget.style.background = '#D4AF37'; }}
            data-testid="btn-sinscrire"
          >
            S'inscrire
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden text-[#FAFAFA] hover:text-[#D4AF37] transition-colors"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          data-testid="mobile-menu-toggle"
        >
          {isMobileMenuOpen ? <X size={28} /> : <List size={28} />}
        </button>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="md:hidden glass border-t border-white/10"
            data-testid="mobile-menu"
          >
            <div className="px-6 py-6 flex flex-col gap-4">
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  className="text-[#A1A1AA] hover:text-[#D4AF37] transition-colors py-2 text-lg"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {link.name}
                </a>
              ))}

              {/* Gamme sub-items in mobile */}
              <div>
                <p className="text-[#A1A1AA] text-sm uppercase tracking-wide py-1">Gamme</p>
                <div className="pl-4 flex flex-col gap-2 mt-1">
                  {GAMME_ITEMS.map((item) => (
                    <a
                      key={item}
                      href="#gammes"
                      className="py-1 text-base transition-colors duration-200"
                      style={{ color: '#C7B588' }}
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      {item}
                    </a>
                  ))}
                </div>
              </div>

              {/* Language flags */}
              <div className="flex items-center gap-3 py-2">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => setActiveLang(lang.code)}
                    className="text-2xl"
                    style={{ opacity: activeLang === lang.code ? 1 : 0.5, background: 'none', border: 'none', cursor: 'pointer', fontFamily: "'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif" }}
                  >
                    {lang.flag}
                  </button>
                ))}
              </div>

              {/* Réserver button */}
              <a
                href="#reserver"
                className="font-semibold w-full text-center py-3 rounded-lg transition-all duration-300 mt-2"
                style={{ background: '#D4AF37', color: '#0A0A0A' }}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Réserver
              </a>

              {/* Connexion */}
              <Link
                to="/login"
                className="font-semibold w-full text-center py-3 rounded-lg transition-all duration-300"
                style={{ border: '1.5px solid #D4AF37', color: '#D4AF37', background: 'transparent' }}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Connexion
              </Link>

              {/* S'inscrire */}
              <Link
                to="/register"
                className="font-semibold w-full text-center py-3 rounded-lg transition-all duration-300"
                style={{ background: '#D4AF37', color: '#232323' }}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                S'inscrire
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
};

export default Navbar;
