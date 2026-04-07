import React, { useState } from 'react';

const LanguageSelector = () => {
    const [language, setLanguage] = useState('');

    const handleLanguageChange = (lang) => {
        setLanguage(lang);
        // You can add more logic here to handle the language change
    };

    return (
        <div>
            <button onClick={() => handleLanguageChange('fr')}>🇫🇷 French</button>
            <button onClick={() => handleLanguageChange('en')}>🇬🇧 English</button>
            <button onClick={() => handleLanguageChange('es')}>🇪🇸 Spanish</button>
        </div>
    );
};

export default LanguageSelector;