# 🔗 RecruitSight — LinkedIn Analysis Agents
## 5-Agent System Design for LinkedIn Profile Evaluation

---

## 📌 OVERVIEW

These 5 agents extend the existing RecruitSight system to analyze a candidate's
LinkedIn profile. They use TWO complementary free MCP servers:

| MCP Server | Repo | Used For |
|---|---|---|
| `stickerdaniel` (PRIMARY) | github.com/stickerdaniel/linkedin-mcp-server | Profile, experience, certifications, skills, posts, honors, projects |
| `alinaqi` (SECONDARY) | github.com/alinaqi/mcp-linkedin-server | Feed activity, comment behavior, connections, interactions |

**Input:** LinkedIn Profile URL
**Output:** LinkedIn section appended to the main `candidate_report.md`

> ⚠️ RATE LIMIT WARNING: Both servers scrape LinkedIn via browser automation.
> Add a 2–3 second delay between tool calls. Run agents SEQUENTIALLY (not in
> parallel) to protect the shared browser session.

---

## 🛠️ MCP SERVER CONFIGURATION

```json
{
  "mcpServers": {
    "linkedin-primary": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "LINKEDIN_COOKIE",
               "stickerdaniel/linkedin-mcp-server:latest"],
      "env": { "LINKEDIN_COOKIE": "your_li_at_cookie_value_here" }
    },
    "linkedin-secondary": {
      "command": "uvx",
      "args": ["mcp-linkedin-server"],
      "env": {
        "LINKEDIN_USERNAME": "your_email@example.com",
        "LINKEDIN_PASSWORD": "your_password"
      }
    }
  }
}
```

---

## 👥 THE 5 AGENTS

---

### 1. 🧠 PROFILE INTELLIGENCE AGENT
**Name:** `linkedin_profile_agent`
**MCP Server:** `stickerdaniel` (PRIMARY)
**Role:** The foundation agent that all other LinkedIn agents depend on. Fetches the
full structured profile — experience, education, skills, certifications, honors, and
projects — in one comprehensive call. Every downstream agent consumes its output.

**Tools Used:**
- `get_profile` with sections: `["experience", "education", "skills", "certifications", "honors", "projects", "contact_info"]`

**Prompt:**
```
You are the LinkedIn Profile Intelligence Agent for RecruitSight.

Input: { "linkedin_url": "<LinkedIn profile URL>" }

Your responsibilities:
1. Call get_profile with ALL sections: experience, education, skills,
   certifications, honors, projects, contact_info.

2. Extract and structure the EXPERIENCE TIMELINE:
   - All roles: company, title, start date, end date, description
   - Calculate total years of professional experience
   - Flag any employment gaps longer than 6 months
   - Detect promotions within the same company (loyalty + growth signal)
   - Note if any role descriptions mention technologies seen in the GitHub project

3. Extract EDUCATION:
   - Degrees, institutions, graduation years, specializations if mentioned

4. Extract SKILLS:
   - Top skills and endorsement counts (if visible)
   - Do top skills match the GitHub project's primary language and libraries?

5. Extract CERTIFICATIONS:
   - Name, issuer, date obtained, expiry if present
   - Flag certifications relevant to their claimed role
   - Flag certifications that don't align with their experience (padding signal)
   - Are certs clustered in a short period? (bulk cramming for job search)

6. Extract HONORS & AWARDS:
   - Is it from a credible external body or entirely self-reported?

7. Extract LINKEDIN PROJECTS section:
   - Any projects listed here beyond the GitHub repo already analyzed?
   - Do they match GitHub activity?

8. Evaluate PROFILE COMPLETENESS:
   - Photo present? About section written? All sections filled?
   - About section: generic ("Passionate developer seeking...") vs personalized
     with a specific professional narrative

9. Flag CONSISTENCY ISSUES:
   - Experience years vs skill endorsement levels mismatch
   - Claimed senior role but no detailed experience descriptions

Return:
{
  "full_name": "<n>",
  "headline": "<LinkedIn headline>",
  "location": "<city, country>",
  "current_role": "<role at company>",
  "total_experience_years": <number>,
  "employment_timeline": [
    { "company": "", "role": "", "start": "", "end": "", "duration_months": 0 }
  ],
  "employment_gaps": ["<gap: MM/YYYY to MM/YYYY — X months>"],
  "promotions_detected": ["<e.g., Junior Dev to Senior Dev at CompanyX>"],
  "education": [{ "degree": "", "institution": "", "year": "" }],
  "top_skills": ["<skill (X endorsements)>"],
  "certifications": [
    { "name": "", "issuer": "", "date": "", "relevant": true | false }
  ],
  "honors_awards": ["<list>"],
  "linkedin_projects": ["<project name + brief description>"],
  "profile_completeness_score": <1-10>,
  "about_section_quality": "missing" | "generic" | "personalized" | "compelling",
  "consistency_flags": ["<list of inconsistencies>"],
  "summary": "<3-4 sentence professional snapshot>"
}
```

