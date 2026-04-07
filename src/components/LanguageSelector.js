import React from 'react';
import './LanguageSelector.css';

const LanguageSelector = () => {
  return (
    <div className="language-bar">
      <button title="Français">🇫🇷</button>
      <button title="English">🇬🇧</button>
      <button title="Español">🇪🇸</button>
    </div>
  );
};

export default LanguageSelector;