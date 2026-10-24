
const API_URL = "http://127.0.0.1:8000";

const elements = {
    grid: document.getElementById("jobs-grid"),
    count: document.getElementById("offer-count"),
    results: document.getElementById("results-label"),
    filters: document.getElementById("filters"),
    keyword: document.getElementById("keyword"),
    city: document.getElementById("city"),
    education: document.getElementById("education"),
    duration: document.getElementById("duration"),
    company: document.getElementById("company"),
    reset: document.getElementById("reset-filters"),
    dialog: document.getElementById("job-dialog"),
    detail: document.getElementById("job-detail"),
    closeDialog: document.getElementById("close-dialog"),
};

let searchTimer;
let loading = false;

document.getElementById("year").textContent = new Date().getFullYear();

function createElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined && text !== null) element.textContent = String(text);
    return element;
}

function showMessage(message, isError = false) {
    elements.grid.replaceChildren();
    const box = createElement("div", "state-message");
    box.textContent = message;
    if (isError) {
        const retry = createElement("button", "details-button", "Réessayer");
        retry.type = "button";
        retry.addEventListener("click", () => {
            loadCompanies().then(loadJobs);
        });
        box.append(" ");
        box.append(retry);
    }
    elements.grid.append(box);
}

async function apiGet(path) {
    const response = await fetch(`${API_URL}${path}`);
    if (!response.ok) {
        throw new Error(`Erreur HTTP ${response.status}`);
    }
    return response.json();
}

function fillSelect(select, values, placeholder) {
    const previousValue = select.value;
    select.replaceChildren(new Option(placeholder, ""));

    [...new Set(values.filter(value => value !== null && value !== undefined && String(value).trim() !== ""))]
        .sort((a, b) => String(a).localeCompare(String(b), "fr"))
        .forEach(value => select.add(new Option(String(value), String(value))));

    if ([...select.options].some(option => option.value === previousValue)) {
        select.value = previousValue;
    }
}

async function loadCompanies() {
    try {
        const companies = await apiGet("/companies");
        fillSelect(
            elements.company,
            companies.map(company => company.id),
            "Toutes les entreprises"
        );

        for (const option of elements.company.options) {
            if (!option.value) continue;
            const company = companies.find(item => String(item.id) === option.value);
            if (company) option.textContent = company.name;
        }
    } catch (error) {
        console.error("Impossible de charger les entreprises :", error);
    }
}

function buildQuery() {
    const params = new URLSearchParams();
    const fields = [
        ["keyword", elements.keyword.value.trim()],
        ["city", elements.city.value],
        ["education_level", elements.education.value],
        ["duration", elements.duration.value],
        ["company_id", elements.company.value],
    ];

    for (const [key, value] of fields) {
        if (value) params.set(key, value);
    }

    const query = params.toString();
    return query ? `/jobs?${query}` : "/jobs";
}

function formatDate(value) {
    if (!value) return "Non précisée";
    const date = new Date(`${value}T00:00:00`);
    if (Number.isNaN(date.getTime())) return value;
    return new Intl.DateTimeFormat("fr-FR", {
        day: "numeric",
        month: "long",
        year: "numeric",
    }).format(date);
}

function createJobCard(job) {
    const card = createElement("article", "job-card");
    const companyRow = createElement("div", "company-row");
    const initials = (job.company_name || "Entreprise").trim().charAt(0).toUpperCase();

    companyRow.append(
        createElement("div", "company-avatar", initials || "E")
    );

    const companyInfo = createElement("div");
    companyInfo.append(
        createElement("div", "company-name", job.company_name || "Entreprise"),
        createElement("div", "company-location", job.city || "Lieu non précisé")
    );
    companyRow.append(companyInfo);
    card.append(companyRow);

    if (job.education_level) {
        card.append(createElement("span", "job-tag", job.education_level));
    }

    card.append(
        createElement("h3", "", job.title),
        createElement("p", "job-description", job.description)
    );

    const meta = createElement("div", "job-meta");
    if (job.duration) meta.append(createElement("span", "meta-chip", `◷ ${job.duration}`));
    if (job.start_date) meta.append(createElement("span", "meta-chip", `Début : ${formatDate(job.start_date)}`));
    card.append(meta);

    const footer = createElement("div", "card-footer");
    footer.append(createElement("span", "salary", job.salary || "Rémunération non précisée"));

    const button = createElement("button", "details-button", "Voir le détail ↗");
    button.type = "button";
    button.addEventListener("click", () => openJobDetails(job));
    footer.append(button);
    card.append(footer);

    return card;
}

