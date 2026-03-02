const RESUME_DATA_PATH = "./assets/resume-data.json";

const ICONS = {
    email: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 7.5h18v9H3z"></path><path d="m3 8 9 6 9-6"></path></svg>',
    github: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5A12 12 0 0 0 8.2 24c.6.1.8-.3.8-.6v-2.2c-3.3.7-4-1.4-4-1.4-.6-1.4-1.3-1.8-1.3-1.8-1.1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 .1.8 2.9 3.6 2.1.1-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-6A4.8 4.8 0 0 1 5.5 9c-.1-.3-.6-1.6.1-3.4 0 0 1-.3 3.5 1.3a12 12 0 0 1 6.3 0c2.4-1.6 3.5-1.3 3.5-1.3.7 1.8.2 3.1.1 3.4a4.8 4.8 0 0 1 1.3 3.3c0 4.7-2.8 5.7-5.5 6 .4.3.8 1.1.8 2.2v3.2c0 .3.2.7.8.6A12 12 0 0 0 12 .5"/></svg>',
    link: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m10 13 4-4"></path><path d="M7.9 16.1a3 3 0 0 1 0-4.2l2-2a3 3 0 0 1 4.2 0"></path><path d="M16.1 7.9a3 3 0 0 1 0 4.2l-2 2a3 3 0 0 1-4.2 0"></path></svg>',
};

function hasText(value) {
    return typeof value === "string" && value.trim().length > 0;
}

