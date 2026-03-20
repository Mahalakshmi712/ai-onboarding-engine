import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import UploadPage from "./components/UploadPage";
import ResultsPage from "./components/ResultsPage";
import "./components/UploadPage.css";
import "./components/ResultsPage.css";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">OnboardAI</span>
          <span className="logo-badge">Beta</span>
        </div>
        <div className="navbar-links">
          <span className="nav-link">Powered by Claude + Skill Graph</span>
        </div>
      </div>
    </nav>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <p>
        Built with ❤️ · Claude AI · NetworkX Skill Graph ·
        Gap-Scoring Traversal Algorithm
      </p>
    </footer>
  );
}

export default function App() {
  const [result, setResult] = useState(null);

  const handleResult = (data) => {
    setResult(data);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleReset = () => {
    setResult(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="app-shell">
      <Navbar />

      <main className="app-main">
        <AnimatePresence mode="wait">
          {!result ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.35 }}
            >
              <UploadPage onResult={handleResult} />
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.35 }}
            >
              <ResultsPage data={result} onReset={handleReset} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <Footer />
    </div>
  );
}