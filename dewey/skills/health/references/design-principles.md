# Design Principles

Twelve principles grounded in agent context research (Anthropic, OpenAI) and cognitive science (Sweller, Vygotsky, Paivio, Bjork, Pirolli, Kalyuga, Dunlosky).

## From Agent Context Research

1. **Source Primacy** -- The knowledge base is a curated guide, not a replacement for primary sources. Every entry points to one. When an agent or human needs to go deeper, the path is always clear.
2. **Dual Audience** -- Every entry serves the agent (structured, token-efficient context) and the human (readable, navigable content). When these conflict, favor human readability -- agents are more adaptable readers.
3. **Three-Dimensional Quality** -- Content quality measured across relevance, accuracy/freshness, and structural fitness simultaneously.
4. **Collaborative Curation** -- Either the human or an agent can propose additions, but all content passes through validation. The human brings domain judgment. The agent brings systematic coverage. Neither is sufficient alone.
5. **Provenance & Traceability** -- Every piece of knowledge carries metadata about where it came from, when it was last validated, and why it's in the knowledge base.
6. **Domain-Shaped Organization** -- Organized around the domain's natural structure, not file types or technical categories. The taxonomy should feel intuitive to a practitioner.
7. **Right-Sized Scope** -- Contains what's needed to be effective in the role, and no more. The curation act is as much about what you exclude as what you include.
8. **Empirical Feedback** -- Observable signals about knowledge base health: coverage gaps, stale entries, unused content. Proxy metrics inform curation decisions.
9. **Progressive Disclosure** -- Layered access so agents can discover what's available without loading everything. Metadata -> summaries -> full content -> deep references.

## From Cognitive Science Research

10. **Explain the Why** -- Causal explanations produce better comprehension and retention than stating facts alone. Every entry explains not just what to do, but why.
11. **Concrete Before Abstract** -- Lead with examples and worked scenarios, then build toward the abstraction. Concrete concepts create stronger memory traces.
12. **Multiple Representations** -- Important concepts should exist at multiple levels of depth (overview, working knowledge, reference). Material that helps novices can hinder experts and vice versa -- label each level clearly so readers self-select.
