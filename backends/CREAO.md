
Hack with CREAO @ CalHacks 12.0

Hack with CREAO

October 24 - 26

2025

The Palace of Fine Arts

3601 Lyon St, San Francisco, CA

Register Challenge

Join Discord

At CREAO, we believe in empowering creativity through technology, community, and collaboration. We're proud to sponsor CalHacks 12.0 and bring positive energy to the next generation of builders.

We’re proudly sponsoring CalHacks 12.0


About the Event
We are Creao AI, a vibe coding platform that provides AI-native webapps. What does that mean? You can use your everyday language to ask our platform to create a webapp or a system for you. Creao implements the front end, back end, and database for you so you don’t have to worry about system architecture problems. 



We call our webapps AI native because each one has an in-house AI agent that understands the entire implementation and helps you complete repetitive tasks instantly. Besides allowing other AI tools to be incorporated into Creao, Creao itself can also be integrated into other AI tools like Anthropic Claude, making it truly bidirectional. 



At Creao, we believe AI should be easy to use and easy to share, empowering creativity and productivity. We also believe in community support and are committed to making the world a better place. Join our CalHacks challenge, create something cool, and make an impact together.  

Challenge Statement
At CalHacks 12.0, we’re calling on hackers to build projects that create real impact. This challenge is about creativity, usability, and integration. Design a system that improves lives, simplifies workflows, or inspires new ways to use AI.



Since Creao AI is a vibe-coding platform, we’re especially looking for how you use integrations in your project. Whether you build a custom API or Model Context Protocol (MCP), your project must include at least one custom integration that connects components into a functional system.



Check out our prizes below and choose the scope you want to tackle. Clearly define your project, explain what integration you’ve built, and describe the problem you’re solving.



To participate, click “Register Challenge” on our page to receive your invitation code for a Pro account upgrade. Once your project is complete, submit it through the official Creao Challenge Submission Form to be considered for judging.



If you have any questions, message us on Slack at #spons-creao.

Register Challenge

Get Invitation Code & Join CREAO

Start Building

Submit Challenge

Go

Go


Best Real-World Productivity Tool 

Awarded to the most practical and impactful system that improves productivity in everyday life or within an industry.

1

1,750 USD

1-year Pro subscription

Potential internship opportunity

2

Best Custom Build

Awarded to the team that pushes the limits of customization through unique logic, complex API workflows, or creative agentic systems.

1,250 USD

1-year Pro subscription

Potential internship opportunity

Best Designed Web App 

Awarded to the project with the most polished, intuitive, and user-friendly design that delivers an exceptional user experience.

3

1,000 USD

1-year Pro subscription

Bring your best ideas, integrate creatively, 

and build something that makes the world a better place.

Prize
Schedule
Friday, 

October 24

Hackers Enter Venue

14：00 PDT

Opening Ceremony

16：00 PDT

@ Main Stage

Hacking Begins

18：00 PDT

Saturday, 

October 25

Workshop

Build and Host Your Own API/Agent on CREAO

10：00 - 11:00 PDT

@ DOE Workshop Room

Networking

Come Learn About Creao AI and ‘Yoga’ With Us

15：00 - 17:00 PDT

@ Bancroft Workshop Room

Booth Open

9：00 - 17:00 PDT

Sunday, 

October 26

Final Project Submissions Due

10：30 PDT

Judging

10：30 - 12：30 PDT

Closing Ceremony / Tech Prize Presentation

13：00 - 15:00 PDT

@ Main Stage

Tech Stack
Build Agent

S3

Rollout Service

Render Layer

Biz Layer

Data Access Layer

FrontEnd

Schema Registry

Data Store

Data Service

Permission Registry

Identity Judge

Access Control

Schema Registry

Proxy Servie

API & MCP Service

Documentation & Important Links
Welcome to Creao

MCP & API Explained 

MCP Integration

Custom MCP Integration

API Integration

Import Figma Design

Judging Rubric
SUBMISSION GUIDELINES

All projects must be built during the hackathon (Oct 24–26, 2025) and must include at least one custom registered API on the Creao platform to be eligible for judging.

Teams should assemble their APIs into a working system and provide a short demo or explanation of functionality. Each project may compete in only one Creao prize track and have up to 4 members.

After submitting their projects, teams must complete a short form with their team name, member names, brief project description, project link, and selected prize category. 

Judging categories

IMPACT

0-30 POINTS

Does the project solve a meaningful, real-world problem? Who benefits?

Problem trivial or unclear 

0-10 Pt

Relevant but limited scope

11-20 Pt

Well-defined, urgent, high impact

21-30 Pt

CREATIVITY & INNOVATION

0-25 POINTS

How original or unique is the approach? Are APIs used in unexpected ways?

Predictable/standard

0-8 Pt

Some unique features

9-16 Pt

Bold, original, highly innovative

17-25 Pt

TECHNICAL EXCUTION

0-25 POINTS

Are APIs functional, integrated smoothly, and demo-ready?

Incomplete/non-functional

0-8 Pt

Basic functionality

9-16 Pt

Polished, strong technical foundation

17-25 Pt

SCALABILITY & SUSTAINABILITY

0-10 POINTS

Could the system grow beyond the hackathon into a real-world application?

Some potential with improvements

4-7 Pt

No potential beyond demo

0–3 Pt

Strong scalability and real-world viability

8-10 Pt

PRESENTATION & DEMO

0-10 POINTS

Was the project clearly presented with a smooth demo showing Creao integration?

Unclear explanation, weak demo

4-7 Pt

Adequate explanation, functional demo

0–3 Pt

Clear, engaging presentation and effective demo

8-10 Pt

Submit Challenge

Judging Headshot
Judge & Mentor


Peter

CTO


Henry

Member of Technical Staff


Joshua

Member of Technical Staff

Eric

Member of Technical Staff

Judge


Charis

Member of 

Technical Staff


Rachel

Member of Technical Staff


Haiming

Member of 

Technical Staff


Avinash

Member of 

Technical Staff

Come and Meet with us

© 2025 Creao AI. All rights reserved

Privacy policy

Terms & Conditions


---

## ✅ Integration Plan: AI Task MCP Server

To satisfy the Creao challenge requirement for a custom integration, we expose our FastAPI backend through a **Model Context Protocol (MCP)** server implemented with `fastmcp`. This lets Creao (or any MCP-aware agent) call the same task-planning APIs without bespoke HTTP glue.

### Capabilities
- `ai_generate` — invoke Claude via OpenRouter, optionally persisting a full task tree.
- `create_todo`, `list_todos`, `update_todo`, `delete_todo` — full CRUD with filters identical to `/todos`.
- `todo_tree` — fetch hierarchical tasks for rendering.
- `memory_search` — surface semantic matches via ChromaDB.
- `health` — lightweight readiness check.
- Resources: `creao://docs/api` (REST contract) and `creao://docs/creao-challenge` (this brief) for in-agent reference.

### Running the MCP Bridge
From `backends/`:
```bash
uv run python app/mcp_server.py --transport stdio
# or expose via HTTP/SSE
uv run python app/mcp_server.py --transport http --host 127.0.0.1 --port 8766
```

Then call `http://127.0.0.1:8766/mcp` with JSON-RPC payloads, `Content-Type: application/json`, and `Accept: application/json, text/event-stream`. See `docs/MCPGuide.md` for detailed instructions.

This server can be registered inside Creao or any MCP-compatible orchestrator, enabling future AI agents to compose actions (e.g., auto-prioritize tasks, trigger Godot webhooks) using the same tool vocabulary the game already understands.

When we later add autonomous agents, they simply connect over MCP and reuse these tools—no new API plumbing required.
