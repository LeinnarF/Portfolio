---
title: Lakad Mobile Application
summary: A mobile personalized itinerary generator for Bulacan
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
year: 2025
links:
  - label: Github
    url: https://github.com/niceWizzard/thesis-lakad-rn
  - label: Figma
    url: https://www.figma.com/design/VSL6zxCmBpNVmyVJ8L0N34/This-is-Thesis?node-id=284-2880&t=TfPgrRKF6iwPEvVX-1 
  - label: Manuscript
    url: https://github.com/LeinnarF/Thesis-LaTex
---
## The Problem

Bulacan is full of places worth visiting, yet many of them stay unknown to tourists. Visitors who do come usually plan their own trip, guessing which spots fit together and which order makes sense. Lakad began as our undergraduate thesis, with a simple goal: help people discover the province and give them a ready-made plan to follow.

## The Approach

Lakad is a mobile app that builds a personalized itinerary from the user's preferences. The tourist spot data was collected and verified with the Provincial Tourism Office, so the app recommends real, confirmed places. Picking the spots is only half the job. Visiting all of them efficiently is a Travelling Salesman Problem, so we used that as the framework for finding the best route.

Rather than assume one algorithm would work best, we evaluated several metaheuristic algorithms. An adaptive genetic algorithm turned out best for generating the itinerary itself. For route optimization, simulated annealing won on the evaluation results. The app is built with React Native and Expo, and Mapbox provides the maps and live navigation.

![[Pasted image 20261020103218.png|Tourist Spot Exploration|95%]]

## The Result

Users begin by exploring tourist spots, which also serves the app's aim of promoting the province.

![[Pasted image 20261020103421.png|Personalized Itinerary Generation|95%]]

Then they tell the app what they like, and it generates an itinerary around those preferences.

![[Pasted image 20261020103502.png|Itinerary Optimization|520]]

Next, the route is optimized so every stop is visited in an efficient order, without backtracking across the province.

![[Pasted image 20261020103550.png|Itinerary Navigation|520]]

On the day of the trip, live navigation guides travelers from one stop to the next.

![[Pasted image 20261020103634.png|Admin Dashboard and Management|95%]]

Behind the scenes, an admin dashboard lets tourism staff manage the spots and data the app relies on.

## Evaluation

A good-looking app still has to earn its users' trust, so we evaluated Lakad from two angles: how users felt about it, and how well it was built.

First, users rated the app using the Technology Acceptance Model (TAM). Every construct scored in the "Highly acceptable" range, with a grand mean of 4.6719 out of 5. Attitude towards using the app scored highest at 4.7200. Behavioral intention to use scored lowest, though still high at 4.5556, which suggests people liked the app and would likely keep using it.

**System Acceptability Results (TAM)**

| Construct                   | Mean Score | Standard Deviation | Interpretation    |
| --------------------------- | ---------- | ------------------ | ----------------- |
| Perceived usefulness        | 4.7053     | 0.3435             | Highly acceptable |
| Perceived ease of use       | 4.7067     | 0.4383             | Highly acceptable |
| Attitude towards using      | 4.7200     | 0.4015             | Highly acceptable |
| Behavioral intention to use | 4.5556     | 0.4740             | Highly acceptable |
| **Grand TAM Score**         | **4.6719** | **0.4189**         | **Highly acceptable** |

Second, experts assessed the system against the ISO/IEC 25010:2023 quality model. All nine characteristics were rated "Excellent", with a grand mean of 4.7642. Functional suitability scored highest at 4.8636, so the app does what it promises. Security (4.8258) and reliability (4.8182) also scored very high. Compatibility was the lowest at 4.6591, still well within the excellent range.

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

## Recognition

These results backed up the panel's confidence in the work. Lakad was named Best Thesis Runner-Up in our college.
