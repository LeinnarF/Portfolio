---
title: Internship Project
summary: A real-world UI/UX project developed during my internship.
disciplines:
  - uiux
  - research
year: 2024
technologies:
  - UX Research
  - UI Design
  - Prototyping
links:
  - label: Figma
    url: https://www.figma.com/design/1gTxpORAa67VcKBpSLCD0m/ESO--Copy-?node-id=0-1&t=d7oNZmF288BKe1Aw-1
  - label: Plan
    url: https://www.figma.com/board/810YCX2EM9kgSkevRHNU7V/ESO-Planning?node-id=0-1&t=rBMQKKBP7CREi12r-1
---

## The Problem

Every extension project at the university begins as a proposal, and every proposal passes through many hands: faculty who write it, coordinators who review it, a head admin who signs it off, and ESO staff who track it all. Before this project, that journey was hard to follow. Nobody could easily say where a proposal stood, which faculty had submitted their requirements, or how involved each college really was. Our internship task was to design a system that made the whole journey visible.

## The Approach

We started by mapping the process end to end, focusing on who does what and what the system should say back at each step. A faculty member drafts a proposal, classifies it as independent (outreach or faculty-initiated) or co-proponent, names the faculty involved, and uploads attachments such as scanned wet signatures. A coordinator reviews it and either approves it or asks for changes. The Head Admin gives the final approval, and that approval locks the proposal, so nothing in the terminal report can be quietly edited afterwards.

The map also covered the people around that main path. ESO staff manage the denominators behind involvement percentages and check submission requirements. Student organization leaders submit their own programs and participation forms in parallel. Coordinators can optionally log awards for their college.

Because the system serves five very different roles, We treated access as a design problem in its own right. Each role gets its own menu and sees only what it needs. Faculty see proposals and workplans. Student leaders see programs and participation forms. Coordinators see endorsements, awards and college reports. ESO staff see compliance and denominators. The Head Admin sees final approvals and university-wide analytics. Only coordinators can add awards or file a "change/modify member" request, which needs Research Coordinator approval and is reported to the Head Admin. Approved changes appear in the terminal report as initial versus actual details.

## The Result

Once a proposal is approved and its workplan updated, the system does the tedious work on its own. It compiles the terminal report and lists who has and hasn't submitted. The dashboard shows live numbers: partners, programs, beneficiaries, faculty and student involvement, and accomplishment against yearly targets.

Everything starts at the login page. One entry point serves all five roles, and the account decides what each person sees next.

![[Pasted image 20261019205550.png|Login Page]]

For faculty, the dashboard answers one question first: where do my proposals stand? Drafts, submissions and the status of ESO requirement checks are all in one place.

![[Pasted image 20261020092103.png|Faculty Dashboard]]

The admin view zooms out to the whole university. Yearly targets, involvement percentages and accomplishment rates are visible at a glance, with proposals waiting for final approval close by.

![[Pasted image 20261020094813.png|Admin Dashboard]]

The proposal form is where most of the work happens. Title, timeline, beneficiaries, category and classification are all captured here, so later review and reporting can rely on clean data.

![[Pasted image 20261020095132.png|Project Proposal Creation]]

Finally, the profile page gives each user a simple home for their account details and role information.

![[Pasted image 20261020092423.png|User Profile]]

## After User Testing

User acceptance testing didn't end the work. It sent us into a post-UAT enhancement sprint built around stakeholder requests. The sprint covered one account per student organization, proposal locking, change requests, student participation tracking, awards, and richer dashboard metrics. It also added two features stakeholders asked for: funds tracking (PAPS), which shows whether money is submitted to accounting, in budget or in payroll, and a calendar of extension activities. Notifications keep everyone current, whether that is the Head Admin hearing about an approved member change or faculty watching their requirements move from pending to submitted.

## Takeaway

This project taught us that good UI/UX starts before any screen exists. Getting the roles, the handoffs and the rules right made the interface easy to design, and it gave the reports and dashboard something reliable to display.
