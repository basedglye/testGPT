const form = document.getElementById("tag-form");
const celebritySelect = document.getElementById("celebrity");
const locationInput = document.getElementById("location");
const notesInput = document.getElementById("notes");
const summaryGrid = document.getElementById("summary-grid");
const logList = document.getElementById("log-list");
const resetButton = document.getElementById("reset");
const shareButton = document.getElementById("share-button");
const shareLink = document.getElementById("share-link");
const shareStatus = document.getElementById("share-status");
const shareHint = document.getElementById("share-hint");
const summaryTemplate = document.getElementById("summary-card-template");
const logTemplate = document.getElementById("log-item-template");

const celebrities = ["Taylor Swift", "Scarlett Johansson", "Miley Cyrus"];
const storageKey = "michelle-lookalike-log";

const loadEntries = () => {
  const stored = localStorage.getItem(storageKey);
  return stored ? JSON.parse(stored) : [];
};

const saveEntries = (entries) => {
  localStorage.setItem(storageKey, JSON.stringify(entries));
};

const formatTime = (timestamp) =>
  new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(timestamp));

const renderSummary = (entries) => {
  summaryGrid.innerHTML = "";

  celebrities.forEach((name) => {
    const count = entries.filter((entry) => entry.celebrity === name).length;
    const card = summaryTemplate.content.cloneNode(true);
    card.querySelector(".summary-name").textContent = name;
    card.querySelector(".summary-count").textContent = count.toString();
    summaryGrid.appendChild(card);
  });
};

const renderLog = (entries) => {
  logList.innerHTML = "";

  if (entries.length === 0) {
    const empty = document.createElement("p");
    empty.textContent = "No tags yet. Add the first one above.";
    empty.className = "log-empty";
    logList.appendChild(empty);
    return;
  }

  entries
    .slice()
    .sort((a, b) => b.timestamp - a.timestamp)
    .forEach((entry) => {
      const item = logTemplate.content.cloneNode(true);
      item.querySelector(".log-celebrity").textContent = entry.celebrity;
      item.querySelector(".log-location").textContent = `Location: ${entry.location}`;
      item.querySelector(".log-notes").textContent = entry.notes
        ? `Notes: ${entry.notes}`
        : "";
      item.querySelector(".log-time").textContent = formatTime(entry.timestamp);
      logList.appendChild(item);
    });
};

const render = () => {
  const entries = loadEntries();
  renderSummary(entries);
  renderLog(entries);
};

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const newEntry = {
    celebrity: celebritySelect.value,
    location: locationInput.value.trim(),
    notes: notesInput.value.trim(),
    timestamp: Date.now(),
  };

  const entries = loadEntries();
  entries.push(newEntry);
  saveEntries(entries);

  form.reset();
  celebritySelect.value = newEntry.celebrity;
  locationInput.focus();
  render();
});

resetButton.addEventListener("click", () => {
  localStorage.removeItem(storageKey);
  render();
});

render();

const updateShareLink = () => {
  if (!shareLink) {
    return;
  }

  const url = window.location.href;
  shareLink.textContent = url;

  if (shareHint) {
    shareHint.textContent =
      window.location.protocol === "file:"
        ? "This is a local file link. Host it (GitHub Pages or Netlify) for a shareable URL."
        : "Copy or share the URL above.";
  }
};

const showShareStatus = (message) => {
  if (!shareStatus) {
    return;
  }

  shareStatus.textContent = message;
};

const handleShare = async () => {
  const url = window.location.href;

  if (navigator.share) {
    try {
      await navigator.share({
        title: "Michelle's Celebrity Lookalike Tracker",
        url,
      });
      showShareStatus("Shared successfully.");
      return;
    } catch (error) {
      showShareStatus("Share canceled.");
      return;
    }
  }

  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(url);
      showShareStatus("Link copied to clipboard.");
      return;
    } catch (error) {
      showShareStatus("Unable to copy link.");
      return;
    }
  }

  showShareStatus("Copy the link from above.");
};

updateShareLink();

if (shareButton) {
  shareButton.addEventListener("click", () => {
    handleShare();
  });
}
