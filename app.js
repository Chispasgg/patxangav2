const CONFIG_PATH = "./config/config.json";
const MS_PER_DAY = 24 * 60 * 60 * 1000;

const titleNode = document.querySelector("#campaign-title");
const descriptionNode = document.querySelector("#campaign-description");
const mediaContainerNode = document.querySelector("#media-container");
const effectiveDateNode = document.querySelector("#effective-date");
const contentNameNode = document.querySelector("#content-name");
const errorMessageNode = document.querySelector("#error-message");

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
    throw new Error("startDate debe tener formato YYYY-MM-DD");
  }

  if (timeMode === "local") {
    return new Date(year, month - 1, day);
  }

  return new Date(Date.UTC(year, month - 1, day));
}

function getCurrentItem(config, now = new Date()) {
  if (config.rotationMode !== "daily") {
    throw new Error("Solo se soporta rotationMode=daily en esta versión");
  }

  if (!Array.isArray(config.items) || config.items.length === 0) {
    throw new Error("La configuración debe incluir al menos un elemento en items");
  }

  const effectiveNow = startOfDay(now, config.timeMode);
  const startDate = parseDateOnly(config.startDate, config.timeMode);
  const diffDays = Math.floor((effectiveNow.getTime() - startDate.getTime()) / MS_PER_DAY);
  const normalizedIndex = ((diffDays % config.items.length) + config.items.length) % config.items.length;

  return {
    item: config.items[normalizedIndex],
    effectiveNow,
  };
}

function formatEffectiveDate(date, timeMode) {
  if (timeMode === "local") {
    return date.toLocaleDateString("es-ES");
  }

  return date.toISOString().slice(0, 10);
}

function renderMedia(item) {
  mediaContainerNode.innerHTML = "";

  if (item.type === "image") {
    const image = document.createElement("img");
    image.src = item.src;
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
    source.src = item.src;
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

async function bootstrap() {
  hideError();

  try {
    const config = await loadConfig();
    const { item, effectiveNow } = getCurrentItem(config);

    document.title = config.pageTitle || "patxangav2";
    titleNode.textContent = config.title;
    descriptionNode.textContent = config.description;
    effectiveDateNode.textContent = formatEffectiveDate(effectiveNow, config.timeMode);
    contentNameNode.textContent = item.name || item.src;

    renderMedia(item);
  } catch (error) {
    titleNode.textContent = "No se pudo cargar el contenido";
    descriptionNode.textContent = "Revisa la configuración o vuelve a intentarlo más tarde.";
    mediaContainerNode.innerHTML = "";
    showError(error instanceof Error ? error.message : "Error desconocido");
  }
}

bootstrap();

