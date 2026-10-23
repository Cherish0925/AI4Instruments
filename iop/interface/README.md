# IOP interface

[Desktop and browser](../interface.md) · [中文使用说明](../interface.zh-CN.md)

The runtime serves the application from its installed package. The same pages are used by ordinary browsers and the native desktop window. There is no frontend build step or external asset service.

| Source | Responsibility |
| --- | --- |
| `src/ai4instruments/iop/reader.html` | Application shell and navigation |
| `src/ai4instruments/iop/ui/app.css` | Layout, themes and responsive views |
| `ui/core.js` | Shared state, HTTP calls, localization and common elements |
| `ui/app.js` | Navigation, overview, search, settings and refresh |
| `ui/devices.js` | Discovery, registration and device operations |
| `ui/platforms.js` | Platform descriptions, connection graph and procedures |
| `ui/runs.js` | Workflow/program submission, history, results and downloads |
| `ui/resources.js` | Resource capacities, allocation and installed adapters |
| `src/ai4instruments/iop/desktop.py` | Native window, browser handoff and OS launchers |

Run the browser workflow checks from this directory:

```sh
npm ci
npx playwright install chromium
npm test
```

The check starts an isolated runtime, registers simulated instruments through the interface, saves a topology, submits an experiment, reads results, edits resources and exercises search, languages, themes and narrow layouts. It uploads an experiment ZIP and downloads a generated CSV file. It also confirms that closing the browser leaves an accepted experiment running. Set `IOP_UI_SCREENSHOTS` to a directory to save screenshots.

The native-window check uses pywebview and the same running application:

```sh
python -m pip install '.[desktop]'
python iop/interface/test/desktop.py
```

Run these two commands from the repository root. The release workflow runs native Windows/macOS windows, a Linux Qt window and browser workflows before publishing the packages. Native checks open the page, navigate devices, switch to the browser and confirm experiment continuity after closing the window.

`npm run format` formats the shipped interface source. Runtime/API and launcher checks are part of `python -m unittest discover -s tests -v` at the repository root.
