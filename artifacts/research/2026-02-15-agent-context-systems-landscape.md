# Landscape Map: Agent Context Systems & Knowledge for Dual Audiences

## Strategic Summary

The agent context space is rapidly consolidating around a layered hybrid model: structured Markdown files for stable domain knowledge, RAG/retrieval for large dynamic collections, MCP as the universal interop layer, and knowledge graphs for relationship-rich domains. The biggest gap in the landscape is a purpose-built tool for curating version-controlled knowledge bases that serve both human learners and AI agents equally -- traditional KM tools added AI to help humans, agent memory tools serve agents only, and "knowledge as code" conventions (AGENTS.md, CLAUDE.md) lack tooling for quality, freshness, and curation. This is exactly where Dewey sits.

## Scope

**Included:** Tools, frameworks, and approaches for grounding AI agents with domain knowledge, with particular attention to systems that also serve human learning and upskilling. Covers RAG frameworks, vector databases, coding agent context injection, knowledge management platforms, developer documentation tools, learning platforms, knowledge-as-code approaches, agent memory systems, and emerging standards (MCP, AGENTS.md, llms.txt).

**Excluded:** General-purpose LLM fine-tuning platforms, prompt marketplaces, AI code generation tools (except their context mechanisms), pure chatbot builders.

---

## Categories

### 1. RAG Frameworks & Retrieval Infrastructure

The backbone for dynamically grounding agents with large document collections.

- **Established players:** LangChain/LangGraph (most widely adopted, 600-800 companies in production), LlamaIndex (retrieval specialist, 35% accuracy boost over LangChain), Haystack (enterprise-grade, 99.9% uptime, dominant in regulated industries)
- **Emerging players:** DSPy (Stanford -- programmatic prompt optimization, lowest overhead at ~3.5ms), Pathway (real-time streaming RAG, 60K msg/sec, used by NATO/Intel)
- **Key tools:** LangGraph for orchestration, LlamaIndex for ingestion/indexing, Haystack for production reliability
- **Trend:** RAG is being subsumed into "context engineering" as a broader discipline. Agentic RAG (self-evaluating, multi-step retrieval loops) is entering production. 60% of LLM apps now use RAG. Framework boundaries are blurring toward interoperability.

### 2. Vector Databases

The storage layer for embedding-based retrieval.

- **Established players:** Pinecone (managed, enterprise-dominant, highest cost), Milvus (billion-vector scale, strongest distributed architecture), Weaviate (open-source, best hybrid search)
- **Emerging players:** Qdrant (best free tier, Rust-based, edge-friendly), pgvector (PostgreSQL extension -- "good enough" for teams already on Postgres)
- **Prototyping tier:** Chroma (developer-friendly, embeddable, not enterprise-scale)
- **Trend:** Convergence toward hybrid search (vector + keyword). pgvector gaining share as pragmatic choice. Purpose-built vector DBs differentiating on operational simplicity (Pinecone) vs cost/flexibility (Qdrant, Weaviate).

### 3. Coding Agent Context Injection

How coding assistants get project-specific knowledge.