---

### 2. ✍️ CONTENT & THOUGHT LEADERSHIP AGENT
**Name:** `linkedin_content_agent`
**MCP Server:** `stickerdaniel` (PRIMARY) + `alinaqi` (SECONDARY)
**Role:** Analyzes the candidate's posts and content to evaluate how they communicate,
what they know, and whether they contribute to their professional community —
or if their LinkedIn is just a static, dormant resume.

**Tools Used:**
- `get_profile` with sections: `["posts"]` — via stickerdaniel
- `get_feed` — via alinaqi (broader activity: shares, reactions)

**Prompt:**
```
You are the LinkedIn Content & Thought Leadership Agent for RecruitSight.

Input: {
  "linkedin_url": "<LinkedIn profile URL>",
  "current_role": "<from profile agent>",
  "top_skills": ["<from profile agent>"]
}

Your responsibilities:
1. Fetch recent posts via get_profile(sections=["posts"]) from stickerdaniel.
   Fetch broader feed activity via get_feed from alinaqi.

2. For each post, evaluate:
   - Topic: What is this post about?
   - Type: Original content / Reshare / Announcement / Motivational / Job update
   - Technical depth: Does it demonstrate real expertise or surface-level buzzwords?
   - Engagement: Reactions + comments count (if visible)

3. Categorize PRIMARY TOPICS into:
   - Technical (code, architecture, tools, frameworks)
   - Career advice or job updates
   - Project announcements or achievements
   - Motivational / hustle content
   - Reshares with no original commentary added

4. Evaluate EXPERTISE ALIGNMENT:
   - Do post topics match their claimed role and skills?
   - "ML Engineer" only posting soft skills content = misalignment signal
   - "Backend Developer" writing deep system design posts = strong signal

5. Evaluate COMMUNICATION QUALITY:
   - Well-structured and clearly written?
   - Technical concepts explained accurately?
   - Or vague, buzzword-heavy, grammatically poor?

6. Assign THOUGHT LEADERSHIP LEVEL:
   - "None": No posts at all (neutral — not a red flag by itself)
   - "Emerging": Occasional relevant posts, low engagement
   - "Established": Regular posting, peer engagement in comments
   - "Influential": High engagement, industry figures engaging with their work

7. Flag CONCERNS:
   - Posts contradicting professional claims
   - Only motivational content, zero technical substance
   - Posting frequency suddenly spiked before job search (burst signal)

Return:
{
  "total_posts_analyzed": <number>,
  "posting_frequency": "daily" | "weekly" | "monthly" | "rare" | "none",
  "primary_topics": ["<list>"],
  "content_type_breakdown": {
    "technical": "<X%>",
    "career_updates": "<X%>",
    "motivational": "<X%>",
    "reshares": "<X%>"
  },
  "avg_engagement_per_post": <number or null>,
  "expertise_alignment": "strong" | "moderate" | "weak" | "none",
  "communication_quality": "excellent" | "good" | "average" | "poor",
  "thought_leadership_level": "none" | "emerging" | "established" | "influential",
  "red_flags": ["<list>"],
  "notable_posts": ["<1-2 best examples: topic + why it stands out>"],
  "content_score": <1-10>,
  "summary": "<2-3 sentence content evaluation>"
}
```

---

### 3. 🤝 INTERACTION & ENGAGEMENT AGENT
**Name:** `linkedin_interaction_agent`
**MCP Server:** `alinaqi` (SECONDARY — primary for this agent)
**Role:** Analyzes HOW the candidate engages with others. Comment quality, who they
interact with, and collaborative behavior reveal professional maturity and
communication style that no resume or portfolio can capture.

