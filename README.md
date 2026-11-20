![Jacob Isaacson — AI systems and software engineering. Plan, build, review: building software factories and keeping humans in control.](assets/banner.svg)

<p align="center">
  <b>Senior Software Engineer · AI Agents · Software Factories</b><br>
  I build backend systems and tools that help people turn ideas into working software.
</p>

<p align="center">
  <a href="https://github.com/search?q=is%3Apr+author%3Ajacoboi33+-user%3Ajacoboi33&type=pullrequests"><img alt="Open-source contributions" src="https://img.shields.io/badge/Open_source-contributions-22D3EE?style=for-the-badge&logo=git&logoColor=white&labelColor=08191E"></a>
  <a href="https://carbonstudios.dev"><img alt="Carbon Studios" src="https://img.shields.io/badge/Carbon_Studios-carbonstudios.dev-22D3EE?style=for-the-badge&logo=googlechrome&logoColor=white&labelColor=08191E"></a>
  <a href="https://www.linkedin.com/in/jacob-isaacson-profile/"><img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-Connect-22D3EE?style=for-the-badge&labelColor=08191E"></a>
  <a href="mailto:jisaacs46@gmail.com"><img alt="Email jisaacs46@gmail.com" src="https://img.shields.io/badge/Email-jisaacs46@gmail.com-22D3EE?style=for-the-badge&logo=gmail&logoColor=white&labelColor=08191E"></a>
</p>

---

## 🛩️ What I’m building

My current focus: coordinating AI agents across planning, implementation, review, and testing — with a human approving what ships. Everything is built to be model-agnostic: the same workflows run on Claude Code, Codex, and Kiro.

```mermaid
flowchart LR
    idea([Idea]) --> plan[Planner agents]
    plan --> build[Builder agents<br>code + tests]
    build --> review[Reviewer agents]
    review -- changes requested --> build
    review -- passes --> human{Human approval}
    human -- rework --> plan
    human -- approved --> ship([Shipped])
```

### Squadron — the software factory
An AI-powered software factory: planner, builder, and reviewer agents working together, with a human approving every change. *(Private)*

### Swarm Commander — the agent swarm
Portable multi-agent workflow definitions: specialist roles, structured handoffs, shared steering, and skills. One definition, any provider — Claude Code, Codex, and Kiro today. *(Private)*

### Flight Deck — the cockpit
The IDE you command the swarm from: multiple AI coding providers working side by side, with reviewed changes applied deliberately rather than blindly. *(Private)*

### Carbon Studios — the business
[carbonstudios.dev](https://carbonstudios.dev) — lead-generating websites, booking flows, and automation systems for local and professional service businesses in Utah. Engineered, not assembled.

## 🔧 Open-source work

### OperationKit · AI-review reliability

[View pull request #127 →](https://github.com/Axia-Growth/OperationKit/pull/127) <img alt="Pull request #127 status" src="https://img.shields.io/github/pulls/detail/state/Axia-Growth/OperationKit/127?style=flat-square">

Proposed a fix that prevents an AI review from recording success when its own checklist explicitly reports a failure. The contribution also preserves blocked results, improves a slow parser pattern, and adds regression and database integration tests.

Built with Claude Code, with testing details and tradeoffs documented in the pull request.

## 🧭 How I work

- **Humans approve, agents execute.** Automation does the legwork; people make the calls that matter.
- **Every change is reviewable.** Clear handoffs and small diffs beat a black box.
- **Trust is earned with tests.** A prototype becomes a product when it can prove it works.
- **No model lock-in.** Workflows, steering, and skills are portable across LLMs and providers.

## 🧰 Tools I work with

**Backend**<br>
<img alt="Go" src="https://img.shields.io/badge/Go-08191E?style=flat-square&logo=go&logoColor=22D3EE">
<img alt="Java" src="https://img.shields.io/badge/Java-08191E?style=flat-square&logo=openjdk&logoColor=22D3EE">
<img alt="Spring Boot" src="https://img.shields.io/badge/Spring_Boot-08191E?style=flat-square&logo=springboot&logoColor=22D3EE">
<img alt="Python" src="https://img.shields.io/badge/Python-08191E?style=flat-square&logo=python&logoColor=22D3EE">

**Web**<br>
<img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-08191E?style=flat-square&logo=typescript&logoColor=22D3EE">
<img alt="Angular" src="https://img.shields.io/badge/Angular-08191E?style=flat-square&logo=angular&logoColor=22D3EE">
<img alt="React" src="https://img.shields.io/badge/React-08191E?style=flat-square&logo=react&logoColor=22D3EE">
<img alt="Next.js" src="https://img.shields.io/badge/Next.js-08191E?style=flat-square&logo=nextdotjs&logoColor=22D3EE">

**Systems**<br>
<img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-08191E?style=flat-square&logo=postgresql&logoColor=22D3EE">
<img alt="Redis" src="https://img.shields.io/badge/Redis-08191E?style=flat-square&logo=redis&logoColor=22D3EE">
<img alt="Kafka" src="https://img.shields.io/badge/Kafka-08191E?style=flat-square&logo=apachekafka&logoColor=22D3EE">
<img alt="Docker" src="https://img.shields.io/badge/Docker-08191E?style=flat-square&logo=docker&logoColor=22D3EE">
<img alt="AWS" src="https://img.shields.io/badge/AWS-08191E?style=flat-square">

## 🚀 Public projects

A selection of my public repositories, ordered by their latest push. Private work is not included.

<!-- Generated daily by .github/workflows/recent-projects.yml. To add or remove a repo, edit scripts/public-projects.json (public repos only). If the list stops updating, re-enable the workflow in the Actions tab: GitHub pauses schedules after 60 days without repo activity. -->
<!-- RECENT-PROJECTS:START -->
- **[bookie2](https://github.com/jacoboi33/bookie2)** — JavaScript · Last push: 2026-05-19
- **[riffload](https://github.com/jacoboi33/riffload)** — Python · Last push: 2026-02-24
- **[interview-prep](https://github.com/jacoboi33/interview-prep)** — HTML · Last push: 2026-02-19
- **[asteroids](https://github.com/jacoboi33/asteroids)** — asteroids game in python · Last push: 2025-01-18
- **[go-time](https://github.com/jacoboi33/go-time)** — go cli tool for tracking time · Last push: 2024-11-15
<!-- RECENT-PROJECTS:END -->

[Browse all repositories →](https://github.com/jacoboi33?tab=repositories&sort=updated)

---

<p align="center">
  <i>I’m especially interested in reliable AI-assisted development, useful automation,<br>
  and the engineering that turns a promising prototype into something people can trust.</i>
</p>
