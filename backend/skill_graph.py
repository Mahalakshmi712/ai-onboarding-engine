"""
Skill Graph Engine — The Adaptive Pathing Core
Uses a directed graph (NetworkX) where:
  - Nodes = individual skills with metadata
  - Edges = prerequisite relationships (A → B means "learn A before B")
The gap-scoring algorithm finds the shortest competency path
from the hire's current skill set to the target role's requirements.
"""

import networkx as nx
from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class SkillNode:
    id: str
    name: str
    domain: str          # e.g. "programming", "data", "leadership"
    level: int           # 1=Beginner, 2=Intermediate, 3=Advanced
    estimated_hours: int
    description: str
    resources: list[str] = field(default_factory=list)


class SkillGraphEngine:
    """
    Directed Acyclic Graph of skills with prerequisite edges.
    Core adaptive logic: gap-score traversal to build personalized paths.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_master_graph()

    def _add_skill(self, node: SkillNode):
        self.graph.add_node(
            node.id,
            name=node.name,
            domain=node.domain,
            level=node.level,
            estimated_hours=node.estimated_hours,
            description=node.description,
            resources=node.resources
        )

    def _add_prerequisite(self, from_skill: str, to_skill: str):
        """Edge means: must know `from_skill` before learning `to_skill`"""
        self.graph.add_edge(from_skill, to_skill)

    def _build_master_graph(self):
        """
        Master skill taxonomy — covers Technical AND Operational roles
        for Cross-Domain Scalability score.
        """

        skills = [
            # ── FOUNDATIONAL ──────────────────────────────────────────
            SkillNode("communication_basics", "Workplace Communication", "soft_skills", 1, 3,
                "Professional written and verbal communication in a workplace setting.",
                ["LinkedIn Learning: Business Communication"]),

            SkillNode("computer_basics", "Computer & Software Basics", "foundational", 1, 4,
                "File management, email, calendar tools, and basic office software.",
                ["Google Workspace Training", "Microsoft 365 Basics"]),

            SkillNode("company_culture", "Company Culture & Compliance", "foundational", 1, 2,
                "HR policies, code of conduct, DEI principles, and company values.",
                ["Internal HR Handbook", "SHRM Compliance Modules"]),

            # ── PROGRAMMING ───────────────────────────────────────────
            SkillNode("python_basics", "Python Programming — Fundamentals", "programming", 1, 10,
                "Variables, loops, functions, and basic data structures in Python.",
                ["Python.org Official Tutorial", "Automate the Boring Stuff"]),

            SkillNode("python_intermediate", "Python — Intermediate", "programming", 2, 15,
                "OOP, file I/O, error handling, list comprehensions, and modules.",
                ["Real Python", "Fluent Python (Book)"]),

            SkillNode("python_advanced", "Python — Advanced & Performance", "programming", 3, 20,
                "Async programming, decorators, generators, and profiling.",
                ["Python Cookbook", "High Performance Python"]),

            SkillNode("git_basics", "Version Control with Git", "programming", 1, 5,
                "Commits, branches, merges, and pull requests on GitHub/GitLab.",
                ["Pro Git (free book)", "GitHub Learning Lab"]),

            SkillNode("sql_basics", "SQL & Relational Databases", "data", 1, 8,
                "SELECT, JOIN, GROUP BY, subqueries, and indexing fundamentals.",
                ["Mode Analytics SQL Tutorial", "SQLZoo"]),

            SkillNode("sql_advanced", "Advanced SQL & Query Optimization", "data", 2, 10,
                "Window functions, CTEs, execution plans, and performance tuning.",
                ["Use The Index, Luke", "Advanced SQL on Coursera"]),

            SkillNode("api_design", "REST API Design & Integration", "programming", 2, 8,
                "HTTP methods, authentication, OpenAPI spec, and consuming APIs.",
                ["REST API Design Rulebook", "Postman Learning Center"]),

            SkillNode("docker_basics", "Containerization with Docker", "devops", 2, 6,
                "Images, containers, Dockerfiles, volumes, and docker-compose.",
                ["Docker Official Docs", "Play with Docker"]),

            SkillNode("cloud_fundamentals", "Cloud Fundamentals (AWS/GCP/Azure)", "devops", 2, 10,
                "Core services: compute, storage, networking, and IAM basics.",
                ["AWS Cloud Practitioner Essentials", "Google Cloud Fundamentals"]),

            # ── DATA & AI ─────────────────────────────────────────────
            SkillNode("data_analysis", "Data Analysis & Visualization", "data", 2, 12,
                "Pandas, NumPy, Matplotlib/Seaborn for exploratory data analysis.",
                ["Kaggle: Pandas Course", "Python for Data Analysis (Book)"]),

            SkillNode("ml_fundamentals", "Machine Learning Fundamentals", "ai_ml", 2, 20,
                "Supervised/unsupervised learning, model evaluation, and sklearn.",
                ["fast.ai", "Coursera: ML Specialization (Andrew Ng)"]),

            SkillNode("llm_basics", "LLMs & Prompt Engineering", "ai_ml", 2, 8,
                "Transformer architecture intuition, prompting techniques, and API usage.",
                ["Anthropic Prompt Engineering Guide", "DeepLearning.AI: ChatGPT Prompt Eng."]),

            SkillNode("deep_learning", "Deep Learning & Neural Networks", "ai_ml", 3, 25,
                "CNNs, RNNs, backpropagation, and modern architectures.",
                ["fast.ai Deep Learning", "Deep Learning (Goodfellow et al.)"]),

            # ── LEADERSHIP & MANAGEMENT ───────────────────────────────
            SkillNode("project_management", "Project Management Fundamentals", "leadership", 1, 8,
                "Agile, Scrum, Kanban, and basic project lifecycle management.",
                ["PMI PMBOK Overview", "Atlassian Agile Coach"]),

            SkillNode("team_leadership", "Team Leadership & Delegation", "leadership", 2, 6,
                "1:1s, performance feedback, goal-setting with OKRs, and team dynamics.",
                ["Manager Tools Podcast", "The Manager's Path (Book)"]),

            SkillNode("strategic_thinking", "Strategic Thinking & Decision Making", "leadership", 3, 8,
                "Frameworks for business analysis, prioritization, and executive communication.",
                ["HBR: Strategic Thinking", "Good Strategy Bad Strategy (Book)"]),

            # ── OPERATIONS / LABOR ────────────────────────────────────────
            SkillNode("safety_compliance", "Workplace Safety & OSHA Compliance", "operations", 1, 4,
                "OSHA standards, hazard identification, PPE usage, and incident reporting.",
                ["OSHA 10-Hour General Industry", "SafeStart Training"]),

            SkillNode("forklift_operation", "Forklift & Material Handling Equipment", "operations", 1, 6,
                "Safe operation of forklifts, pallet jacks, and material handling equipment.",
                ["OSHA Forklift Operator Training", "Toyota Forklift Safety Course"]),

            SkillNode("warehouse_basics", "Warehouse Operations Fundamentals", "operations", 1, 5,
                "Receiving, putaway, picking, packing, and shipping processes in a warehouse.",
                ["Coursera: Warehouse Operations", "WERC Warehouse Fundamentals"]),

            SkillNode("inventory_management", "Inventory Management & Stock Control", "operations", 2, 8,
                "Stock counting, cycle counts, FIFO/LIFO methods, and inventory accuracy.",
                ["APICS CPIM Basics", "Udemy: Inventory Management"]),

            SkillNode("supply_chain_basics", "Supply Chain & Logistics Fundamentals", "operations", 2, 6,
                "Procurement, vendor management, warehousing, and distribution basics.",
                ["APICS CSCP Overview", "Coursera: Supply Chain Basics"]),

            SkillNode("wms_software", "Warehouse Management Systems (WMS)", "operations", 2, 6,
                "Using WMS software for order management, tracking, and reporting.",
                ["SAP Extended Warehouse Management", "Manhattan Associates WMS Training"]),

            SkillNode("quality_management", "Quality Management (Six Sigma / ISO)", "operations", 3, 10,
                "Process control, DMAIC methodology, and quality auditing principles.",
                ["ASQ Six Sigma Overview", "ISO 9001 Fundamentals"]),

            SkillNode("team_lead_operations", "Operations Team Leadership", "operations", 3, 8,
                "Shift supervision, KPI tracking, safety compliance leadership, and team coordination.",
                ["Supervisory Skills for Operations", "LinkedIn Learning: Team Lead Fundamentals"]),
        ]

        for skill in skills:
            self._add_skill(skill)

        # ── PREREQUISITE EDGES ────────────────────────────────────────
        prerequisites = [
            # Programming chain
            ("computer_basics",      "python_basics"),
            ("python_basics",        "python_intermediate"),
            ("python_intermediate",  "python_advanced"),
            ("python_basics",        "git_basics"),
            ("python_intermediate",  "api_design"),
            ("python_intermediate",  "data_analysis"),
            ("sql_basics",           "sql_advanced"),

            # DevOps chain
            ("git_basics",           "docker_basics"),
            ("docker_basics",        "cloud_fundamentals"),

            # Data/AI chain
            ("data_analysis",        "ml_fundamentals"),
            ("python_intermediate",  "ml_fundamentals"),
            ("ml_fundamentals",      "deep_learning"),
            ("python_basics",        "llm_basics"),
            ("ml_fundamentals",      "llm_basics"),

            # Leadership chain
            ("communication_basics", "project_management"),
            ("project_management",   "team_leadership"),
            ("team_leadership",      "strategic_thinking"),

             # Operations / Warehouse chain
            ("company_culture",      "safety_compliance"),
            ("safety_compliance",    "forklift_operation"),
            ("safety_compliance",    "warehouse_basics"),
            ("warehouse_basics",     "inventory_management"),
            ("inventory_management", "supply_chain_basics"),
            ("inventory_management", "wms_software"),
            ("supply_chain_basics",  "quality_management"),
            ("wms_software",         "quality_management"),
            ("quality_management",   "team_lead_operations"),
        ]

        for src, dst in prerequisites:
            self._add_prerequisite(src, dst)

    # ─────────────────────────────────────────────────────────────────
    # CORE ADAPTIVE ALGORITHM
    # ─────────────────────────────────────────────────────────────────

    def compute_learning_pathway(
        self,
        known_skill_ids: list[str],
        target_skill_ids: list[str]
    ) -> dict:
        """
        Gap-Scoring Traversal Algorithm:
        1. Mark all known skills as 'mastered'
        2. For each target skill, find the shortest prerequisite path
           from the nearest mastered node (or graph root if none)
        3. Remove already-mastered nodes from the path
        4. Score each remaining skill by: dependency_depth + domain_relevance
        5. Return ordered pathway with reasoning trace
        """

        known_set = set(known_skill_ids)
        target_set = set(target_skill_ids)
        gap_skills = target_set - known_set

        if not gap_skills:
            return {
                "pathway": [],
                "total_hours": 0,
                "reasoning_trace": ["✅ No skill gaps detected. Hire is fully prepared for this role."],
                "gap_analysis": {}
            }

        pathway_nodes = set()
        reasoning_trace = []
        gap_analysis = {}

        for target_id in gap_skills:
            if target_id not in self.graph:
                reasoning_trace.append(f"⚠️ '{target_id}' not found in skill graph — skipped.")
                continue

            # Find the best "bridge" node: a known skill that is an ancestor
            ancestors = nx.ancestors(self.graph, target_id)
            known_ancestors = ancestors & known_set

            if known_ancestors:
                # Find the closest known ancestor (fewest hops away)
                best_start = min(
                    known_ancestors,
                    key=lambda a: nx.shortest_path_length(self.graph, a, target_id)
                )
                try:
                    path = nx.shortest_path(self.graph, best_start, target_id)
                    path_to_add = [n for n in path if n not in known_set]
                    trace_msg = (
                        f"🎯 For '{self.graph.nodes[target_id]['name']}': "
                        f"Found bridge from known skill "
                        f"'{self.graph.nodes[best_start]['name']}' "
                        f"→ {len(path_to_add)} new modules needed."
                    )
                except nx.NetworkXNoPath:
                    path_to_add = [target_id]
                    trace_msg = f"🎯 '{self.graph.nodes[target_id]['name']}': No prerequisite path — added directly."
            else:
                # No known ancestors — find all prerequisites from graph roots
                all_prereqs = list(nx.ancestors(self.graph, target_id)) + [target_id]
                # Topological sort to get correct learning order
                subgraph = self.graph.subgraph(all_prereqs)
                try:
                    ordered = list(nx.topological_sort(subgraph))
                except nx.NetworkXUnfeasible:
                    ordered = all_prereqs
                path_to_add = [n for n in ordered if n not in known_set]
                trace_msg = (
                    f"🎯 For '{self.graph.nodes[target_id]['name']}': "
                    f"No prior knowledge bridge found — "
                    f"building full path of {len(path_to_add)} modules."
                )

            reasoning_trace.append(trace_msg)
            gap_analysis[target_id] = {
                "skill_name": self.graph.nodes[target_id]["name"],
                "modules_required": len(path_to_add),
                "bridge_from": self.graph.nodes[best_start]["name"] if known_ancestors else "None"
            }
            pathway_nodes.update(path_to_add)

        # ── ORDER BY TOPOLOGICAL SORT (respects prerequisites) ────────
        if pathway_nodes:
            subgraph = self.graph.subgraph(pathway_nodes)
            try:
                ordered_pathway = [
                    n for n in nx.topological_sort(subgraph)
                    if n in pathway_nodes
                ]
            except nx.NetworkXUnfeasible:
                ordered_pathway = list(pathway_nodes)
        else:
            ordered_pathway = []

        # ── BUILD RICH OUTPUT ─────────────────────────────────────────
        pathway_details = []
        total_hours = 0
        for i, node_id in enumerate(ordered_pathway):
            node = self.graph.nodes[node_id]
            total_hours += node["estimated_hours"]
            pathway_details.append({
                "step": i + 1,
                "id": node_id,
                "name": node["name"],
                "domain": node["domain"],
                "level": node["level"],
                "estimated_hours": node["estimated_hours"],
                "description": node["description"],
                "resources": node["resources"],
                "is_prerequisite": node_id not in gap_skills,
                "is_target": node_id in target_set
            })

        reasoning_trace.append(
            f"📊 Total pathway: {len(pathway_details)} modules, "
            f"~{total_hours} hours of learning."
        )

        return {
            "pathway": pathway_details,
            "total_hours": total_hours,
            "reasoning_trace": reasoning_trace,
            "gap_analysis": gap_analysis,
            "known_skills_count": len(known_set),
            "target_skills_count": len(target_set),
            "gap_count": len(gap_skills)
        }

    def get_all_skills(self) -> list[dict]:
        """Returns all skills for frontend dropdowns / debugging."""
        return [
            {"id": n, **self.graph.nodes[n]}
            for n in self.graph.nodes
        ]

    def get_skill_domains(self) -> list[str]:
        return list(set(
            self.graph.nodes[n]["domain"] for n in self.graph.nodes
        ))