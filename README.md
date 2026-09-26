<p align="center"><img src="icons/icon128.png" width="96" alt="icon"></p>

<h1 align="center">Quiet Tab · 静页</h1>

<p align="center">English | <a href="README.zh-CN.md">中文</a></p>

<p align="center">A Chrome new tab page that shows <b>only your own wallpaper</b> — <b>no permissions, no scripts, no network requests</b>.</p>

<p align="center"><img src="samples/starry-sky.jpg" width="760" alt="Preview with the bundled sample wallpaper"><br><sub>Preview with the bundled sample wallpaper "Nocturne Field" (CC0)</sub></p>

---

## What is this

Even with a custom background, Chrome's built-in new tab page always keeps the Google logo, the search box and a few cards in the middle, and Chrome offers no option to turn them off.

This extension replaces the whole new tab page with an image of your choice: open a new tab and you see only your wallpaper. Searching still works from the address bar at the top.

It is deliberately tiny: a handful of files, no JavaScript at all, no permissions in the manifest, and the page makes no network requests. You can read the entire source in 30 seconds and verify for yourself that it collects nothing.

## Features

- 🖼️ **Just the wallpaper**: no Google logo, search box, shortcuts or cards
- 🔒 **Zero permissions**: no `permissions` or `host_permissions` in `manifest.json`
- 🚫 **No scripts, no network**: plain HTML + CSS that only loads local files from the extension folder
- 📁 **Drop in an image and go**: supports `background.jpg`, `background.png` and `background.webp`
- 🌗 **Without an image** it is a blank page whose color follows your system's light / dark mode
- 🔍 **Search is unaffected**: just start typing in the address bar after opening a new tab

## Files

```
quiet-tab/
├── manifest.json        # Declares one thing only: replace the new tab page
├── newtab.html          # The new tab page itself (HTML + CSS)
├── favicon.svg          # Tab icon (monochrome, adapts to light / dark theme)
├── icons/               # Icons for the extensions page (16 / 48 / 128 px)
├── _locales/            # English and Chinese name and description
├── samples/             # Sample wallpaper (original, CC0) with its generator and design notes
├── background.jpg       # ← your own wallpaper (not included in the repo)
├── README.md            # English documentation
└── README.zh-CN.md      # Chinese documentation
```

## Getting started

