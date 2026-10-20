/**
 * Portfolio Minimalist Interactions
 * - Clean digital glitch & role scramble
 * - Live local time in Hero meta row
 * - Minimalist discipline filtering for project index
 * - Scroll reveal animation (IntersectionObserver)
 */

document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();
    initCleanGlitchFlicker();
    initLocalTime();
    initProjectFiltering();
    initScrollReveal();
});

/* =========================================
   1. CLEAN DIGITAL GLITCH & ROLE SCRAMBLE
   ========================================= */

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
            "Data Scientist",
            "UI/UX Designer",
            "Mobile Developer",
            "Researcher",
            "Mathematician",
        ];
    }

    const GLYPHS = "!<>-_\\/[]{}—=+*^?#0123456789";
    const SCRAMBLE_TIME = 200; // Fast digital glitch duration (ms)
    const FRAME_RATE = 25;     // Tick rate (ms)

    let currentIndex = 0;

    function randomGlyph() {
        return GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
    }

    function getRandomReadingDuration() {
        return Math.floor(Math.random() * (1600 - 600 + 1)) + 600;
    }

    function updatePrefix(role) {
        if (!prefixEl) return;
        const firstLetter = role.trim()[0]?.toLowerCase();
        const isVowel = ["a", "e", "i", "o", "u"].includes(firstLetter);
        prefixEl.textContent = isVowel ? "I'm an" : "I'm a";
    }

    function glitchScrambleTo(targetText, onComplete) {
        updatePrefix(targetText);

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

    updatePrefix(roles[0]);
    flickerEl.textContent = roles[0];
    setTimeout(cycleNext, getRandomReadingDuration());
}

/* =========================================
   2. LIVE LOCAL TIME
   ========================================= */

function initLocalTime() {
    const timeEl = document.getElementById("local-time");
    if (!timeEl) return;

    const timezone = timeEl.dataset.timezone || "Asia/Manila";

    function updateTime() {
        try {
            const now = new Date();
            const formatter = new Intl.DateTimeFormat("en-US", {
                timeZone: timezone,
                hour: "2-digit",
                minute: "2-digit",
                hour12: false,
            });
            timeEl.textContent = `${formatter.format(now)} local time`;
        } catch (e) {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, "0");
            const mins = String(now.getMinutes()).padStart(2, "0");
            timeEl.textContent = `${hours}:${mins} local time`;
        }
    }

    updateTime();
    setInterval(updateTime, 10000);
}

/* =========================================
   3. DISCIPLINE FILTERING
   ========================================= */

function initProjectFiltering() {
    const filterContainers = document.querySelectorAll("#project-filters");
    if (!filterContainers.length) return;

    filterContainers.forEach((filters) => {
        const buttons = filters.querySelectorAll(".filter-btn");
        const list = filters.closest(".container")?.querySelector(".project-list");
        if (!list) return;

        const rows = list.querySelectorAll(".project-row");

        buttons.forEach((btn) => {
            btn.addEventListener("click", () => {
                const filter = btn.dataset.filter;

                buttons.forEach((b) => {
                    b.classList.remove("active");
                    b.setAttribute("aria-selected", "false");
                });
                btn.classList.add("active");
                btn.setAttribute("aria-selected", "true");

                let visibleCount = 1;
                rows.forEach((row) => {
                    const rowDisciplines = (row.dataset.disciplines || "").split(" ").filter(Boolean);
                    const isMatch = filter === "all" || rowDisciplines.includes(filter);

                    if (isMatch) {
                        row.style.display = "";
                        const numEl = row.querySelector(".row-num");
                        if (numEl) {
                            numEl.textContent = String(visibleCount).padStart(2, "0");
                        }
                        visibleCount++;
                    } else {
                        row.style.display = "none";
                    }
                });
            });
        });
    });
}

/* =========================================
   4. SCROLL REVEAL ANIMATION
   ========================================= */

function initScrollReveal() {
    const revealEls = document.querySelectorAll(".reveal-on-scroll");
    if (!revealEls.length) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-revealed");
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.08,
            rootMargin: "0px 0px -30px 0px",
        }
    );

    revealEls.forEach((el) => observer.observe(el));
}

/* =========================================
   5. LIGHT / DARK THEME TOGGLE
   ========================================= */

function initThemeToggle() {
    const toggleBtn = document.getElementById("theme-toggle");
    if (!toggleBtn) return;

    toggleBtn.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", newTheme);
        try {
            localStorage.setItem("theme", newTheme);
        } catch (e) {}
    });
}
