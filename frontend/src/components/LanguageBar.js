import React from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import './LanguageBar.css';

const LANGUAGES = [
  { code: 'fr', label: 'FR' },
  { code: 'en', label: 'GB' },
  { code: 'es', label: 'ES' },
];

const LanguageBar = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="language-bar">
      <div className="language-bar-spacer"></div>
      <div className="language-bar-actions">
        {LANGUAGES.map((lang) => (
          <button
            key={lang.code}
            className="lang-btn"
            title={lang.label}
            onClick={() => setLanguage(lang.code)}
            style={{
              fontWeight: 'bold',
              color: language === lang.code ? '#D4AF37' : '#A1A1AA',
            }}
          >
            {lang.label}
          </button>
        ))}
        <a href="/login" className="action-btn">Connexion</a>
        <a href="/register" className="action-btn action-btn--primary">S'inscrire</a>
      </div>
    </div>
  );
};

export default LanguageBar;