function escapeHtml(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function toggleVisibility(el, visible) {
    if (!el) return;
    el.classList.toggle("is-hidden", !visible);
}

function appendStateText(message) {
    const p = document.createElement("p");
    p.className = "state-text";
    p.textContent = message;
    document.body.appendChild(p);
}

function buildLinkHtml(link) {
    const label = hasText(link.label) ? link.label.trim() : "链接";
    const url = hasText(link.url) ? link.url.trim() : "";
    if (!url) return "";

    const type = hasText(link.type) ? link.type.trim().toLowerCase() : "link";
    const icon = ICONS[type] || ICONS.link;

    return `
        <a class="social-link" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">
            <span>${icon}</span>
            <span>${escapeHtml(label)}</span>
        </a>
    `;
}

function buildBaseInfo(profile) {
    const list = [profile.location, profile.phone].filter(hasText);
    return list.map((item) => `<span>${escapeHtml(item.trim())}</span>`).join("");
}

function renderProfile(profile) {
    document.title = `个人简历 | ${hasText(profile.name) ? profile.name.trim() : "候选人"}`;

    const userName = document.getElementById("user-name");
    const userTitle = document.getElementById("user-title");
    const socialLinks = document.getElementById("social-links");
    const baseInfo = document.getElementById("base-info");
    const avatarWrap = document.getElementById("avatar-wrap");
    const avatar = document.getElementById("avatar");

    userName.textContent = hasText(profile.name) ? profile.name.trim() : "未命名简历";
    userTitle.textContent = hasText(profile.headline) ? profile.headline.trim() : "";

    const links = Array.isArray(profile.links) ? profile.links : [];
    socialLinks.innerHTML = links.map(buildLinkHtml).join("");
    toggleVisibility(socialLinks, links.length > 0);

    baseInfo.innerHTML = buildBaseInfo(profile);
    toggleVisibility(baseInfo, hasText(baseInfo.textContent));

    const avatarUrl = hasText(profile.avatar) ? profile.avatar.trim() : "";
    if (avatarUrl) {
        avatar.src = avatarUrl;
        toggleVisibility(avatarWrap, true);
    } else {
        toggleVisibility(avatarWrap, false);
    }

    const bg = hasText(profile.backgroundImage) ? profile.backgroundImage.trim() : "./assets/background.webp";
    document.body.style.backgroundImage =
        `linear-gradient(rgba(15, 23, 42, 0.32), rgba(15, 23, 42, 0.32)), url('${bg}')`;
}

function renderSummary(summary) {
    const section = document.getElementById("section-summary");
    if (!summary || !hasText(summary.content)) {
        toggleVisibility(section, false);
        return;
    }

    document.getElementById("summary-title").textContent = hasText(summary.title) ? summary.title.trim() : "专业技能";
    document.getElementById("summary-content").innerHTML = summary.content;
    toggleVisibility(section, true);
}

function renderExperience(containerId, sectionId, titleId, section, fallbackTitle = "工作经历") {
    const sectionEl = document.getElementById(sectionId);
    if (!section || !Array.isArray(section.items) || section.items.length === 0) {
        toggleVisibility(sectionEl, false);
        return;
    }

    document.getElementById(titleId).textContent = hasText(section.title) ? section.title.trim() : fallbackTitle;

    const html = section.items
        .map((item) => {
            const title = hasText(item.company) ? item.company : "未命名";
            const role = hasText(item.role) ? `<p class="card-subtitle">${escapeHtml(item.role)}</p>` : "";
            const period = hasText(item.period) ? `<span class="card-time">${escapeHtml(item.period)}</span>` : "";
            const description = hasText(item.description) ? `<div class="card-desc">${item.description}</div>` : "";

            const meta = [
                hasText(item.location) ? item.location.trim() : "",
                item.website && hasText(item.website.url)
                    ? `<a href="${escapeHtml(item.website.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.website.label || item.website.url)}</a>`
                    : "",
            ].filter(Boolean);

            return `
                <article class="card">
                    <div class="card-head">
                        <h3 class="card-title">${escapeHtml(title)}</h3>
                        ${period}
                    </div>
                    ${role}
                    ${description}
                    ${meta.length > 0 ? `<p class="card-meta">${meta.join(" · ")}</p>` : ""}
                </article>
            `;
        })
        .join("");

    document.getElementById(containerId).innerHTML = html;
    toggleVisibility(sectionEl, true);
}

function renderProjects(section) {
    const sectionEl = document.getElementById("section-projects");
    if (!section || !Array.isArray(section.items) || section.items.length === 0) {
        toggleVisibility(sectionEl, false);
        return;
    }

    document.getElementById("projects-title").textContent = hasText(section.title) ? section.title.trim() : "项目经历";

    const html = section.items
        .map((item) => {
            const name = hasText(item.name) ? item.name.trim() : "未命名项目";
            const period = hasText(item.period) ? `<span class="card-time">${escapeHtml(item.period)}</span>` : "";
            const description = hasText(item.description) ? `<div class="card-desc">${item.description}</div>` : "";
            const website = item.website && hasText(item.website.url)
                ? `<p class="card-meta"><a href="${escapeHtml(item.website.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.website.label || item.website.url)}</a></p>`
                : "";

            return `
                <article class="card">
                    <div class="card-head">
                        <h3 class="card-title">${escapeHtml(name)}</h3>
                        ${period}
                    </div>
                    ${description}
                    ${website}
                </article>
            `;
        })
        .join("");

    document.getElementById("projects-container").innerHTML = html;
    toggleVisibility(sectionEl, true);
}

function renderCertifications(certifications, awards) {
    const sectionEl = document.getElementById("section-certs");
    const certItems = certifications && Array.isArray(certifications.items) ? certifications.items : [];
    const awardItems = awards && Array.isArray(awards.items) ? awards.items : [];
    const items = [...certItems, ...awardItems];

    if (items.length === 0) {
        toggleVisibility(sectionEl, false);
        return;
    }

    const title = hasText(certifications?.title) ? certifications.title.trim() : "荣誉与专利";
    document.getElementById("certs-title").textContent = title;

    const html = items
        .map((item) => {
            const titleText = hasText(item.title) ? item.title.trim() : "未命名";
            const right = [item.issuer, item.date].filter(hasText).map((v) => escapeHtml(v.trim())).join(" · ");
            const desc = hasText(item.description) ? `<div class="card-desc">${item.description}</div>` : "";
            const website = item.website && hasText(item.website.url)
                ? `<p class="card-meta"><a href="${escapeHtml(item.website.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.website.label || item.website.url)}</a></p>`
                : "";

            return `
                <article class="card">
                    <div class="card-head">
                        <h3 class="card-title">${escapeHtml(titleText)}</h3>
                        ${right ? `<span class="card-time">${right}</span>` : ""}
                    </div>
                    ${desc}
                    ${website}
                </article>
            `;
        })
        .join("");

    document.getElementById("certs-container").innerHTML = html;
    toggleVisibility(sectionEl, true);
}

function renderEducation(section) {
    const sectionEl = document.getElementById("section-education");
    if (!section || !Array.isArray(section.items) || section.items.length === 0) {
        toggleVisibility(sectionEl, false);
        return;
    }

    document.getElementById("education-title").textContent = hasText(section.title) ? section.title.trim() : "教育经历";

    const html = section.items
        .map((item) => {
            const school = hasText(item.school) ? item.school.trim() : "未命名学校";
            const degree = hasText(item.degreeArea) ? item.degreeArea.trim() : "";
            const period = hasText(item.period) ? `<span class="card-time">${escapeHtml(item.period.trim())}</span>` : "";
            const desc = hasText(item.description) ? `<div class="card-desc">${item.description}</div>` : "";

            const meta = [
                hasText(item.location) ? item.location.trim() : "",
                item.website && hasText(item.website.url)
                    ? `<a href="${escapeHtml(item.website.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.website.label || item.website.url)}</a>`
                    : "",
            ].filter(Boolean);

            return `
                <article class="card">
                    <div class="card-head">
                        <h3 class="card-title">${escapeHtml(school)}</h3>
                        ${period}
                    </div>
                    ${degree ? `<p class="card-subtitle">${escapeHtml(degree)}</p>` : ""}
                    ${desc}
                    ${meta.length > 0 ? `<p class="card-meta">${meta.join(" · ")}</p>` : ""}
                </article>
            `;
        })
        .join("");

    document.getElementById("education-container").innerHTML = html;
    toggleVisibility(sectionEl, true);
}

function renderCustomSections(customSections) {
    const sectionEl = document.getElementById("section-custom");
    if (!Array.isArray(customSections) || customSections.length === 0) {
        toggleVisibility(sectionEl, false);
        return;
    }

    const html = customSections
        .map((section) => {
            const title = hasText(section.title) ? section.title.trim() : "补充经历";
            if (!Array.isArray(section.items) || section.items.length === 0) return "";

            if (section.type === "experience") {
                const cards = section.items
                    .map((item) => {
                        const company = hasText(item.company) ? item.company.trim() : "未命名";
                        const role = hasText(item.role) ? `<p class="card-subtitle">${escapeHtml(item.role)}</p>` : "";
                        const desc = hasText(item.description) ? `<div class="card-desc">${item.description}</div>` : "";
                        return `
                            <article class="card">
                                <h4 class="card-title">${escapeHtml(company)}</h4>
                                ${role}
                                ${desc}
                            </article>
                        `;
                    })
                    .join("");

                return `
                    <section class="card">
                        <h3 class="card-title">${escapeHtml(title)}</h3>
                        <div class="stack">${cards}</div>
                    </section>
                `;
            }

            return "";
        })
        .join("");

    document.getElementById("custom-sections").innerHTML = html;
    toggleVisibility(sectionEl, hasText(document.getElementById("custom-sections").textContent));
}

function renderFooter(footer) {
    document.getElementById("footer-copy").textContent = hasText(footer?.copy) ? footer.copy.trim() : "";
    document.getElementById("footer-quote").textContent = hasText(footer?.quote) ? footer.quote.trim() : "";
    toggleVisibility(document.getElementById("footer-quote"), hasText(footer?.quote));
}

function renderResume(resumeData) {
    renderProfile(resumeData.profile || {});
    renderSummary(resumeData.summary);
    renderExperience("experience-container", "section-experience", "experience-title", resumeData.experience, "工作经历");
    renderProjects(resumeData.projects);
    renderCertifications(resumeData.certifications, resumeData.awards);
    renderEducation(resumeData.education);
    renderCustomSections(resumeData.customSections);
    renderFooter(resumeData.footer || {});
}

async function init() {
    try {
        const response = await fetch(RESUME_DATA_PATH, { cache: "no-store" });
        if (!response.ok) {
            throw new Error(`简历数据加载失败: HTTP ${response.status}`);
        }

        const resumeData = await response.json();
        renderResume(resumeData);
    } catch (error) {
        console.error(error);
        appendStateText("简历数据加载失败，请先运行 parse_resume.py 生成 assets/resume-data.json");
    }
}

document.addEventListener("DOMContentLoaded", init);
