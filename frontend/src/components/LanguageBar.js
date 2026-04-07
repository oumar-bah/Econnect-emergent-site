import React from 'react';
import './LanguageBar.css';

const LanguageBar = () => (
  <div className="language-bar">
    <div className="language-bar-spacer"></div>
    <div className="language-bar-actions">
      <button className="lang-btn" title="Français">🇫🇷</button>
      <button className="lang-btn" title="English">🇬🇧</button>
      <button className="lang-btn" title="Español">🇪🇸</button>
      <a href="/login" className="action-btn">Connexion</a>
      <a href="/register" className="action-btn action-btn--primary">S'inscrire</a>
    </div>
  </div>
);

export default LanguageBar;