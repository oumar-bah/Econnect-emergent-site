import { BrowserRouter } from 'react-router-dom';
import LanguageBar from './components/LanguageBar';
import Header from './components/Header';
import './components/LanguageBar.css';
import './components/Header.css';

function App() {
  return (
    <BrowserRouter>
      <LanguageBar />
      <Header />
      {/* Other components and routing logic */}
    </BrowserRouter>
  );
}

export default App;