function openJobDetails(job) {
    elements.detail.replaceChildren();

    const company = createElement("div", "company-row");
    company.append(createElement("div", "company-avatar", (job.company_name || "E").trim().charAt(0).toUpperCase()));
    const companyInfo = createElement("div");
    companyInfo.append(
        createElement("div", "company-name", job.company_name || "Entreprise"),
        createElement("div", "company-location", job.city || "Lieu non précisé")
    );
    company.append(companyInfo);

    elements.detail.append(
        company,
        createElement("h2", "dialog-title", job.title),
        createElement("p", "dialog-description", job.description)
    );

    const facts = createElement("div", "detail-facts");
    const items = [
        ["Ville", job.city],
        ["Niveau d'études", job.education_level],
        ["Durée", job.duration],
        ["Rémunération", job.salary],
        ["Date de début", formatDate(job.start_date)],
    ];

    for (const [label, value] of items) {
        const fact = createElement("div", "detail-fact");
        fact.append(
            createElement("small", "", label),
            createElement("strong", "", value || "Non précisé")
        );
        facts.append(fact);
    }

    elements.detail.append(
        facts,
        createElement("p", "dialog-note", "La consultation des offres est disponible. La candidature en ligne sera ajoutée dans une prochaine version d'AlternanceHub.")
    );

    elements.dialog.showModal();
}

async function loadJobs() {
    if (loading) return;
    loading = true;
    elements.count.textContent = "Recherche…";
    elements.results.textContent = "Chargement des offres";
    showMessage("Chargement des opportunités…");

    try {
        const jobs = await apiGet(buildQuery());
        if (!Array.isArray(jobs)) {
            throw new Error("Le format des offres reçu par l'API est inattendu.");
        }

        fillSelect(elements.city, jobs.map(job => job.city), "Toutes les villes");
        fillSelect(elements.education, jobs.map(job => job.education_level), "Tous les niveaux");
        fillSelect(elements.duration, jobs.map(job => job.duration), "Toutes les durées");

        elements.count.textContent = `${jobs.length} offre${jobs.length > 1 ? "s" : ""}`;
        elements.results.textContent = jobs.length
            ? `${jobs.length} opportunité${jobs.length > 1 ? "s" : ""} à découvrir`
            : "Aucune offre ne correspond à ta recherche";

        if (jobs.length === 0) {
            showMessage("Aucune offre trouvée. Essaie d'autres mots-clés ou réinitialise les filtres.");
        } else {
            elements.grid.replaceChildren(...jobs.map(createJobCard));
        }
    } catch (error) {
        console.error("Erreur lors du chargement des offres :", error);
        elements.count.textContent = "Connexion indisponible";
        elements.results.textContent = "Impossible de charger les offres";
        showMessage(
            "L'API n'a pas répondu. Vérifie que FastAPI est lancé sur http://127.0.0.1:8000 et que le CORS est configuré.",
            true
        );
    } finally {
        loading = false;
    }
}

function scheduleSearch() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadJobs, 250);
}

elements.keyword.addEventListener("input", scheduleSearch);
elements.filters.addEventListener("change", loadJobs);

elements.reset.addEventListener("click", () => {
    elements.filters.reset();
    loadJobs();
});

elements.closeDialog.addEventListener("click", () => elements.dialog.close());

elements.dialog.addEventListener("click", event => {
    if (event.target === elements.dialog) elements.dialog.close();
});

async function init() {
    await loadCompanies();
    await loadJobs();
}

init();