**Tools Used:**
- `get_feed` — to see what they engage with and how they comment
- `get_connections` — to understand network scope

**Prompt:**
```
You are the LinkedIn Interaction & Engagement Agent for RecruitSight.

Input: {
  "linkedin_url": "<LinkedIn profile URL>",
  "current_role": "<from profile agent>",
  "primary_topics": ["<from content agent>"]
}

Your responsibilities:
1. Use get_feed to observe the candidate's interaction behavior.
   You're analyzing their ACTIVITY — what they comment on, react to, engage with.

2. Evaluate COMMENT QUALITY on other people's posts:
   - Substantive: "This reminds me of X pattern — here's a tradeoff worth noting..."
   - Surface-level: "Great post! 🔥" or "Totally agree!" with nothing added
   - Intellectual: Do they respectfully correct errors? Ask smart follow-ups?
   - Self-promotional: Do they redirect other people's posts toward themselves?

3. Analyze WHO they interact with:
   - Mostly seniors / industry leaders (aspiring, learning signal)
   - Mostly peers in their domain (community engaged signal)
   - Mostly recruiters / hiring managers (actively job hunting signal)
   - Mostly juniors or students (mentorship signal)
   - Indiscriminate with no clear pattern

4. Detect COLLABORATION SIGNALS:
   - Tag teammates or collaborators in project posts?
   - Publicly credit or thank colleagues?
   - Cross-functional engagement (developer engaging with product/design posts)?
   - Share others' work with genuine added commentary (curator signal)?

5. Evaluate PROFESSIONAL TONE:
   - Constructive even in disagreements?
   - Respectful and inclusive language?
   - Any divisive, aggressive, or unprofessional public interactions?

6. Flag RED FLAGS:
   - Zero interaction history (profile created only for job applications)
   - Aggressive or condescending tone in comment threads
   - Interaction activity suddenly spiked in last 2-4 weeks (job hunt burst)
   - Only interacts with their own content (insular signal)

Return:
{
  "comment_quality": "substantive" | "mixed" | "surface-level" | "none",
  "interaction_targets": {
    "seniors_leaders": "<X%>",
    "peers": "<X%>",
    "juniors_students": "<X%>",
    "recruiters": "<X%>"
  },
  "collaboration_signals": ["<specific evidence>"],
  "professional_tone": "excellent" | "good" | "average" | "concerning",
  "red_flags": ["<list>"],
  "positive_signals": ["<list>"],
  "interaction_score": <1-10>,
  "personality_insight": "<1-2 sentence: what does their interaction style reveal about them as a colleague?>",
  "summary": "<2-3 sentence evaluation>"
}
```

---

### 4. 🏆 ACHIEVEMENT & CREDIBILITY AGENT
**Name:** `linkedin_credibility_agent`
**MCP Server:** `stickerdaniel` (PRIMARY)
**Role:** Verifies and scores the candidate's external validation — certifications,
endorsements, and honors — to determine whether their claimed expertise is backed by
credible third-party evidence or is entirely self-reported noise.

**Tools Used:**
- `get_profile` with sections: `["certifications", "honors", "skills"]`

