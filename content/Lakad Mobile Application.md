---
title: Lakad Mobile Application
summary: A personalized travel itinerary generator and route optimizer for Bulacan.
disciplines:
  - mobile
  - uiux
  - research
technologies:
  - React-Native
  - Figma
  - Expo
  - Kotlin
  - Supabase
year: 2026
links:
  - label: GitHub
    url: https://github.com/niceWizzard/thesis-lakad-rn
  - label: Figma
    url: https://www.figma.com/design/VSL6zxCmBpNVmyVJ8L0N34/This-is-Thesis?node-id=284-2880&t=TfPgrRKF6iwPEvVX-1 
  - label: Manuscript
    url: https://github.com/LeinnarF/Thesis-LaTex
---

## The Problem

Bulacan is full of heritage sites, nature spots, and local attractions worth visiting, yet many of them stay unknown to travelers. Visitors who do come usually piece together their own trips, guessing which destinations fit together and what order makes sense on the road. Lakad began as our undergraduate thesis with a simple goal: help people discover the province and give them an optimized, ready-made plan to follow.

## The Approach

Lakad is a mobile application that builds a personalized itinerary from a traveler's preferences. Every tourist spot in the system was collected and verified in partnership with the Provincial Tourism Office, ensuring that recommendations reflect real, confirmed destinations.

Picking the spots is only half the problem—visiting all of them efficiently is a variant of the Travelling Salesman Problem. Rather than assume a single algorithm would perform best, we benchmarked several metaheuristic approaches. An **Adaptive Genetic Algorithm (AGA)** proved strongest at selecting and matching attractions to user preferences, while **Simulated Annealing (SA)** won out for optimizing the multi-stop route order. We built the cross-platform mobile client with React Native and Expo, backed by Supabase and Mapbox for interactive mapping and live turn-by-turn navigation.

## The Result

![[Pasted image 20261020103218.png|Tourist Spot Exploration|95%]]

The journey starts with discovery. Users can browse verified attractions across Bulacan by category, ratings, and location—advancing the app's broader mission of promoting local tourism.

![[Pasted image 20261020103421.png|Personalized Itinerary Generation|95%]]

When planning a trip, travelers set their interests, budget, and schedule. The Adaptive Genetic Algorithm then assembles a tailored itinerary around those constraints.

![[Pasted image 20261020103502.png|Itinerary Optimization|520]]

Once the stops are chosen, Simulated Annealing reorders the sequence to minimize travel distance and eliminate backtracking across the province.

![[Pasted image 20261020103550.png|Itinerary Navigation|520]]

On the day of the trip, integrated Mapbox navigation guides travelers from one stop to the next in real time.

![[Pasted image 20261020103634.png|Admin Dashboard and Management|95%]]

Behind the scenes, a web-based admin dashboard gives tourism staff direct control over destination listings, operating hours, and verification data.

## Evaluation

A well-designed app still has to earn its users' trust, so we evaluated Lakad from two perspectives: how everyday travelers experienced it, and how software experts judged its engineering quality.

First, users rated the app through the Technology Acceptance Model (TAM). Every construct scored in the "Highly acceptable" range, achieving a grand mean of **4.67 out of 5**. Attitude toward using the app scored highest at 4.72, while behavioral intention to use followed closely at 4.56—strong evidence that travelers found the itineraries genuinely useful for real trips.

**System Acceptability Results (TAM)**

| Construct                   | Mean Score | Standard Deviation | Interpretation    |
| --------------------------- | ---------- | ------------------ | ----------------- |
| Perceived usefulness        | 4.7053     | 0.3435             | Highly acceptable |
| Perceived ease of use       | 4.7067     | 0.4383             | Highly acceptable |
| Attitude towards using      | 4.7200     | 0.4015             | Highly acceptable |
| Behavioral intention to use | 4.5556     | 0.4740             | Highly acceptable |
| **Grand TAM Score**         | **4.6719** | **0.4189**         | **Highly acceptable** |

Second, technical evaluators assessed the system against the ISO/IEC 25010:2023 software quality standard. All nine characteristics earned "Excellent" ratings with a grand mean of **4.76 out of 5**, led by Functional Suitability (4.86), Security (4.83), and Reliability (4.82).

**System Quality Results (ISO/IEC 25010:2023)**

| Construct              | Mean Score | Standard Deviation | Interpretation |
| ---------------------- | ---------- | ------------------ | -------------- |
| Functional Suitability | 4.8636     | 0.2447             | Excellent      |
| Performance Efficiency | 4.7727     | 0.3902             | Excellent      |
| Compatibility          | 4.6591     | 0.4973             | Excellent      |
| Interaction Capability | 4.7614     | 0.2642             | Excellent      |
| Reliability            | 4.8182     | 0.3634             | Excellent      |
| Security               | 4.8258     | 0.3190             | Excellent      |
| Maintainability        | 4.6818     | 0.3187             | Excellent      |
| Flexibility            | 4.7500     | 0.3086             | Excellent      |
| Safety                 | 4.7455     | 0.4501             | Excellent      |
| **Grand ISO/IEC 25010:2023 Score** | **4.7642** | **0.3575** | **Excellent** |

## Recognition & Takeaway

Pairing verified local tourism data with metaheuristic optimization turned a theoretical computer science problem into a practical travel companion—and earned Lakad **Best Thesis Runner-Up** in our college.
