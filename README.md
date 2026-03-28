# patxangav2

Sitio estático para publicar una URL fija accesible por QR y rotar el contenido mostrado según el día.

## Objetivo

El QR siempre apunta a la misma URL. La página carga una configuración centralizada desde `config/config.json` y decide qué imagen o vídeo mostrar ese día.

## Estructura

- `index.html`: punto de entrada
- `styles.css`: estilos de la página
- `app.js`: lógica de carga y rotación diaria
- `config/config.json`: configuración centralizada
- `assets/`: contenido estático publicado

## Rotación

La rotación usa:

- `startDate`: fecha base de inicio
- `rotationMode`: actualmente `daily`
- `timeMode`: `utc` o `local`
- `items`: lista ordenada de contenidos

El contenido del día se calcula con la diferencia en días respecto a `startDate` y el índice resultante sobre `items`.

## Publicación en GitHub Pages

1. Subir el repositorio a GitHub.
2. Activar GitHub Pages desde la rama principal.
3. Usar la URL publicada como destino del QR.

## Cambiar contenidos

1. Sustituir o añadir archivos dentro de `assets/`.
2. Editar `config/config.json`.
3. Publicar los cambios.

