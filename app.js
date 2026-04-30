const CONFIG_PATH = "./config/config.json";
const PHRASES_PATH = "./config/frases.json";

const titleNode = document.querySelector("#campaign-title");
const descriptionNode = document.querySelector("#campaign-description");
const itemDescriptionNode = document.querySelector("#item-description");
const mediaContainerNode = document.querySelector("#media-container");
const effectiveDateNode = document.querySelector("#effective-date");
const contentNameNode = document.querySelector("#content-name");
const errorMessageNode = document.querySelector("#error-message");
const randomPhraseButtonNode = document.querySelector("#random-phrase-button");
const randomPhraseMessageNode = document.querySelector("#random-phrase-message");

let availablePhrases = [];

function showError(message) {
  errorMessageNode.hidden = false;
  errorMessageNode.textContent = message;
}

function hideError() {
  errorMessageNode.hidden = true;
  errorMessageNode.textContent = "";
}

function startOfDay(date, timeMode) {
  if (timeMode === "local") {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate());
  }

  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
}

function parseDateOnly(value, timeMode) {
  const [year, month, day] = value.split("-").map(Number);

  if (!year || !month || !day) {
    throw new Error("Las fechas deben tener formato YYYY-MM-DD");
  }

  if (timeMode === "local") {
    return new Date(year, month - 1, day);
  }

  return new Date(Date.UTC(year, month - 1, day));
}

function matchesDatePattern(pattern, date, timeMode) {
  const parts = pattern.split("-");

  if (parts.length !== 3) {
    throw new Error("Las fechas deben tener formato YYYY-MM-DD");
  }

  const [yearPattern, monthPattern, dayPattern] = parts;
  const yearValue = timeMode === "local" ? date.getFullYear() : date.getUTCFullYear();
  const monthValue = String((timeMode === "local" ? date.getMonth() : date.getUTCMonth()) + 1).padStart(2, "0");
  const dayValue = String(timeMode === "local" ? date.getDate() : date.getUTCDate()).padStart(2, "0");

  const yearMatches = yearPattern === "YYYY" || yearPattern === String(yearValue);
  const monthMatches = monthPattern === "MM" || monthPattern === monthValue;
  const dayMatches = dayPattern === dayValue;

  return yearMatches && monthMatches && dayMatches;
}

function getCurrentItem(config, now = new Date()) {
  if (!config.defaultItem) {
    throw new Error("La configuración debe incluir defaultItem");
  }

  const effectiveNow = startOfDay(now, config.timeMode);
  const datedItems = Array.isArray(config.items) ? config.items : [];
  const matchingItem = datedItems.find((item) => {
    if (!item.date) {
      throw new Error("Cada elemento de items debe incluir una fecha en el campo date");
    }

    return matchesDatePattern(item.date, effectiveNow, config.timeMode);
  });

  return {
    item: matchingItem || config.defaultItem,
    effectiveNow,
  };
}

function formatEffectiveDate(date, timeMode) {
  if (timeMode === "local") {
    return date.toLocaleDateString("es-ES");
  }

  return date.toISOString().slice(0, 10);
}

function resolveMediaSource(item, fallbackMimeType) {
  if (typeof item.img === "string" && item.img.trim() !== "") {
    const trimmedContent = item.img.trim();

    if (trimmedContent.startsWith("data:")) {
      return trimmedContent;
    }

    return `data:${item.mimeType || fallbackMimeType};base64,${trimmedContent}`;
  }

  if (typeof item.src === "string" && item.src.trim() !== "") {
    return item.src;
  }

  throw new Error(`Los elementos de tipo ${item.type} deben incluir \`img\` en base64 o \`src\``);
}

function renderMedia(item) {
  mediaContainerNode.innerHTML = "";

  if (item.type === "image") {
    const image = document.createElement("img");
    image.src = resolveMediaSource(item, "image/jpeg");
    image.alt = item.alt || item.name || "Contenido del día";
    mediaContainerNode.appendChild(image);
    return;
  }

  if (item.type === "video") {
    const video = document.createElement("video");
    video.className = "video-frame";
    video.controls = true;
    video.autoplay = true;
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    video.setAttribute("aria-label", item.name || "Vídeo del día");

    const source = document.createElement("source");
    source.src = resolveMediaSource(item, "video/mp4");
    source.type = item.mimeType || "video/mp4";

    video.appendChild(source);
    mediaContainerNode.appendChild(video);
    return;
  }

  throw new Error(`Tipo de contenido no soportado: ${item.type}`);
}

async function loadConfig() {
  const response = await fetch(CONFIG_PATH, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`No se pudo cargar la configuración (${response.status})`);
  }

  return response.json();
}

async function loadPhrases() {
  const response = await fetch(PHRASES_PATH, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`No se pudieron cargar las frases (${response.status})`);
  }

  const payload = await response.json();

  if (!Array.isArray(payload.phrases)) {
    throw new Error("El archivo de frases debe incluir una lista en `phrases`");
  }

  return payload.phrases.filter((phrase) => typeof phrase === "string" && phrase.trim() !== "");
}

function getRandomPhrase(phrases) {
  if (phrases.length === 0) {
    throw new Error("No hay frases disponibles");
  }

  const randomIndex = Math.floor(Math.random() * phrases.length);
  return phrases[randomIndex];
}

function showRandomPhrase() {
  const phrase = getRandomPhrase(availablePhrases);

  randomPhraseMessageNode.hidden = false;
  randomPhraseMessageNode.textContent = phrase;
  window.alert(phrase);
}

function setupRandomPhraseButton() {
  if (availablePhrases.length === 0) {
    randomPhraseButtonNode.disabled = true;
    randomPhraseMessageNode.hidden = false;
    randomPhraseMessageNode.textContent = "No hay frases disponibles ahora mismo.";
    return;
  }

  randomPhraseButtonNode.disabled = false;
  randomPhraseButtonNode.addEventListener("click", showRandomPhrase);
}

async function bootstrap() {
  hideError();

  try {
    const [config, phrases] = await Promise.all([
      loadConfig(),
      loadPhrases().catch(() => []),
    ]);
    const { item, effectiveNow } = getCurrentItem(config);
    availablePhrases = phrases;

    document.title = config.pageTitle || "patxangav2";
    titleNode.textContent = config.title;
    descriptionNode.textContent = config.description;
    itemDescriptionNode.textContent = item.description || "Sin descripción específica para este contenido.";
    effectiveDateNode.textContent = formatEffectiveDate(effectiveNow, config.timeMode);
    contentNameNode.textContent = item.name || item.src;

    renderMedia(item);
    setupRandomPhraseButton();
  } catch (error) {
    titleNode.textContent = "No se pudo cargar el contenido";
    descriptionNode.textContent = "Revisa la configuración o vuelve a intentarlo más tarde.";
    itemDescriptionNode.textContent = "";
    mediaContainerNode.innerHTML = "";
    randomPhraseButtonNode.disabled = true;
    showError(error instanceof Error ? error.message : "Error desconocido");
  }
}

bootstrap();
