# Adding images in FigCraft

Verified against figcraft-cli 0.12.1 (the figcraft MCP server and the CLI
command registry, 2026-10). The same `{command, params}` objects run
through the MCP `exec` / `batch` tools and `figcraft-cli run`.

Contents: command · placement patterns · adjustments · SVG and file import · generated and downloaded images · checks · errors

## Command

MCP `exec {command: "image.place", params: {...}}` (same params inside
`batch` steps and `figcraft-cli run` lines)

| Param             | Meaning                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------- |
| `path` or `data`  | Local file path, or base64 bytes. Exactly one. No URL parameter.                            |
| `x`, `y`          | Position relative to the parent (ignored inside an auto-layout parent).                     |
| `width`, `height` | Size of the new layer. Omitted: the image's natural size (a 200×120 PNG placed as 200×120). |
| `parent`          | Node id of the frame to place into.                                                         |
| `target`          | Existing layer id: the image is added on top of its fills instead of creating a layer.      |
| `mode`            | `fill` (default), `fit`, `crop`, or `tile`.                                                 |

Result: `{id, image, width, height, imageProfile}`. `image` is a content
hash; placing the same bytes twice stores one image. With `target`, `id`,
`width`, and `height` describe the target layer.

PNG, JPG, WebP, GIF, BMP, and TIFF are the expected inputs; a non-image file
returns `unsupported image: The image format could not be determined`.
`file.placeImage {path | data, x?, y?}` is the menu equivalent with fewer
options; prefer `image.place`.

## Placement patterns

Image layer in an auto-layout frame (the layout positions it, so no `x`/`y`):

```json
{
  "command": "image.place",
  "params": { "path": "/abs/hero.jpg", "parent": 2, "width": 358, "height": 200, "mode": "crop" }
}
```

Avatar or masked thumbnail: make the shape first, then fill it. The rounded
corners clip the image, and the original fill stays underneath as a
fallback.

```json
[
  {
    "command": "node.create",
    "params": {
      "type": "rectangle",
      "parent": 2,
      "width": 64,
      "height": 64,
      "name": "avatar",
      "props": { "cornerRadius": 32, "fill": "#CCCCCC" }
    }
  },
  { "command": "image.place", "params": { "path": "/abs/face.png", "target": 4, "mode": "crop" } }
]
```

Capture the shape's id from the first result; the `4` above is the id the
previous calls happened to return, so never hard-code it.

Background image behind content: place into the page frame with
`parent`, then set `absolute: true` on it (`node.set`) so auto layout
does not push the content around, and keep it first in layer order
(`node.reorder`).

Mode choice: `crop` for photos that must fill a fixed box without
distortion; `fit` for logos and product shots that must not be cut; `fill`
stretches to the box; `tile` for patterns.

Batch several placements as one undo step:

```json
{
  "commands": [
    {
      "command": "image.place",
      "params": { "path": "/abs/a.png", "parent": 2, "width": 80, "height": 80, "mode": "fit" }
    },
    {
      "command": "image.place",
      "params": { "path": "/abs/b.png", "parent": 2, "width": 80, "height": 80, "mode": "fit" }
    }
  ],
  "label": "gallery"
}
```

## Adjustments

`image.adjust {ids?, target?, index?, preset?, filters?}` acts on the
selection when `ids` is omitted, and new layers become the selection, so a
call right after `image.place` adjusts the image just placed.

- Presets: `vivid`, `muted`, `warm`, `cool`, `blackAndWhite`, `fade`,
  `reset`, or a name saved with `image.savePreset`.
- `filters`: `exposure`, `contrast`, `saturation`, `temperature`, `tint`,
  `highlights`, `shadows`, each −1..1, applied over the preset.
- `image.presets` lists built-in and saved presets.

## SVG and file import

- `file.import {path | data + name, x?, y?, center?}`: SVG becomes an
  editable frame of vectors and text; a raster file becomes an image layer.
- `file.open {path}` opens a raster image as its own document.
- For logos and icons prefer SVG: it stays editable and exports as vectors.

## Generated and downloaded images

FigCraft never fetches from the network, so get the bytes onto disk first:

1. Download or generate into a project folder (for example `assets/`), with
   a descriptive name.
2. Place by absolute `path`. Use base64 `data` only for in-memory images
   (passed directly in the MCP arguments or the run script); payloads over
   32 MiB are refused.
3. Keep the source file next to the `.figcraft` document; the document embeds
   the pixels, but regenerating or re-placing needs the original.

## Access limits

- Headless server with `--automation-read-root DIR` can read images only
  inside those folders (and write only inside `--automation-write-root`).
  Outside paths fail with `automation path rejected`.
- Attached mode: the app opens the path itself, so confinement comes from
  the flags the app was started with, and the file must exist on the app's
  machine.

## Checks after placing

1. MCP `inspect {id}` (`node.get`): `width`/`height` as intended,
   and the `fills` list has an `image` paint with `scale_mode` as chosen.
2. MCP `render {ids: [<frame>]}`: the image is visible, not distorted, and
   not clipped by a parent. A missing image almost always means a parent
   frame without `sizingH`/`sizingV`, or a `target` id that is not the
   shape you meant.
3. Color profile: `imageProfile: null` means no usable embedded profile, so
   sRGB is assumed. Check wide-gamut sources if color matters.
