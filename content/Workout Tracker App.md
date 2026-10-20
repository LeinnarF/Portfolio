---
title: Workout Tracker App
summary: An offline-first mobile app for logging workouts, double-progression overload, and strength analytics.
disciplines:
  - mobile
  - uiux
technologies:
  - Expo
  - React-Native
  - TypeScript
  - SQLite
year: 2026
links: 
  - label: GitHub
    url: https://github.com/LeinnarF/Workout-Tracker-App
  - label: Download
    url: https://github.com/LeinnarF/Workout-Tracker-App/releases
---

## The Problem

Most workout trackers ask for an account, a recurring subscription, or a steady internet connection. Gyms often have spotty signal, and logging a set between heavy lifts should take seconds—not a loading spinner or a login screen. I wanted a fast, distraction-free tracker that works completely offline, automates progressive overload math, and keeps all training data strictly on my own phone.

## The Approach

Workout Tracker is a **100% offline-first** mobile app built with **Expo (React Native)** and **TypeScript**. Every workout, set, and personal record lives in an on-device **SQLite** database (`expo-sqlite`), requiring zero network access, accounts, or cloud sync. File-based navigation runs on Expo Router, progression charts use `react-native-gifted-charts`, and the custom rest timer dial is rendered with `react-native-svg`.

At the heart of the app is **double progression**. Instead of guessing when to add weight, you train within a target rep range (such as 5 to 10 reps). Once every working set in a session reaches the top of that range, the app automatically prompts a weight increase (for example, `+5 lb`). Accepting the prompt with a single tap updates the exercise's default working weight for the next session.

| Layer | Choice |
| --- | --- |
| Framework | Expo SDK 57, React Native 0.86, TypeScript |
| Routing | Expo Router (file-based navigation) |
| Storage | `expo-sqlite` (on-device persistent database) |
| Charts & Graphics | `react-native-gifted-charts`, `react-native-svg` |
| Feedback & Device | `expo-audio`, `expo-haptics`, `expo-keep-awake` |
| Portability | `expo-file-system`, `expo-sharing` |

## The Result

![[Pasted image 20261020134050.png|Workout Logging|20%]]

The Log tab is where lifters spend most of their time, so every tap is minimized. Exercises sit in a clean accordion layout tagged by movement category (Upper, Lower, Core, Push, Pull, Legs). Working weights prefill automatically from the previous session, and target set limits prevent accidental over-logging by marking completed lifts with a clear "Done" badge. Hitting the top of a rep range across all sets triggers a one-tap overload prompt, while long-pressing any exercise opens quick controls to adjust target sets, rep ranges, weight increments, or archive status.

![[Pasted image 20261020134141.png|Rest Timer|20%]]

Between sets, the Rest Timer pairs a high-contrast vector progress dial with clear state indicators (`READY`, `RESTING`, `PAUSED`). One-tap presets from `30s` to `3:00` handle standard rest intervals, alongside custom minute and second inputs for specialized programming. A shared timer context keeps the countdown running across tabs, prevents the screen from sleeping, and fires an audio chime and haptic pulse the moment rest is over.

![[Pasted image 20261020134218.png|Weight Converter|20%]]

Because gyms often mix pound and kilogram equipment, the Convert tab translates weights in both directions in real time. Its built-in plate calculator breaks down exactly which plates to load on each side of the bar, paired with quick presets for common barbell milestones and dumbbell racks so you never have to do plate math between sets.

![[Pasted image 20261020134301.png|Progress Tracker|20%]]

The Stats tab turns raw set logs into clear feedback across three views: Overview, Charts, and History. Overview surfaces lifetime volume and set totals, a weekly consistency streak, a Progression Radar showing which lifts are ready for a weight jump, and a Personal Records trophy case. Charts filter by exercise and timeframe (`4W`, `3M`, `1Y`, `All Time`) to plot weekly rep volume, estimated 1-Rep Max trends via the Epley formula, and session workload. History organizes completed workouts by calendar date with concise rep breakdowns and top weights.

## Takeaway

Keeping the app strictly offline simplified the architecture while making the user experience noticeably faster on the gym floor. Separating pure domain logic—unit conversion, 1RM estimation, and double-progression rules in `src/logic`—from the SQLite query layer in `src/db` and reusable UI primitives in `src/components/ui` kept the codebase modular and easy to extend. And because owning your data matters, built-in JSON snapshots and CSV exports ensure lifters can back up their history or analyze their training in external tools anytime.
