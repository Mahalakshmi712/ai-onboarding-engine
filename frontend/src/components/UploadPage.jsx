import { useState, useRef } from "react";
import { Upload, FileText, Briefcase, ArrowRight, CheckCircle, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";

const API = "http://localhost:8000";

function FileDropZone({ label, icon: Icon, file, onFile, accept }) {
  const ref = useRef();
  const [dragging, setDragging] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  };

  return (
    <motion.div
      className={`drop-zone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => ref.current.click()}
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
    >
      <input
        ref={ref}
        type="file"
        accept={accept}
        style={{ display: "none" }}
        onChange={(e) => onFile(e.target.files[0])}
      />
      <div className="drop-zone-inner">
        {file ? (
          <>
            <CheckCircle size={32} color="#10b981" />
            <p className="drop-zone-filename">{file.name}</p>
            <span className="drop-zone-sub">Click to change file</span>
          </>
        ) : (
          <>
            <Icon size={32} color="#6366f1" />
            <p className="drop-zone-label">{label}</p>
            <span className="drop-zone-sub">PDF, DOCX, or TXT · Click or drag & drop</span>
          </>
        )}
      </div>
    </motion.div>
  );
}

export default function UploadPage({ onResult }) {
  const [resume, setResume] = useState(null);
  const [jd, setJd] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [stage, setStage] = useState("");

  const stages = [
    "📄 Extracting text from documents...",
    "🧠 AI analyzing resume skills...",
    "🎯 Parsing job requirements...",
    "🔗 Running skill graph traversal...",
    "✨ Generating reasoning trace...",
  ];

  const handleAnalyze = async () => {
    if (!resume || !jd) {
      setError("Please upload both a resume and a job description.");
      return;
    }
    setError("");
    setLoading(true);

    // Cycle through stages for UX feedback
    let i = 0;
    setStage(stages[0]);
    const interval = setInterval(() => {
      i = (i + 1) % stages.length;
      setStage(stages[i]);
    }, 1800);

    try {
      const form = new FormData();
      form.append("resume", resume);
      form.append("job_description", jd);

      const res = await axios.post(`${API}/analyze`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      clearInterval(interval);
      setLoading(false);
      onResult(res.data);
    } catch (err) {
      clearInterval(interval);
      setLoading(false);
      setError(
        err.response?.data?.detail ||
        "Something went wrong. Make sure the backend is running."
      );
    }
  };

  return (
    <div className="upload-page">
      {/* Hero Header */}
      <motion.div
        className="hero"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="hero-badge">🏆 AI-Powered Onboarding</div>
        <h1 className="hero-title">
          Your Personal<br />
          <span className="gradient-text">Learning Roadmap</span>
        </h1>
        <p className="hero-sub">
          Upload your resume and the job description. Our adaptive AI engine
          will map the exact skills you need — no fluff, no redundancy.
        </p>
      </motion.div>

      {/* Upload Cards */}
      <motion.div
        className="upload-grid"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="glass upload-card">
          <h3 className="upload-card-title">
            <FileText size={18} /> Candidate Resume
          </h3>
          <FileDropZone
            label="Drop your Resume here"
            icon={FileText}
            file={resume}
            onFile={setResume}
            accept=".pdf,.docx,.txt"
          />
        </div>

        <div className="upload-divider">
          <ArrowRight size={24} color="#6366f1" />
        </div>

        <div className="glass upload-card">
          <h3 className="upload-card-title">
            <Briefcase size={18} /> Job Description
          </h3>
          <FileDropZone
            label="Drop the Job Description here"
            icon={Briefcase}
            file={jd}
            onFile={setJd}
            accept=".pdf,.docx,.txt"
          />
        </div>
      </motion.div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            className="error-banner"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <AlertCircle size={16} /> {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Analyze Button */}
      <motion.div
        className="analyze-section"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <button
          className="btn-primary analyze-btn"
          onClick={handleAnalyze}
          disabled={loading || !resume || !jd}
        >
          {loading ? (
            <>
              <span className="spinner" /> Analyzing...
            </>
          ) : (
            <>
              <Upload size={18} /> Generate My Learning Path
            </>
          )}
        </button>

        <AnimatePresence>
          {loading && (
            <motion.p
              className="stage-text"
              key={stage}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              {stage}
            </motion.p>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}