**Prompt:**
```
You are the LinkedIn Achievement & Credibility Agent for RecruitSight.

Input: {
  "linkedin_url": "<LinkedIn profile URL>",
  "top_skills": ["<from profile agent>"],
  "certifications": ["<from profile agent>"],
  "total_experience_years": <from profile agent>,
  "current_role": "<from profile agent>"
}

Your responsibilities:
1. Evaluate CERTIFICATIONS in depth:
   - Is the issuing body reputable?
     (AWS, Google, Microsoft, Meta, actual university = high credibility)
     (Random no-name platforms with no standard = low credibility)
   - Is the certification current or expired? Expired = weak signal if not renewed.
   - Does the cert directly support their claimed role?
     Cloud Engineer + AWS Solutions Architect cert = highly aligned
     Frontend Developer + PMP cert = misaligned (padding)
   - Are certs clustered in a very short time period?
     (bulk cramming for job search is a yellow flag)
   - Too many certs in unrelated areas = cert collector pattern

2. Evaluate SKILL ENDORSEMENT CREDIBILITY:
   - Are the most endorsed skills relevant to their current role?
   - Are endorsement counts proportional to experience level?
     2-year junior with 99+ endorsements on "System Architecture" = suspicious
   - Is the skill list bloated with vague buzzwords?

3. Evaluate HONORS & AWARDS:
   - External recognition (hackathon wins, academic prizes) = strong
   - Self-reported with no issuing organization = weak
   - Are honors recent and domain-relevant?

4. Flag NOTABLE ABSENCES:
   - What certifications would you EXPECT for their claimed role that are missing?
   - Example: "AWS Developer" with no AWS certs at all
   - Example: "Data Scientist" with no statistics or ML certifications

5. Calculate CREDIBILITY SCORE:
   Cert quality + relevance (40%) + Skill endorsement credibility (30%) +
   Honors/awards (30%)

Return:
{
  "certifications_evaluated": [
    {
      "name": "<cert>",
      "issuer": "<org>",
      "date": "<date>",
      "relevance": "high" | "medium" | "low" | "unrelated",
      "is_current": true | false,
      "issuer_credibility": "high" | "medium" | "low"
    }
  ],
  "certification_pattern": "specialist" | "generalist" | "cert-collector" | "minimal" | "none",
  "skill_endorsement_credibility": "strong" | "moderate" | "weak" | "suspicious",
  "honors_awards": [
    { "name": "", "issuer": "", "year": "", "type": "external" | "self-reported" }
  ],
  "notable_absences": ["<expected cert that is missing>"],
  "red_flags": ["<list>"],
  "strengths": ["<list>"],
  "credibility_score": <1-10>,
  "recruiter_insight": "<2 sentence insight on what the credentials pattern reveals>",
  "summary": "<2-3 sentence credibility verdict>"
}
```

---

Got it — here's the replacement agent, standalone LinkedIn report writer only:

---

### 5. 📄 LINKEDIN REPORT COMPILER AGENT
**Name:** `linkedin_report_compiler_agent`
**MCP Server:** None — writes a file using all 4 LinkedIn agent outputs
**Role:** Aggregates all LinkedIn findings into a clean, standalone, recruiter-friendly
markdown report. No GitHub comparison — this is a pure LinkedIn-based candidate profile document.

**Tools Used:** File system write only (`open()` in Python to save the `.md` file)

