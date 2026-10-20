---
title: Pokédex Desktop Application
summary: A JavaFX desktop information system modeled around Pokémon data.
disciplines:
  - uiux
  - development
technologies:
  - Java
  - JavaFX
  - Figma
year: 2024
links: 
  - label: GitHub
    url: https://github.com/niceWizzard/PokedexxFX
  - label: Figma
    url: https://www.figma.com/design/tjZOKKif0F1oMEBPxKjFfE/Comprog3-team-library?node-id=0-1&p=f&t=jLxGneyjssMqs0uo-0
---

## The Problem

For our final project in Computer Programming III during second year of college, the assignment was to build an information system in Java. Most classroom information systems default to standard business record management, which often feels dry and mechanical. We realized that a Pokédex is fundamentally an information system—one that stores, organizes, and retrieves structured data for hundreds of entries. Choosing a Pokédex gave us a creative domain to explore object-oriented programming while taking on our first real software project.

## The Approach

Because this was the first application we ever built, we used the project to practice core object-oriented principles from the ground up. Each Pokémon is modeled as an object with distinct attributes, including identification numbers, dual types, physical measurements, and lore text. 

Before writing code, we designed the user interface components in Figma, mapping out a split-screen desktop layout to separate browsing from inspection. We then built the application in Java using JavaFX for the user interface. Color-coded card components match the primary elemental types—green for grass, orange for fire, and blue for water—giving users immediate visual feedback as they navigate through the roster.

## The Result

The completed application provides a responsive desktop directory where users can search, browse, and inspect individual Pokémon entries.

![[Pasted image 20261020132206.png|Pokedex Desktop Application Interface|85%]]

The left sidebar displays a scrollable index of Pokémon cards with their National Pokédex number, name, pixel sprite, and type coloring. Selecting a card updates the main panel with high-resolution artwork, height, weight, and elemental badges. A tabbed panel below the details separates lore descriptions, evolution paths, and base statistics into distinct views, keeping the interface uncluttered while allowing easy exploration.

## Takeaway

Building our first application demonstrated how object-oriented concepts like encapsulation and class hierarchies translate into clean, working software. Prototyping the interface in Figma before implementation proved essential, as having established layout and component boundaries made the JavaFX code straightforward to structure and style.
