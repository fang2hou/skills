# Adding images in FigCraft

Verified against `figcraft-cli` 0.12.1 and the `figcraft-live` MCP server. The same `{command, params}` objects work in MCP `exec`, MCP `batch`, and `figcraft-cli run`.

Contents:

- [Command signature](#command-signature)
- [Placement patterns](#placement-patterns)
- [Image adjustments](#image-adjustments)
- [SVG and file import](#svg-and-file-import)
- [Generated and downloaded images](#generated-and-downloaded-images)
- [Access limits](#access-limits)
- [Checks after placing](#checks-after-placing)

## Command signature

Call `exec {command: "image.place", params: {...}}` (or include the same object inside a `batch` array or `figcraft-cli run` script):

| Parameter         | Meaning                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| `path` or `data`  | Local file path or base64-encoded image bytes. Supply converter-clean bytes; URLs are not allowed |
| `x`, `y`          | Coordinates relative to the parent frame (ignored when the parent uses auto layout)               |
| `width`, `height` | Dimensions of the new layer; when omitted, defaults to the image's intrinsic pixel dimensions     |
| `parent`          | Node ID of the parent frame for the new image layer                                               |
| `target`          | Existing node ID; appends the image to that layer's `fills` instead of creating a new layer       |
| `mode`            | Scale mode: `fill` (default, stretches to box), `fit`, `crop`, or `tile`                          |

**Return value**: `{id, image, width, height, imageProfile}`. `image` is a content hash, so placing identical bytes twice stores a single asset. When `target` is used, `id`, `width`, and `height` reflect the target layer.

**Supported formats**: PNG, JPG, WebP, GIF, BMP, and TIFF. Passing a non-image file returns `unsupported image: The image format could not be determined`. Prefer `image.place` over `file.placeImage {path | data, x?, y?}`, which is the menu wrapper with fewer options.

## Placement patterns

### Image layer inside an auto-layout frame

Omit `x` and `y` because the parent auto-layout frame positions the child:

```json
{
  "command": "image.place",
  "params": {
    "path": "/abs/path/hero.jpg",
    "parent": 2,
    "width": 358,
    "height": 200,
    "mode": "crop"
  }
}
```

### Avatar or masked thumbnail

Create a rounded shape first, then apply the image fill to it via `target` (or `$ref` inside a `batch`). The shape's `cornerRadius` clips the image while keeping the base fill color underneath as a fallback:

```json
{
  "label": "avatar",
  "commands": [
    {
      "command": "node.create",
      "as": "avatar-shape",
      "params": {
        "type": "rectangle",
        "parent": { "$ref": "nav" },
        "width": 64,
        "height": 64,
        "name": "avatar",
        "props": { "cornerRadius": 32, "fill": "#CCCCCC" }
      }
    },
    {
      "command": "image.place",
      "params": {
        "path": "/abs/path/face.png",
        "target": { "$ref": "avatar-shape" },
        "mode": "crop"
      }
    }
  ]
}
```

Always reference the created shape with `as`/`$ref` (or capture its returned `id` from a prior call) rather than guessing node IDs.

### Background image behind auto-layout content

Place the image into the page frame with `parent`, set `absolute: true` on it via `node.set` so auto layout ignores it when flowing siblings, and move it to the back of the layer order with `node.reorder`.

### Choosing `mode`

- `crop`: Fills a fixed box without aspect-ratio distortion (best for photos and avatars).
- `fit`: Keeps the entire image visible without cropping (best for logos and product shots).
- `fill`: Stretches the image to the exact box dimensions.
- `tile`: Repeats the image at its intrinsic size for patterns.

### Batching multiple placements

Group related image placements into one `batch` so they share a single undo step:

```json
{
  "label": "gallery",
  "commands": [
    {
      "command": "image.place",
      "params": { "path": "/abs/path/a.png", "parent": 2, "width": 80, "height": 80, "mode": "fit" }
    },
    {
      "command": "image.place",
      "params": { "path": "/abs/path/b.png", "parent": 2, "width": 80, "height": 80, "mode": "fit" }
    }
  ]
}
```

## Image adjustments

`image.adjust {ids?, target?, index?, preset?, filters?}` modifies image fills. When `ids` is omitted, it acts on the current selection; because newly created layers become the selection, calling `image.adjust` immediately after `image.place` adjusts the newly placed image.

- **Presets**: `vivid`, `muted`, `warm`, `cool`, `blackAndWhite`, `fade`, `reset`, or a custom name saved with `image.savePreset`. Call `image.presets` to list available presets.
- **Filters**: `exposure`, `contrast`, `saturation`, `temperature`, `tint`, `highlights`, and `shadows`, each accepting a float in `-1..1` layered on top of any preset.

## SVG and file import

- `file.import {path | data + name, x?, y?, center?}`: Imports an SVG as an editable frame of vector and text layers, or imports a raster file as an image layer.
- `file.open {path}`: Opens a raster image as a standalone document tab.
- Prefer SVG for logos and icons so they remain editable and export cleanly as vectors.

## Generated and downloaded images

FigCraft never fetches remote URLs over the network. Write remote or generated images to disk first:

1. Download or generate the image into a project directory (such as `assets/`) with a descriptive filename.
2. Pass its absolute `path` to `image.place`. Reserve base64 `data` for small in-memory payloads; requests larger than 32 MiB are rejected by the control channel.
3. Keep the source image files in the repository alongside the `.figcraft` file. Although `.figcraft` embeds the pixel bytes, rebuilding or re-placing assets requires the original files.

## Access limits

- **Sandboxed roots**: When FigCraft runs with `--automation-read-root <dir>` or `--automation-write-root <dir>`, file reads and writes outside those directories fail with `automation path rejected`.
- **Local filesystem**: In attached live mode, the FigCraft app reads the path directly from the host filesystem where the app is running.

## Checks after placing

1. **Model check (`inspect {id}`)**: Verify that `width` and `height` match your target dimensions and that `fills` contains an `image` entry with the expected `scale_mode`.
2. **Pixel check (`render {ids: [<frame_id>]}`)**: Confirm that the image is visible, unstretched, and not clipped. If a placed image is invisible, check whether its parent auto-layout frame is missing `sizingH`/`sizingV` (defaulting to `100×100`) or whether `target` pointed to the wrong node ID.
3. **Color profile**: `imageProfile: null` indicates no embedded ICC profile (sRGB is assumed). Verify colors visually when importing wide-gamut (Display P3) assets.