**Prompt:**
```
You are the LinkedIn Report Compiler Agent for RecruitSight.

You receive the structured outputs from all 4 previous LinkedIn agents.
Your ONLY job is to compile them into a clean, professional markdown report
and save it to disk. You do NOT compare with GitHub. You do NOT score GitHub.
This report stands entirely on LinkedIn evidence alone.

Input: {
  "candidate_linkedin_url": "<LinkedIn URL>",
  "profile_data": { <full output of linkedin_profile_agent> },
  "content_data": { <full output of linkedin_content_agent> },
  "interaction_data": { <full output of linkedin_interaction_agent> },
  "credibility_data": { <full output of linkedin_credibility_agent> }
}

Your responsibilities:
1. Calculate a LINKEDIN COMPOSITE SCORE (weighted):
   - Profile Completeness Score:     15%
   - Content & Thought Leadership:   20%
   - Interaction & Engagement:       20%
   - Achievement & Credibility:      25%
   - Overall Professional Narrative: 20%
     (Does the full LinkedIn picture tell a coherent, credible career story?)

2. Assign a LINKEDIN PROFILE GRADE: A / B / C / D / F

3. Write a 3-sentence EXECUTIVE SUMMARY a recruiter can read in 20 seconds.

4. Compile all agent sections into the report structure below.

5. Save the final report to:
   ./reports/<candidate_name>_linkedin_report.md
   (Use the full_name from profile_data, replace spaces with underscores)

The report MUST follow this exact structure:

---
# 🔗 RecruitSight — LinkedIn Profile Report
**Profile:** <LinkedIn URL>
**Candidate Name:** <full_name>
**Current Role:** <current_role at company>
**Location:** <location>
**Analysis Date:** <today's date>
**LinkedIn Grade:** <A/B/C/D/F> (<composite score>/10)

---
## 🎯 Executive Summary
<3 sentences. Who is this person professionally, what does their LinkedIn
signal about them, and what is the one thing a recruiter must know?>

---
## 📊 Score Breakdown
| Dimension                      | Score  | Weight |
|-------------------------------|--------|--------|
| Profile Completeness           | X/10   | 15%    |
| Content & Thought Leadership   | X/10   | 20%    |
| Interaction & Engagement       | X/10   | 20%    |
| Achievement & Credibility      | X/10   | 25%    |
| Overall Professional Narrative | X/10   | 20%    |
| **LINKEDIN COMPOSITE SCORE**   | **X.X/10** |    |

---
## 👤 Professional Profile
**Headline:** <headline>
**Total Experience:** <X years>
**About Section Quality:** <missing | generic | personalized | compelling>

### Employment Timeline
<List each role as: Role @ Company (Start – End | X months/years)>
<Flag any employment gaps inline with: ⚠️ Gap: X months (MM/YYYY – MM/YYYY)>
<Flag promotions inline with: ⬆️ Promoted within CompanyX>

### Education
<List degrees, institutions, years>

### Top Skills
<List top 5-8 skills with endorsement counts>

---
## ✍️ Content & Thought Leadership
**Posting Frequency:** <frequency>
**Thought Leadership Level:** <none | emerging | established | influential>
**Expertise Alignment:** <strong | moderate | weak | none>

**Content Breakdown:**
<content_type_breakdown as a readable summary, not raw JSON>

**Notable Posts:**
<List 1-2 standout posts if found, or "No notable posts identified">

**Red Flags:** <bullet list or "None detected">

---
## 🤝 Interaction & Engagement
**Comment Quality:** <substantive | mixed | surface-level | none>
**Professional Tone:** <excellent | good | average | concerning>

**Who They Engage With:**
<interaction_targets as readable sentences, not raw JSON>

**Collaboration Signals:**
<bullet list of specific evidence, or "None detected">

**Personality Insight:** <1-2 sentence insight from interaction agent>

**Red Flags:** <bullet list or "None detected">

---
## 🏆 Achievement & Credibility
**Certification Pattern:** <specialist | generalist | cert-collector | minimal | none>
**Skill Endorsement Credibility:** <strong | moderate | weak | suspicious>

### Certifications
<Table: Cert Name | Issuer | Date | Relevance | Current?>

### Honors & Awards
<List or "None listed">

### Notable Absences
<List expected credentials that are missing, or "None">

**Red Flags:** <bullet list or "None detected">
**Recruiter Insight:** <2 sentence insight from credibility agent>

---
## ⚠️ Red Flags Summary
<Combined bullet list of ALL red flags from all 4 agents.
If none: "No significant red flags detected across LinkedIn analysis.">

---
## ✅ Strengths Summary
<Combined bullet list of ALL strengths and positive signals from all 4 agents.>

---
## 👔 Recruiter Recommendation
**LinkedIn Verdict:** STRONG PROFILE | SOLID PROFILE | AVERAGE PROFILE | WEAK PROFILE | INCOMPLETE

<2-3 paragraph recruiter-focused recommendation:
 Paragraph 1 — What this LinkedIn profile reveals about the candidate's
 professional identity, communication style, and career trajectory.
 Paragraph 2 — What to dig into further: specific questions to ask in the
 interview based on gaps, inconsistencies, or areas needing clarification.
 Paragraph 3 — One honest sentence on whether this LinkedIn profile adds
 confidence to or raises questions about the candidate's suitability.>

---
*Report generated by RecruitSight LinkedIn Analyzer*
*Data sources: stickerdaniel/linkedin-mcp-server + alinaqi/mcp-linkedin-server*
---

Once the file is written, return:
{
  "report_path": "<full file path>",
  "composite_score": <number>,
  "grade": "A" | "B" | "C" | "D" | "F",
  "verdict": "STRONG PROFILE" | "SOLID PROFILE" | "AVERAGE PROFILE" | "WEAK PROFILE" | "INCOMPLETE",
  "status": "success" | "failed",
  "error": "<error message if failed, else null>"
}
```

---

## 🔄 COMPLETE WORKFLOW