1. **Download**: click **Code → Download ZIP** on this page and unzip it, or `git clone` this repository. Keep the folder in a permanent location (don't move or delete it after loading).
2. **Add your wallpaper**: copy your image into the folder and rename it to `background.jpg` (or `background.png` / `background.webp`). No image at hand? Copy `samples/starry-sky.jpg` out and rename it (see "Sample wallpaper" below).
3. **Open the extensions page**: type `chrome://extensions` in the address bar and press Enter.
4. **Turn on Developer mode**: use the toggle in the top-right corner.
5. **Load the extension**: click **Load unpacked** and select this folder.
6. **Check it**: press `Ctrl + T` (`⌘ + T` on macOS). If Chrome asks whether this is the new tab page you expected, choose **Keep it**.

## Changing the wallpaper

1. Replace `background.*` in the folder with your new image (keep the file name).
2. Go back to `chrome://extensions` and click the reload button (↻) on this extension's card.
3. Open a new tab to see the new wallpaper.

> If several formats are present, the priority is `webp` > `png` > `jpg`. Remember to delete the old file when switching formats.

## Sample wallpaper

`samples/starry-sky.jpg` is an original 4K starry-sky wallpaper (3840×2160) made for this project. It is generated entirely by code and released under **CC0**, so you can use, modify and share it freely.

- The composition deliberately keeps the **centre dark and calm**, with the Milky Way arching across the top, which suits a new tab page;
- `samples/generate_starry_sky.py` is the generator. Its random seed is fixed, so **anyone can regenerate the image**, which proves it is original. With the same library versions (this image used numpy 2.5.3, scipy 1.18.1 and pillow 12.3.0) the output is byte-for-byte identical; other versions produce a visually equivalent image whose file may differ slightly. Change `SEED` for a different sky;
- `samples/starry-sky.md` contains the design notes for the image.

To regenerate (requires [uv](https://docs.astral.sh/uv/)):

```bash
cd samples
uv run --with numpy --with scipy --with pillow python generate_starry_sky.py
```

## Customization (optional)

All of these are edits to `newtab.html`; reload the extension afterwards:

| What to change | Where | Example |
|---|---|---|
| Which part of the image stays visible when the window's aspect ratio differs | `--focus` | `center` (default), `30% 50%` (subject on the left third) |
| Background color when there is no image / before it loads | `--fallback-color` | One value for light mode, one for dark mode |
| Tab title | `<title>` | Defaults to `New Tab` |

## Hiding the footer (Chrome 138 and later)

Since Chrome 138, **new tab pages provided by extensions** get an extra footer at the bottom showing the extension's name and a "Customize Chrome" button, and it covers part of the page. Chrome adds it, so the extension cannot remove it, but you can turn it off:

- **Right-click** the footer → **Hide footer on New Tab page**, or
- Click **Customize Chrome** in the bottom-right corner → at the bottom of the side panel, turn off **Show footer on New Tab page**.

The wallpaper then fills the whole page.

> ⚠️ Once hidden, the toggle no longer appears on extension-provided new tab pages. To turn it back on, visit `chrome://new-tab-page` (Chrome's original new tab page) and open **Customize Chrome** there. Menu labels may differ slightly between Chrome versions.

## Uninstalling / restoring the default new tab page

Open `chrome://extensions` and **turn off** or **remove** this extension. The new tab page immediately returns to Chrome's default.

## Notes

- **Developer mode is required**: the extension is installed as an unpacked extension, so Chrome may occasionally remind you that developer-mode extensions are in use. This is expected.
- **Don't move or delete the folder**: Chrome reads it directly; if you move it, load it again.
- **Only one extension can control the new tab page at a time**: if you have other new tab extensions, the most recently enabled one usually wins, so disable the others.
- **Phones and tablets are not supported**: Chrome for Android and iOS doesn't support extensions. Both can now set your own image as the new tab background from the new tab page's customize menu, though the Google logo and search box can't be removed there either.
- **The wallpaper doesn't sync across devices**: the image lives in a local folder, so each computer needs its own copy.
- **Image rights**: only use images you have the right to use. If it's someone else's artwork, don't commit it to a public repository (this repo's `.gitignore` excludes `background.*` by default), and credit the artist when sharing screenshots.
- **Image size**: a resolution close to your screen is enough (4K is plenty). Very large files may make new tabs open with a slight delay.
- **Other browsers**: Chromium-based browsers such as Microsoft Edge and Brave should work in principle, but they haven't all been tested.

## Privacy

- No permissions are requested, so it cannot read your history, tabs or page content.
- The page contains no JavaScript: nothing runs, and no network requests are made.
- Your wallpaper stays in this folder on your computer.

## FAQ

**Why not let me pick the image inside the page?**
That would need scripts and a storage permission, which defeats the "zero permissions, zero scripts" goal. Replacing one file is simple enough.

**Can I start typing to search right after opening a new tab?**
Yes, just type in the address bar (tested on Chrome).

**Why isn't the icon the Chrome logo?**
The Chrome logo is a registered trademark of Google. This project uses its own neutral icon (a frame with mountains and a moon).

## Acknowledgements

- Built with the help of [Claude](https://claude.com) (Anthropic), including research into similar projects, code, documentation and testing.
- The sample wallpaper "Nocturne Field · 夜曲星场" was designed and procedurally generated by Claude, and is released with the project under CC0.

## License

The code is released under the [MIT](LICENSE) license; the sample wallpaper `samples/starry-sky.jpg` is released under CC0.
