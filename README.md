# patxangav2

Regalo de los colegas de la uni para Tajada. Un QR que, al escanearlo, te lleva a este sitio y te suelta la chorrada del día.

## Cómo funciona

El QR siempre apunta a la misma URL. La página decide qué imagen o vídeo mostrar según el día consultando `config/config.json`. Si el día tiene algo especial preparado, lo muestra; si no, sale el contenido por defecto.

También tiene un botón para recibir sabiduría aleatoria cortesía del Taj.

## Añadir o cambiar contenidos

1. Mete los archivos nuevos en `fotos/`.
2. Conviértelos a base64:
   ```bash
   python3 scripts/export_assets_base64.py --input-dir fotos --output-dir base64_exports
   ```
3. Copia el base64 generado en el campo `img` del elemento correspondiente en `config/config.json`.
4. Sube los cambios. GitHub Pages lo publica automáticamente.

Para añadir frases al botón, edita `config/frases.json`.

## Estructura de archivos

- `index.html` — punto de entrada
- `styles.css` — estilos
- `app.js` — lógica de selección de contenido
- `config/config.json` — configuración y contenidos en base64
- `config/frases.json` — frases para el botón aleatorio
- `fotos/` — archivos fuente originales (no se sirven directamente)
- `scripts/export_assets_base64.py` — herramienta para convertir archivos a base64

## Selección de contenido por fecha

Cada elemento de `items` en `config.json` tiene un campo `date` con formato `YYYY-MM-DD`. El sistema muestra el primer elemento cuya fecha coincida con la del día actual. Si ninguno coincide, se usa `defaultItem`.

`YYYY` y `MM` actúan como comodines:

| Patrón       | Coincide con                       |
| ------------ | ---------------------------------- |
| `2025-06-15` | Exactamente el 15 de junio de 2025 |
| `YYYY-06-15` | El 15 de junio de cualquier año    |
| `YYYY-MM-15` | El día 15 de cualquier mes y año   |

## Formato de un elemento de contenido

### Elemento de fecha exacta o patrón

```json
{
  "date": "YYYY-MM-15",
  "type": "image",
  "name": "Nombre descriptivo",
  "description": "Descripción visible en la página",
  "alt": "Texto alternativo",
  "img": "<base64>",
  "mimeType": "image/jpeg"
}
```

### Elemento de rango de fechas (varias imágenes)

```json
{
  "startDate": "2026-05-14",
  "endDate": "2026-06-05",
  "images": [
    {
      "type": "image",
      "name": "Foto 1",
      "img": "<base64>",
      "mimeType": "image/jpeg"
    },
    {
      "type": "image",
      "name": "Foto 2",
      "img": "<base64>",
      "mimeType": "image/jpeg"
    }
  ]
}
```

Cuando la fecha actual cae dentro del rango, se muestra una imagen aleatoria del array `images` en cada carga de página.

### Elemento de rango con fecha y hora (un solo contenido)

```json
{
  "startDate": "2026-05-24 02:05",
  "endDate": "2026-05-25 03:50",
  "type": "youtube",
  "name": "Video nocturno",
  "src": "https://www.youtube.com/watch?v=..."
}
```

Cuando se incluye hora en `startDate` o `endDate`, la comparación es exacta (fecha + hora). El contenido sólo aparece dentro de esa franja. Sin hora, el rango abarca el día completo.

---

- `type`: `"image"`, `"video"` o `"youtube"`.
- `img`: base64 del archivo. Alternativa: `src` con una URL externa. Para YouTube, usa `src` con la URL del vídeo (`youtube.com/watch?v=...` o `youtu.be/...`).
- `mimeType`: por defecto `image/jpeg` para imágenes y `video/mp4` para vídeos.
- `timeMode` en la raíz del config: `"utc"` o `"local"` (zona horaria para evaluar la fecha).