- **Static context files:**
  - CLAUDE.md (Claude Code) -- hierarchical, always loaded, version-controlled
  - AGENTS.md (cross-tool standard) -- 60,000+ repos, backed by OpenAI/Google/Cursor/Factory
  - Cursor Rules (.cursor/rules/*.mdc) -- YAML frontmatter for conditional activation, glob-based scoping
  - GitHub Copilot Instructions (.github/copilot-instructions.md) -- layered priority (personal > repo > org)
- **Key finding:** Vercel's evals showed 8KB of always-present static context achieved 100% pass rate vs 79% for on-demand skill retrieval -- agents failed to look up knowledge they needed 56% of the time
- **Trend:** Multiple formats converging toward a common pattern: static Markdown in repo, version-controlled, injected into every conversation. AGENTS.md is the leading cross-tool candidate. Static context beats dynamic retrieval for coding agents.

### 4. Agent Grounding Primitives (Provider-Level)

Built-in grounding tools from major AI providers.

- **Anthropic:** CLAUDE.md hierarchy + Agent Skills (progressive disclosure: metadata -> SKILL.md -> workflows -> references) + MCP for external tools
- **OpenAI:** Responses API with built-in file_search (RAG over uploaded docs) and web_search. Agents SDK for orchestration. Knowledge Retrieval Blueprint as turnkey pattern. Assistants API deprecated (Aug 2026 shutdown).
- **Google:** Gemini API grounding with Google Search (dynamic retrieval auto-decides when to ground). Vertex AI Search for enterprise docs. Agent Development Kit (ADK) with grounding as built-in primitives.
- **Microsoft:** Unified Agent Framework (merged AutoGen + Semantic Kernel, GA Q1 2026). Deep Azure integration. 40+ Azure services via MCP server.
- **Trend:** Grounding is becoming a first-class primitive, not an application-layer concern. All major providers now ship grounding as built-in tools rather than leaving it to developers.

### 5. MCP (Model Context Protocol) Ecosystem

The universal interop layer for agent-to-tool connectivity.

- **Scale:** 97M+ monthly SDK downloads, 5,800+ servers, 300+ clients
- **Governance:** Donated to Linux Foundation (AAIF) Dec 2025 for vendor-neutral stewardship
- **Adoption:** OpenAI, Google DeepMind, Microsoft, Cursor, Figma, Replit, Sourcegraph, Zapier all support it
- **What's being built:** Databases (PostgreSQL, Cosmos DB), dev tools (GitHub, Docker), communication (Slack, Notion), CRM (HubSpot, Salesforce), search (Ahrefs), cloud infra (40+ Azure services)
- **Market size:** ~$1.8B in 2025; Gartner predicts 75% of gateway vendors will have MCP features by 2026
- **Trend:** MCP won the interop layer -- it is the USB-C of agent connectivity. The question is no longer adoption but governance at enterprise scale.

### 6. AI-Aware Knowledge Management Platforms

Traditional KM tools that added AI features for human users.

- **Established players:** Notion AI (multi-model, Ask Notion, AI Agents), Confluence + Rovo (Teamwork Graph search, Rovo Agents), Glean (enterprise AI search overlay, $50+/user/mo)
- **Mid-market:** Guru (MCP + API support -- rare for KM tools), Slite (clean AI search for small teams), Tettra (Slack-native Q&A bot)
- **Trend:** All added AI to help humans find and consume knowledge faster. Almost none created pathways for external AI agents to consume their knowledge as structured context. Guru is the notable exception with MCP/API support.
- **Gap:** These tools are walled gardens. Knowledge trapped inside proprietary platforms, inaccessible to AI coding agents or other external systems.

### 7. Developer Documentation Tools

Documentation platforms, increasingly bridging human readers and AI agents.

- **Dual-audience leaders:** Mintlify (llms.txt + MCP + AI chat -- strongest dual-audience positioning), Backstage/AiKA (TechDocs as Markdown-in-repo + MCP server + AI assistant), Inkeep (bolt-on AI chat + MCP over any existing docs)
- **Human-first:** GitBook (polished editor + git-sync, limited AI agent path), Docusaurus (open-source, Markdown-in-repo, no native AI), ReadMe (interactive API docs)
- **Trend:** MCP support is the dividing line. Tools with MCP (Mintlify, Backstage, Inkeep) are genuinely dual-audience. Those without remain human-only documentation.

### 8. Knowledge-as-Code Approaches

Knowledge stored in repositories, version-controlled, consumed by humans reading Markdown and agents loading context.

- **Conventions:** AGENTS.md (cross-tool, 60K+ repos), CLAUDE.md (Claude Code), Agent Skills (Anthropic -- progressive disclosure architecture), llms.txt (844K+ websites, unproven effectiveness)
- **Structural frameworks:** Diataxis (tutorials/how-to/reference/explanation), Dewey's three-depth model (overview/working/reference)
- **Tools:** None purpose-built. This is the gap. AGENTS.md is a convention, not a product. No commercial tool exists for curating, validating, and maintaining knowledge bases that live in git repos.
- **Trend:** The pattern is validated by production systems (Spotify 1,500+ merged PRs, Manus, Vercel evals). What's missing is tooling for quality, freshness, and curation.

### 9. Agent Memory & Knowledge Graph Systems

Tools for persistent agent knowledge that accumulates over time.

- **Established:** Neo4j (de facto graph DB, native vector+graph), Microsoft GraphRAG (knowledge graphs from corpora, 3-5x cost of vector RAG)
- **Emerging:** Cognee (open-source knowledge engine for agent memory, integrates with LangGraph/ADK/Claude), Anthropic Memory Tool (39% performance boost, 84% token reduction)
- **Research:** ACE framework (agentic context engineering -- contexts as evolving playbooks)
- **Trend:** Knowledge graphs are experiencing a renaissance as a grounding layer. GraphRAG enables queries that vector-only RAG cannot ("tell me about all themes in this dataset"). LinkedIn reduced ticket resolution by 63% with GraphRAG.

### 10. Learning & Upskilling Platforms

Human-focused learning tools with AI personalization.

- **Established:** Coursera/edX (MOOC), Degreed + Maestro (enterprise L&D, AI learning paths), Cornerstone (enterprise LXP)
- **Spaced repetition:** Anki (gold standard, 37% better retention), RemNote (note-taking + spaced repetition + knowledge graph)
- **Frontline:** Axonify (micro-learning for frontline workers, AI-driven personalization)
- **Trend:** AI personalizes learning for humans but creates no pathways for AI agent consumption. These platforms are entirely human-focused. The bridge between "knowledge that teaches humans" and "knowledge that grounds agents" does not exist in this category.

### 11. Personal Knowledge Management

Individual knowledge tools with AI features.

- **Dual-audience potential:** Obsidian (local-first Markdown vault, 2700+ plugins, AI plugins for Q&A -- vault IS a knowledge-as-code repo), Tana (supertag-structured knowledge graph + MCP integration -- genuine dual-audience)
- **AI-first:** Mem.ai (auto-organizes with knowledge graph, but graph is invisible to external agents)
- **Trend:** Obsidian's Markdown-in-repo model and Tana's MCP integration represent the closest personal tools to true dual-audience. The gap is structured metadata for agent consumption.

---

## Landscape Map

```
                    AGENT-FIRST                          HUMAN-FIRST
                         |                                    |
                         |                                    |
    INFRASTRUCTURE       |         DUAL-AUDIENCE              |        HUMAN-ONLY
    ==================== | ================================== | ====================
                         |                                    |
    RAG Frameworks       |    Mintlify (llms.txt + MCP)       |    Notion AI
      LangGraph          |    Backstage/AiKA (MCP)            |    Confluence/Rovo
      LlamaIndex         |    Inkeep (MCP bolt-on)            |    Slite
      Haystack           |    Guru (MCP + API)                |    Tettra
      DSPy               |    Tana (supertags + MCP)          |    GitBook
                         |                                    |    ReadMe
    Vector DBs           |    AGENTS.md (convention)          |
      Pinecone           |    CLAUDE.md (convention)          |    Learning Platforms
      Weaviate           |    Agent Skills (convention)       |      Degreed/Maestro
      Qdrant             |    Obsidian (Markdown vault)       |      Cornerstone
      Milvus             |                                    |      Axonify
                         |    *** DEWEY SITS HERE ***         |      RemNote/Anki
    Agent Memory         |    (curated KB in repo,            |
      Cognee             |     quality validation,            |    KM Walled Gardens
      Anthropic Memory   |     progressive disclosure,        |      Glean
      GraphRAG           |     human + agent audience)        |      Mem.ai
                         |                                    |
    MCP Ecosystem        |                                    |
      5,800+ servers     |                                    |
      97M+ SDK downloads |                                    |
                         |                                    |
    Provider Primitives  |                                    |
      OpenAI file_search |                                    |
      Gemini grounding   |                                    |
      Vertex AI Search   |                                    |
```

---

## Trends

- **Context engineering is the new discipline.** Anthropic formalized four operations (write, select, compress, isolate). Manus, Spotify, and LangChain have independently validated this framework. "Prompt engineering" is being subsumed -- the bottleneck is not the prompt but the context surrounding it.

- **Static beats dynamic for coding agents.** Vercel's evals showed always-present 8KB of curated context outperformed on-demand skill retrieval (100% vs 79%). Agents fail to look up knowledge they need 56% of the time. Implication: curated, always-loaded knowledge is more valuable than sophisticated retrieval for most coding workflows.

- **MCP is the universal bridge.** Any knowledge platform that adds MCP support instantly becomes accessible to AI agents. This is the single most impactful infrastructure development for dual-audience knowledge. The tools pulling ahead (Mintlify, Backstage, Guru, Tana) are the ones with MCP.

- **Progressive disclosure is validated.** Anthropic (Agent Skills), LlamaIndex (hierarchical indices), Inferable (progressive context enrichment), and Spotify (context engineering for background agents) all demonstrate that layered, on-demand context outperforms everything-at-once. Dewey's three-depth model (overview/working/reference) aligns directly.

- **Knowledge-as-code is emerging but lacks tooling.** AGENTS.md has 60K+ repos. Agent Skills are gaining traction. llms.txt has 844K+ websites. But all are conventions, not products. No one has built the "ESLint for knowledge" -- a tool that validates, freshens, and curates knowledge bases living in git repos.

- **Traditional KM is a walled garden.** Notion, Confluence, Slite, and Tettra added AI to help humans inside their platforms. They did not create pathways for external AI agents. Knowledge trapped in these tools is invisible to coding agents.

- **Provider grounding is commoditizing.** OpenAI, Google, and Anthropic all ship grounding as first-class built-in tools. The differentiation is moving up the stack to curation quality, domain specificity, and feedback loops.

---

## Gaps & White Space

- **Knowledge-as-code tooling.** No commercial product exists for curating, validating, and maintaining structured knowledge bases in git repos that serve both humans and AI agents. AGENTS.md/CLAUDE.md are conventions without quality infrastructure. Dewey is the only tool addressing this with validators, health scoring, freshness checking, and utilization tracking. Opportunity: significant, given 60K+ repos already using AGENTS.md.

- **Human upskilling from agent knowledge.** Learning platforms personalize for humans. Agent memory systems accumulate for agents. Nothing bridges the two. A knowledge base that teaches a human the domain AND grounds an agent in the same domain simultaneously does not exist as a product category. Dewey's "dual audience" design principle directly targets this.

- **Knowledge quality feedback loops.** Utilization data (which knowledge files actually get used by agents) and health data (freshness, accuracy, coverage) are not systematically tracked by any tool. Dewey's three-tier health model (deterministic validators + LLM-assisted assessment + human judgment) is unique in the landscape.

- **Cross-tool knowledge portability.** Each coding agent has its own context format (CLAUDE.md, .cursorrules, copilot-instructions.md, JULES.md). AGENTS.md is converging as the standard, but there's no tool that manages the translation/sync between formats. An opportunity for Dewey or a complementary tool.

- **Knowledge curation as a discipline.** "Context engineering" is recognized. "Knowledge curation for agents" is not yet a named practice. The craft of deciding what goes in a knowledge base, at what depth, organized how, validated when -- this is what Dewey's skills and design principles codify.

---

## Key Insights

1. **The dual-audience gap is real and under-served.** Traditional KM tools serve humans. Agent memory tools serve agents. The tools in the "dual-audience" column of the landscape map are either conventions without products (AGENTS.md), documentation platforms (Mintlify), or personal tools (Tana, Obsidian). None combine curation, validation, progressive disclosure, and feedback loops for production knowledge bases.

2. **Curated static context is more valuable than most people think.** Vercel's 100% vs 79% finding is striking. For domain knowledge that changes at "human speed" (architectural decisions, compliance requirements, domain concepts), a curated 8KB Markdown file outperforms a sophisticated retrieval pipeline. The bottleneck is curation quality, not retrieval sophistication.

3. **The market is splitting into infrastructure and curation.** RAG frameworks, vector databases, and MCP are infrastructure -- they move knowledge around. But they don't address what knowledge to create, how to organize it, when to update it, or how to measure if it's working. Dewey operates in the curation layer, which is orthogonal to (and compatible with) any infrastructure choice.

4. **Progressive disclosure is the winning architecture.** Across Anthropic's Agent Skills, LlamaIndex's hierarchical indices, Dewey's three-depth model, and Diataxis's four-type framework, the pattern is the same: layered access where consumers (human or AI) get the minimum context needed and drill deeper on demand. This is not just a nice-to-have -- it's a prerequisite for effective context engineering at scale.

5. **MCP is the adoption accelerator.** Any knowledge system that exposes itself via MCP becomes instantly consumable by every major AI coding agent. For Dewey, adding MCP support to expose knowledge base contents would dramatically expand its reach beyond Claude Code.

---

## Implications for Dewey

- **Dewey occupies a genuine white space.** No other tool combines: (1) knowledge stored as version-controlled Markdown in a git repo, (2) multi-depth progressive disclosure (overview/working/reference), (3) automated quality validation (three-tier health model), (4) utilization tracking and feedback loops, (5) explicit dual-audience design for both human readers and AI agents. The closest competitors are conventions (AGENTS.md) or documentation platforms (Mintlify), neither of which addresses curation discipline.

- **The "knowledge as code" movement validates the approach.** 60K+ repos with AGENTS.md, 844K+ sites with llms.txt, and Anthropic's Agent Skills standard all confirm that Markdown-in-repo is the winning format for agent context. Dewey is already building on this foundation.

- **MCP support would be a force multiplier.** Adding an MCP server that exposes knowledge base contents (with progressive disclosure -- metadata first, then summaries, then full content) would make Dewey-curated knowledge accessible to Cursor, Copilot, Gemini, and any other MCP-compatible agent, not just Claude Code.

- **The quality/freshness gap is Dewey's moat.** Everyone can write Markdown files. Nobody else validates them, tracks their freshness, measures their utilization, or surfaces curation recommendations. Dewey's three-tier health model is unique infrastructure that becomes more valuable as knowledge bases grow.

- **Consider positioning around "context engineering for teams."** The industry has adopted "context engineering" as the discipline name. Dewey could be positioned as the tool that makes context engineering systematic -- turning ad hoc knowledge files into a managed, quality-assured knowledge base with feedback loops.

---

## Implementation Context

<claude_context>
<positioning>
- opportunities:
  - Knowledge-as-code tooling (no commercial product exists)
  - Quality/freshness/utilization infrastructure for knowledge bases
  - MCP server for cross-agent knowledge distribution
  - Bridge between human upskilling and agent grounding
- crowded:
  - RAG frameworks and vector databases (mature, commoditizing)
  - General-purpose KM platforms (Notion, Confluence walled gardens)
  - Provider-level grounding primitives (OpenAI, Google, Anthropic)
- emerging:
  - Agent Skills as open standard (Anthropic, Dec 2025)
  - Cross-tool knowledge portability (AGENTS.md convergence)
  - Knowledge graph + RAG hybrid (GraphRAG pattern)
  - Context engineering as named discipline
</positioning>
<technical>
- standard_stack: Markdown in git repos, YAML frontmatter for metadata, progressive disclosure via file hierarchy, MCP for interop
- integrations: MCP (universal bridge), AGENTS.md (cross-tool standard), Claude Code hooks (current), potential Cursor/Copilot integration via MCP
- tools_to_evaluate:
  - MCP SDK (for building a Dewey knowledge server)
  - Mintlify (study their llms.txt + MCP implementation as reference)
  - Inkeep (study their bolt-on AI chat + MCP pattern)
  - Tana (study their supertag structured knowledge approach)
  - Cognee (study their agent memory knowledge graph)
</technical>
<trends>
- adopt: Context engineering vocabulary and framework (write/select/compress/isolate), MCP for knowledge distribution, progressive disclosure as core architecture, AGENTS.md compatibility
- watch: GraphRAG for relationship-rich knowledge, Agent Skills standardization, llms.txt adoption and effectiveness, cross-tool knowledge portability
- avoid: Building a RAG pipeline (commoditized), creating a walled-garden platform (market is moving to open formats), fine-tuning for domain knowledge (retrieval/context approach is winning)
</trends>
</claude_context>

---

## Next Action

- **Deep dive on MCP server implementation** -- evaluate adding an MCP server to Dewey that exposes knowledge base contents with progressive disclosure
- **Competitive research on Mintlify + Inkeep** -- study their dual-audience implementation as reference patterns
- **Run /plan/brief** to define Dewey's positioning strategy based on this landscape

---

## Sources

### RAG Frameworks & Infrastructure
- [RAG Frameworks: LangChain vs LangGraph vs LlamaIndex](https://research.aimultiple.com/rag-frameworks/)
- [Production RAG in 2026: LangChain vs LlamaIndex](https://rahulkolekar.com/production-rag-in-2026-langchain-vs-llamaindex/)
- [15 Best Open-Source RAG Frameworks in 2026](https://www.firecrawl.dev/blog/best-open-source-rag-frameworks)
- [RAG Frameworks: Top 5 Picks for Enterprise AI](https://alphacorp.ai/top-5-rag-frameworks-november-2025/)
- [DSPy: Programming Language Models](https://dspy.ai/)
- [Compare Top 7 RAG Frameworks (Pathway)](https://pathway.com/rag-frameworks/)

### Vector Databases
- [Vector Database Comparison 2025](https://liquidmetal.ai/casesAndBlogs/vector-comparison/)
- [Best Vector Databases for RAG 2025](https://latenode.com/blog/ai-frameworks-technical-infrastructure/vector-databases-embeddings/best-vector-databases-for-rag-complete-2025-comparison-guide)
- [Top 9 Vector Databases Feb 2026 (Shakudo)](https://www.shakudo.io/blog/top-9-vector-databases)
- [7 Best Vector Databases 2026 (DataCamp)](https://www.datacamp.com/blog/the-top-5-vector-databases)

### Coding Agent Context
- [AGENTS.md - Open format for coding agents](https://agents.md/)
- [AGENTS.md Emerges as Open Standard (InfoQ)](https://www.infoq.com/news/2025/08/agents-md/)
- [AGENTS.md outperforms skills in agent evals (Vercel)](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)
- [Writing a good CLAUDE.md (HumanLayer)](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- [Cursor AI Complete Guide 2025](https://medium.com/@hilalkara.dev/cursor-ai-complete-guide-2025-real-experiences-pro-tips-mcps-rules-context-engineering-6de1a776a8af)
- [GitHub Copilot Custom Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)

### MCP Ecosystem
- [A Year of MCP: Internal Experiment to Industry Standard](https://www.pento.ai/blog/a-year-of-mcp-2025-review)
- [Why MCP Won (The New Stack)](https://thenewstack.io/why-the-model-context-protocol-won/)
- [2026: Enterprise-Ready MCP Adoption (CData)](https://www.cdata.com/blog/2026-year-enterprise-ready-mcp-adoption)
- [MCP Enterprise Adoption Guide](https://guptadeepak.com/the-complete-guide-to-model-context-protocol-mcp-enterprise-adoption-market-trends-and-implementation-strategies/)
- [MCP Impact 2025 (Thoughtworks)](https://www.thoughtworks.com/en-us/insights/blog/generative-ai/model-context-protocol-mcp-impact-2025)

### Context Engineering
- [Effective Context Engineering for AI Agents (Anthropic)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Context Engineering: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)
- [Context Engineering (LangChain)](https://blog.langchain.com/context-engineering-for-agents/)
- [Background Coding Agents: Context Engineering (Spotify)](https://engineering.atspotify.com/2025/11/context-engineering-background-coding-agents-part-2)
- [Claude Code Best Practices (Anthropic)](https://www.anthropic.com/engineering/claude-code-best-practices)

### Agent Grounding & Providers
- [New Tools for Building Agents (OpenAI)](https://openai.com/index/new-tools-for-building-agents/)
- [Knowledge Retrieval Blueprint (OpenAI)](https://openai.com/solutions/blueprints/knowledge-retrieval/)
- [Grounding Overview (Vertex AI)](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview)
- [ADK Overview (Google)](https://google.github.io/adk-docs/)
- [Agent Skills (Anthropic)](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Microsoft Agent Framework](https://cloudsummit.eu/blog/microsoft-agent-framework-production-ready-convergence-autogen-semantic-kernel/)

### Knowledge Management Platforms
- [Notion AI Review 2026](https://max-productive.ai/ai-tools/notion-ai/)
- [Rovo in Confluence](https://www.atlassian.com/software/confluence/ai)
- [Guru Review 2026](https://www.siit.io/tools/trending/guru-review)
- [Glean](https://www.glean.com)
- [Emerging Agent Stack (Glean)](https://www.glean.com/blog/emerging-agent-stack-2026)

### Developer Documentation
- [Mintlify](https://www.mintlify.com)
- [Mintlify Review 2026](https://ferndesk.com/blog/mintlify-review)
- [AiKA Introduction (The New Stack)](https://thenewstack.io/introducing-aika-backstage-portal-ai-knowledge-assistant/)
- [Inkeep](https://inkeep.com/)
- [GitBook Review 2026](https://ferndesk.com/blog/gitbook-review)

### Knowledge-as-Code & Standards
- [Agent Rules Repo](https://github.com/steipete/agent-rules)
- [llms.txt Adoption](https://llms-txt.io/blog/is-llms-txt-dead)
- [Progressive Disclosure Might Replace MCP (MCPJam)](https://www.mcpjam.com/blog/claude-agent-skills)
- [Progressive Context Enrichment (Inferable)](https://www.inferable.ai/blog/posts/llm-progressive-context-encrichment)
- [Diataxis Framework](https://diataxis.fr/)

### Knowledge Graphs & Agent Memory
- [GraphRAG (Microsoft Research)](https://www.microsoft.com/en-us/research/project/graphrag/)
- [GraphRAG with Neo4j and LangChain](https://pub.towardsai.net/graphrag-explained-building-knowledge-grounded-llm-systems-with-neo4j-and-langchain-017a1820763e)
- [Cognee](https://www.cognee.ai/)
- [Tana](https://tana.inc/)

### Learning Platforms
- [RemNote](https://www.remnote.com/)
- [Obsidian AI 2025](https://www.eesel.ai/blog/obsidian-ai)

### RAG vs Fine-Tuning vs Context
- [Is RAG Dead? Context Engineering (Towards Data Science)](https://towardsdatascience.com/beyond-rag/)
- [RAG Isn't Dead (The New Stack)](https://thenewstack.io/rag-isnt-dead-but-context-engineering-is-the-new-hotness/)
- [Beyond the Hype: RAG Remains Essential (Pinecone)](https://www.pinecone.io/learn/rag-2025/)
- [Long Context vs RAG (arXiv)](https://arxiv.org/abs/2501.01880)
- [Agentic Context Engineering (arXiv)](https://arxiv.org/abs/2510.04618)
