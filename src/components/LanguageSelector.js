import React, { useState } from 'react';
import './LanguageSelector.css';

const LANGUAGES = [
  { code: 'fr', label: 'FR' },
  { code: 'en', label: 'GB' },
  { code: 'es', label: 'ES' },
];

const LanguageSelector = () => {
  const [activeLanguage, setActiveLanguage] = useState('fr');

  return (
    <div className="language-bar">
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          title={lang.label}
          onClick={() => setActiveLanguage(lang.code)}
          style={{
            fontWeight: 'bold',
            color: activeLanguage === lang.code ? '#D4AF37' : '#A1A1AA',
          }}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
};

export default LanguageSelector;
