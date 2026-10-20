---
title: University Extension Services Management System
summary: Designing a multi-role workflow and compliance platform for university extension programs.
disciplines:
  - uiux
year: 2025
technologies:
  - Figma
  - UI Design
  - Prototyping
links:
  - label: Figma
    url: https://www.figma.com/design/1gTxpORAa67VcKBpSLCD0m/ESO--Copy-?node-id=0-1&t=d7oNZmF288BKe1Aw-1
  - label: Plan
    url: https://www.figma.com/board/810YCX2EM9kgSkevRHNU7V/ESO-Planning?node-id=0-1&t=rBMQKKBP7CREi12r-1
---

## The Problem

Every extension project at the university begins as a proposal, and every proposal passes through many hands: faculty who write it, coordinators who review it, a head admin who signs it off, and Extension Services Office (ESO) staff who track it all. Before this project, that journey was hard to follow. Nobody could easily say where a proposal stood, which faculty had submitted their requirements, or how involved each college really was. During our internship, our task was to design a system that made the whole journey visible.

## The Approach

We started by mapping the process end to end, focusing on who does what and what the system should report back at each step. A faculty member drafts a proposal, classifies it as independent (outreach or faculty-initiated) or co-proponent, names the faculty involved, and uploads attachments such as scanned wet signatures. A coordinator reviews it and either approves it or asks for changes. The Head Admin gives the final approval, and that approval locks the proposal so nothing in the terminal report can be quietly edited afterward.

The map also covered the people around that main path. ESO staff manage the denominators behind involvement percentages and check submission requirements. Student organization leaders submit their own programs and participation forms in parallel. Coordinators can optionally log awards for their college.

Because the system serves five distinct roles, we treated access as a design problem in its own right. Each role gets its own tailored workspace and sees only what it needs:

- **Faculty:** Proposals, workplans, and requirement statuses.
- **Student Leaders:** Organization programs and participation forms.
- **Coordinators:** Endorsements, college awards, member change requests, and college-level reports.
- **ESO Staff:** Submission compliance checks and involvement denominators.
- **Head Admin:** Final sign-offs and university-wide analytics.

To preserve audit integrity, only coordinators can file a member modification request, which requires Research Coordinator approval and notifies the Head Admin. Approved changes are recorded transparently in the terminal report as initial versus actual details.

## The Result

Once a proposal is approved and its workplan updated, the system handles the reporting automatically. It compiles the terminal report, tracks who has and hasn't submitted requirements, and updates live metrics across partners, programs, beneficiaries, faculty and student involvement, and progress toward yearly targets.

![[Pasted image 20261019205550.png|Login Page]]

Everything starts at a unified login page. A single entry point serves all five roles, routing each user directly to the workspace built for their responsibilities.

![[Pasted image 20261020092103.png|Faculty Dashboard]]

For faculty, the dashboard immediately answers their most pressing question: *where do my proposals stand?* Drafts, active submissions, and the status of ESO requirement checks are all surfaced in one place.

![[Pasted image 20261020094813.png|Admin Dashboard]]

The admin view zooms out to the entire university. Yearly targets, college involvement percentages, and accomplishment rates are visible at a glance, right alongside proposals awaiting final approval.

![[Pasted image 20261020095132.png|Project Proposal Creation]]

The proposal form is where most of the detailed work happens. It captures the project title, timeline, target beneficiaries, category, and classification upfront so downstream reviews and automated terminal reports can rely on clean, structured data.

![[Pasted image 20261020092423.png|User Profile]]

Finally, the profile page gives every user a clean home for their account details, college affiliation, and assigned role permissions.

## After User Testing

User acceptance testing didn't end the work—it launched a post-UAT enhancement sprint shaped directly by stakeholder feedback. We refined the system to enforce one account per student organization, tightened proposal locking and member change workflows, and expanded dashboard metrics. We also designed two major additions requested during testing: a funds tracking module (PAPS) that shows whether project budgets are in accounting, budget, or payroll, and a university-wide calendar of extension activities paired with real-time notifications.

## Takeaway

This project taught us that good UI/UX starts long before any screen exists. Getting the roles, handoffs, and governance rules right made the interface intuitive to navigate—and gave the automated reports and dashboards data that stakeholders could actually trust.