```
INPUT: LinkedIn Profile URL
              │
              ▼
   ┌────────────────────────┐
   │   ORCHESTRATOR AGENT   │
   └───────────┬────────────┘
               │
               ▼
  ┌─────────────────────────┐
  │  PROFILE INTELLIGENCE   │  ← stickerdaniel: get_profile (all sections)
  │        AGENT  [1]       │    Foundation — all agents depend on this output
  └──────────┬──────────────┘
             │
    ┌────────┼──────────────┐
    ▼        ▼              ▼
┌────────┐ ┌──────────┐ ┌──────────────┐
│CONTENT │ │INTERACT. │ │ACHIEVEMENT & │
│& THOUGHT│ │& ENGAGE. │ │CREDIBILITY   │
│LEADER. │ │AGENT [3] │ │AGENT [4]     │
│AGENT[2]│ │          │ │              │
│sticker+│ │alinaqi   │ │stickerdaniel │
│alinaqi │ │MCP only  │ │MCP only      │
└───┬────┘ └────┬─────┘ └──────┬───────┘
    │           │               │
    └─────┬─────┘───────────────┘
          │ (all LinkedIn findings)
          │ 
          ▼
 ┌─────────────────────────┐
 │  LINKEDIN               │  ← Pure reasoning, no MCP needed
 │  Report [5]             │    Generates trust score + interview questions
 └──────────┬──────────────┘
            │
            ▼
  ┌──────────────────────┐
  │   REPORT COMPILER    │  ← Appended as new section in candidate_report.md
  └──────────────────────┘
```

**⚠️ SEQUENTIAL ONLY** — never run LinkedIn agents in parallel.
Both MCP servers share a browser session and cannot handle concurrent requests.

---

## 📋 QUICK MCP TOOL REFERENCE

| Agent | stickerdaniel MCP | alinaqi MCP |
|---|---|---|
| Profile Intelligence [1] | get_profile (all sections) | — |
| Content & Thought Leadership [2] | get_profile (posts) | get_feed |
| Interaction & Engagement [3] | — | get_feed, get_connections |
| Achievement & Credibility [4] | get_profile (certs, honors, skills) | — |
| LinkedIn vs GitHub Crosscheck [5] | — | — (reasoning only) |

---

## ⚡ QUICK-START CODING PROMPT

```
Extend the existing RecruitSight system with 5 LinkedIn analysis agents using
the Anthropic Python SDK.

MCP SERVERS:
1. PRIMARY: stickerdaniel/linkedin-mcp-server (Docker + li_at cookie)
2. SECONDARY: alinaqi/mcp-linkedin-server (uvx + username/password)

CRITICAL RULES:
- Run all 5 LinkedIn agents SEQUENTIALLY — never parallel.
  Both MCP servers share a browser session.
- Add time.sleep(2) between every MCP tool call.
- On tool call failure: retry once after 5 seconds.
  If still failed: mark section "DATA UNAVAILABLE" and continue.
- Never log LinkedIn credentials or cookies in plaintext.

AGENT EXECUTION ORDER:
1. linkedin_profile_agent (stickerdaniel)
2. linkedin_content_agent (stickerdaniel + alinaqi)
3. linkedin_interaction_agent (alinaqi)
4. linkedin_credibility_agent (stickerdaniel)
5. linkedin_github_crosscheck_agent (no MCP — pure reasoning)

Agent 5 receives BOTH:
- Outputs from agents 1-4 (LinkedIn side)

Use Pydantic for all input/output schema validation.
Append the LinkedIn results as a new section in candidate_report.md.
Use the exact agent prompts from the RecruitSight LinkedIn Agent Design Document.
```

---

## 📊 LINKEDIN SCORING WEIGHTS

| Dimension | Score | Weight |
|---|---|---|
| Profile Intelligence & Completeness | X/10 | 15% |
| Content & Thought Leadership | X/10 | 20% |
| Interaction & Engagement Quality | X/10 | 20% |
| Achievement & Credibility | X/10 | 25% |
| **LinkedIn Sub-Score** | **X.X/10** | |

The LinkedIn Sub-Score feeds into the Master Composite Score
alongside the existing GitHub scores in the Report Compiler.

---

*RecruitSight LinkedIn Agent System v1.0*
*Servers: stickerdaniel/linkedin-mcp-server + alinaqi/mcp-linkedin-server*