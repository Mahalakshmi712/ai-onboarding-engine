import { useState } from "react";
import {
  BookOpen, Clock, Target, Brain, ChevronDown,
  ChevronUp, ArrowLeft, CheckCircle, Star,
  Layers, TrendingUp, Shield, ExternalLink
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import "./ResultsPage.css";

const LEVEL_LABEL = { 1: "Beginner", 2: "Intermediate", 3: "Advanced" };
const LEVEL_COLOR = { 1: "#10b981", 2: "#f59e0b", 3: "#ef4444" };

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <motion.div
      className="stat-card glass"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="stat-icon" style={{ background: `${color}22` }}>
        <Icon size={20} color={color} />
      </div>
      <div>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </motion.div>
  );
}

function ModuleCard({ module, index }) {
  const [expanded, setExpanded] = useState(false);
  const levelColor = LEVEL_COLOR[module.level] || "#6366f1";

  return (
    <motion.div
      className={`module-card glass ${module.is_target ? "is-target" : ""} ${module.is_prerequisite && !module.is_target ? "is-prereq" : ""}`}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <div className="module-header" onClick={() => setExpanded(!expanded)}>
        <div className="module-step">
          <div className="step-number">{module.step}</div>
          {index < 99 && <div className="step-line" />}
        </div>

        <div className="module-info">
          <div className="module-top-row">
            <span className="module-name">{module.name}</span>
            <div className="module-tags">
              {module.is_target && (
                <span className="tag tag-target">
                  <Star size={10} /> Target Skill
                </span>
              )}
              {module.is_prerequisite && !module.is_target && (
                <span className="tag tag-prereq">Prerequisite</span>
              )}
              <span className={`badge badge-${module.domain}`}>
                {module.domain.replace("_", " ")}
              </span>
              <span
                className="tag"
                style={{ background: `${levelColor}22`, color: levelColor }}
              >
                {LEVEL_LABEL[module.level]}
              </span>
            </div>
          </div>

          <div className="module-meta">
            <span className="meta-item">
              <Clock size={12} /> {module.estimated_hours}h
            </span>
          </div>
        </div>

        <button className="expand-btn">
          {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            className="module-body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <p className="module-description">{module.description}</p>
            {module.resources?.length > 0 && (
              <div className="module-resources">
                <p className="resources-title">📚 Recommended Resources</p>
                <ul>
                  {module.resources.map((r, i) => (
                    <li key={i}>
                      <ExternalLink size={11} /> {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function ReasoningPanel({ reasoning }) {
  const [open, setOpen] = useState(true);

  return (
    <motion.div
      className="reasoning-panel glass"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <div
        className="reasoning-header"
        onClick={() => setOpen(!open)}
      >
        <div className="reasoning-title">
          <Brain size={18} color="#a78bfa" />
          <span>AI Reasoning Trace</span>
          <span className="reasoning-badge">Why this path?</span>
        </div>
        {open ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
          >
            {/* AI Summary */}
            <div className="reasoning-summary">
              <p>{reasoning.summary}</p>
            </div>

            {/* Algorithm Trace */}
            <div className="trace-section">
              <p className="trace-title">🔍 Algorithm Trace</p>
              {reasoning.algorithm_trace?.map((line, i) => (
                <motion.div
                  key={i}
                  className="trace-line"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.08 }}
                >
                  {line}
                </motion.div>
              ))}
            </div>

            {/* Hallucination Guard */}
            <div className="guard-section">
              <Shield size={13} color="#10b981" />
              <span>
                Hallucination Guard: {" "}
                {reasoning.hallucination_guard?.resume?.removed_count === 0 &&
                 reasoning.hallucination_guard?.jd?.removed_count === 0
                  ? "✅ All skills validated against graph — zero hallucinations"
                  : `⚠️ ${reasoning.hallucination_guard?.resume?.removed_count +
                      reasoning.hallucination_guard?.jd?.removed_count} unrecognized skills removed`
                }
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function ResultsPage({ data, onReset }) {
  const { candidate, role, pathway, reasoning } = data;

  const totalModules = pathway.modules?.length || 0;
  const totalHours = pathway.total_hours || 0;
  const gapCount = pathway.gap_count || 0;
  const knownCount = pathway.known_skills_count || 0;

  return (
    <div className="results-page">

      {/* Top Nav */}
      <motion.div
        className="results-nav"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <button className="back-btn" onClick={onReset}>
          <ArrowLeft size={16} /> New Analysis
        </button>
        <div className="results-nav-title">
          🎯 Personalized Learning Pathway
        </div>
      </motion.div>

      {/* Profile Cards */}
      <motion.div
        className="profile-grid"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="glass profile-card candidate-card">
          <div className="profile-icon">👤</div>
          <div>
            <div className="profile-label">Candidate</div>
            <div className="profile-value">{candidate.summary}</div>
            <div className="profile-meta">
              {candidate.experience_level} · {candidate.primary_domain?.replace("_", " ")}
              · {knownCount} skills matched
            </div>
          </div>
        </div>

        <div className="profile-arrow">→</div>

        <div className="glass profile-card role-card">
          <div className="profile-icon">💼</div>
          <div>
            <div className="profile-label">Target Role</div>
            <div className="profile-value">{role.summary}</div>
            <div className="profile-meta">
              {role.seniority_level} · {role.primary_domain?.replace("_", " ")}
              · {role.required_skills?.length} skills required
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Row */}
      <div className="stats-row">
        <StatCard
          icon={Layers}
          label="Training Modules"
          value={totalModules}
          color="#6366f1"
        />
        <StatCard
          icon={Clock}
          label="Estimated Hours"
          value={`~${totalHours}h`}
          color="#f59e0b"
        />
        <StatCard
          icon={Target}
          label="Skill Gaps Closed"
          value={gapCount}
          color="#ef4444"
        />
        <StatCard
          icon={CheckCircle}
          label="Skills Already Known"
          value={knownCount}
          color="#10b981"
        />
        <StatCard
          icon={TrendingUp}
          label="Redundancy Eliminated"
          value={`${knownCount > 0 ? Math.round((knownCount / (knownCount + gapCount)) * 100) : 0}%`}
          color="#22d3ee"
        />
      </div>

      {/* Main Content */}
      <div className="results-main">

        {/* Pathway */}
        <div className="pathway-section">
          <h2 className="section-title">
            <BookOpen size={20} /> Your Learning Pathway
          </h2>

          {totalModules === 0 ? (
            <div className="glass no-gaps">
              <CheckCircle size={40} color="#10b981" />
              <h3>No Skill Gaps!</h3>
              <p>This candidate already meets all requirements for this role.</p>
            </div>
          ) : (
            <div className="modules-list">
              {pathway.modules.map((mod, i) => (
                <ModuleCard key={mod.id} module={mod} index={i} />
              ))}
            </div>
          )}
        </div>

        {/* Reasoning Panel */}
        <div className="reasoning-section">
          <h2 className="section-title">
            <Brain size={20} /> Reasoning & Analysis
          </h2>
          <ReasoningPanel reasoning={reasoning} />

          {/* Known Skills */}
          <div className="glass known-skills-card">
            <h3 className="known-title">
              <CheckCircle size={16} color="#10b981" /> Already Mastered
            </h3>
            <div className="known-skills-list">
              {candidate.known_skills?.length > 0 ? (
                candidate.known_skills.map((s) => (
                  <span key={s.skill_id} className="known-skill-tag">
                    ✓ {s.skill_id.replace(/_/g, " ")}
                  </span>
                ))
              ) : (
                <p className="text-muted">No matching skills detected in resume.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}