/**
 * Clean Digital Glitch & Role Scramble
 * Features:
 * - Clean, cohesive typography in the site's accent color
 * - Snappy digital hacker/glitch scramble during transitions
 * - Crisp, steady, perfectly readable settled text
 * - Random reading duration between 0.5s and 1.5s
 */

document.addEventListener("DOMContentLoaded", () => {
    initCleanGlitchFlicker();
});

function initCleanGlitchFlicker() {
    const flickerEl = document.getElementById("role-flicker");
    const prefixEl = document.getElementById("role-prefix");

    if (!flickerEl) return;

    let roles = [];
    try {
        roles = JSON.parse(flickerEl.dataset.roles || "[]");
    } catch (e) {
        roles = [];
    }

    if (!roles || roles.length === 0) {
        roles = [
            "Data Analyst",
            "Data Scientist",
            "Mathematician",
            "Programmer",
            "Game Developer",
        ];
    }

    const GLYPHS = "!<>-_\\/[]{}—=+*^?#0123456789";
    const SCRAMBLE_TIME = 200; // Fast and snappy digital glitch duration (ms)
    const FRAME_RATE = 25;     // Tick rate (ms)

    let currentIndex = 0;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function randomGlyph() {
        return GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
    }

    function getRandomReadingDuration() {
        // Random reading pause between 0.5s (500ms) and 1.5s (1500ms)
        return Math.floor(Math.random() * (1500 - 500 + 1)) + 500;
    }

    function updatePrefix(role) {
        if (!prefixEl) return;
        const firstLetter = role.trim()[0]?.toLowerCase();
        const isVowel = ["a", "e", "i", "o", "u"].includes(firstLetter);
        prefixEl.textContent = isVowel ? "I'm an" : "I'm a";
    }

    function glitchScrambleTo(targetText, onComplete) {
        updatePrefix(targetText);

        if (prefersReducedMotion) {
            flickerEl.textContent = targetText;
            onComplete();
            return;
        }

        const totalFrames = Math.max(1, Math.floor(SCRAMBLE_TIME / FRAME_RATE));
        let frame = 0;

        const interval = setInterval(() => {
            frame++;
            const progress = frame / totalFrames;
            const lockedCount = Math.floor(progress * targetText.length);

            let html = "";
            for (let i = 0; i < targetText.length; i++) {
                const char = targetText[i];
                if (char === " ") {
                    html += " ";
                } else if (i < lockedCount) {
                    html += char;
                } else {
                    html += `<span class="glitch-noise">${randomGlyph()}</span>`;
                }
            }

            flickerEl.innerHTML = html;

            if (frame >= totalFrames) {
                clearInterval(interval);
                // Settle into crisp, clean text
                flickerEl.textContent = targetText;
                onComplete();
            }
        }, FRAME_RATE);
    }

    function cycleNext() {
        currentIndex = (currentIndex + 1) % roles.length;
        const nextRole = roles[currentIndex];

        glitchScrambleTo(nextRole, () => {
            setTimeout(cycleNext, getRandomReadingDuration());
        });
    }

    // Initialize first role cleanly
    updatePrefix(roles[0]);
    flickerEl.textContent = roles[0];

    // Start cycling with a random reading pause (0.5s - 1.5s)
    setTimeout(cycleNext, getRandomReadingDuration());
}
