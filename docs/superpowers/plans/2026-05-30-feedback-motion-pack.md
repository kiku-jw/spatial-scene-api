# Feedback Motion Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the empty preview upload interaction intuitive and add three loop-friendly motion presets across browser demo and API render paths.

**Architecture:** Keep the existing deterministic renderers. Add preset-specific motion formulas to the browser canvas renderer and Python renderer, then map the same names to supported DepthFlow CLI motions.

**Tech Stack:** HTML/CSS/JavaScript, Python, NumPy, unittest, Playwright.

---

### Task 1: Empty Preview Upload Trigger

**Files:**
- Modify: `docs/index.html`
- Test: `tests/test_browser_demo_static.py`

- [x] Add a failing static test requiring `emptyState` to be a button and requiring an `emptyState` click handler that calls `imageInput.click()`.
- [x] Run `.venv/bin/python -m unittest tests.test_browser_demo_static` and confirm the new assertion fails.
- [x] Change the empty preview element to `<button class="empty" id="emptyState" type="button">` and add:

```js
emptyState.addEventListener("click", () => {
  if (!sourceImage && !imageInput.disabled) imageInput.click();
});
```

- [x] Run `.venv/bin/python -m unittest tests.test_browser_demo_static` and confirm it passes.

### Task 2: Browser Motion Presets

**Files:**
- Modify: `docs/index.html`
- Test: `tests/test_browser_demo_static.py`

- [x] Add failing static assertions for `drift`, `push_pull`, and `vertical_float` menu options and `getMotion()` branches.
- [x] Run `.venv/bin/python -m unittest tests.test_browser_demo_static` and confirm the new assertions fail.
- [x] Add the three menu options and browser motion formulas using `loop` and `pingPong`, with identical motion state at progress `0` and `1`.
- [x] Run the static test and JS syntax check.

### Task 3: Backend and DepthFlow Preset Parity

**Files:**
- Modify: `app/render.py`
- Modify: `app/depthflow_external.py`
- Modify: `app/benchmark.py`
- Modify: `app/static/index.html`
- Test: `tests/test_depth_provider.py`
- Test: `tests/test_render_motion.py`
- Test: `tests/test_depthflow_external.py`
- Test: `tests/test_benchmark.py`

- [x] Add failing tests requiring all seven presets and loop continuity for `drift`, `push_pull`, and `vertical_float`.
- [x] Run `.venv/bin/python -m unittest discover -s tests` and confirm the new assertions fail.
- [x] Add deterministic NumPy formulas, DepthFlow mappings, benchmark entries, and FastAPI UI options.
- [x] Run `.venv/bin/python -m unittest discover -s tests` and confirm all tests pass.

### Task 4: Documentation and Browser Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/PLAN.md`
- Modify: `docs/STATUS.md`
- Modify: `docs/TEST_PLAN.md`

- [x] Update preset lists and record the feedback-driven changes.
- [x] Run `.venv/bin/python -m compileall app scripts tests`, JS syntax validation, and `git diff --check`.
- [x] Start a local static server and use Playwright to confirm the empty preview opens the file picker.
- [x] Render a short browser MP4 with one new preset and confirm preview loop and download link.
- [x] Push `main`, wait for the Pages workflow, and verify the live page contains the new preset options.
