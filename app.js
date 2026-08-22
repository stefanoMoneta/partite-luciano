const IT_DAYS = [
  "domenica", "lunedì", "martedì", "mercoledì",
  "giovedì", "venerdì", "sabato"
];

const IT_MONTHS = [
  "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
  "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"
];

function localDateKey(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function dateFromKey(key) {
  const [y, m, d] = key.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function dayHeading(key) {
  const date = dateFromKey(key);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);

  let label;
  if (localDateKey(date) === localDateKey(today)) {
    label = "OGGI";
  } else if (localDateKey(date) === localDateKey(tomorrow)) {
    label = "DOMANI";
  } else {
    label = IT_DAYS[date.getDay()].toUpperCase();
  }

  const fullDate =
    `${IT_DAYS[date.getDay()]} ${date.getDate()} ${IT_MONTHS[date.getMonth()]}`;

  return { label, fullDate };
}

function groupByDate(matches) {
  return matches.reduce((groups, match) => {
    (groups[match.date] ??= []).push(match);
    return groups;
  }, {});
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function isPisaMatch(match) {
  return match.home === "Pisa" || match.away === "Pisa";
}

async function loadMatches() {
  const container = document.getElementById("matches");
  const update = document.getElementById("last-update");

  try {
    const response = await fetch("data/partite.json", { cache: "no-store" });
    if (!response.ok) throw new Error("Impossibile caricare i dati");

    const data = await response.json();

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const todayKey = localDateKey(today);

    const visibleMatches = data.matches
      .filter(match => match.date >= todayKey)
      .sort((a, b) =>
        `${a.date}T${a.time}`.localeCompare(`${b.date}T${b.time}`)
      );

    container.innerHTML = "";

    if (!visibleMatches.length) {
      container.innerHTML = `
        <div class="empty">
          Nessuna partita nei prossimi quattro giorni.
        </div>
      `;
    } else {
      const grouped = groupByDate(visibleMatches);

      for (const [date, matches] of Object.entries(grouped)) {
        const { label, fullDate } = dayHeading(date);

        const section = document.createElement("section");
        section.className = "day";

        section.innerHTML = `
          <div class="day-header">
            <span class="day-label">${escapeHtml(label)}</span>
            <span class="day-date">${escapeHtml(fullDate)}</span>
          </div>
        `;

        for (const match of matches) {
          const article = document.createElement("article");
          article.className = "match";

          if (isPisaMatch(match)) {
            article.classList.add("pisa");
          }

          article.innerHTML = `
            <div class="match-time">${escapeHtml(match.time)}</div>
            <div class="match-teams">
              ${escapeHtml(match.home)} – ${escapeHtml(match.away)}
            </div>
          `;

          section.appendChild(article);
        }

        container.appendChild(section);
      }
    }

    if (data.updatedAt) {
      const updatedAt = new Date(data.updatedAt);
      update.textContent =
        `Aggiornato ${updatedAt.toLocaleDateString("it-IT")} alle ` +
        `${updatedAt.toLocaleTimeString("it-IT", {
          hour: "2-digit",
          minute: "2-digit"
        })}`;
    } else {
      update.textContent = "";
    }
  } catch (error) {
    console.error(error);

    container.innerHTML = `
      <div class="error">
        Non riesco a caricare le partite.<br>
        Riprova tra poco.
      </div>
    `;

    update.textContent = "";
  }
}

loadMatches();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("service-worker.js");
  });
}
