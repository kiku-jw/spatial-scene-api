# Spatial Scene Pro Validation Plan

## Goal

Validate whether Spatial Scene deserves a real client-side Pro product before building billing, accounts, or a kikuai.dev tools hub migration.

Canonical tracker: https://github.com/kiku-jw/spatial-scene-api/issues/1

## Product Assumptions

- Rendering should stay on the user's device.
- A browser-only tool cannot have a hard DRM-grade paywall because the client receives the renderer code.
- The first useful paywall is a soft product gate: watermark, export quality, batch workflow, and convenience.
- The next decision should be based on measured intent, not on building Stripe/Paddle first.

## Milestone 1: GitHub Pages Fake Door

Status: started.

Tasks:

- Add a `Pro Export` control to the current browser demo.
- Keep free rendering and download available.
- Open a waitlist/intent dialog instead of real checkout.
- Track `pro_click` and `pro_interest_submit`.
- Do not upload image or video data.
- Store events locally when no analytics endpoint is configured.
- Support `window.KIKU_SPATIAL_ANALYTICS_ENDPOINT` for a future event collector.

Done criteria:

- Static tests verify the Pro fake door exists.
- Static tests verify image/video payload names are absent from the browser analytics code.
- Browser smoke test can open the Pro dialog without breaking render/download.

## Milestone 2: Privacy-Safe Event Collector

Status: blocked on provider choice.

Preferred shape:

- Endpoint: `POST /api/events` or a small Cloudflare Worker.
- Payload: event name, timestamp, anonymous client id, page path, preset, resolution, fps, duration, strength, depth mode, browser output type.
- Explicitly excluded: image bytes, video bytes, filenames, prompt text, local paths.
- Separate optional endpoint for waitlist email if email capture is enabled.

Implementation options:

- Cloudflare Worker + D1/Supabase table: best fit for kikuai.dev later.
- PostHog/Plausible custom events: faster, but less control over waitlist email.
- Form provider for email only: fast, but weaker funnel data.

Done criteria:

- Events are visible in one dashboard/table.
- A test event from GitHub Pages reaches the endpoint.
- Privacy note is accurate.

## Milestone 3: Two-Week Demand Sprint

Status: not started.

Target metrics:

- 500 unique visitors.
- 100 successful renders.
- 20 Pro clicks.
- 5 email submissions or direct replies.
- 3 users explicitly ask for batch, higher quality export, no watermark, or automation.

Kill criteria:

- Fewer than 10 Pro clicks after qualified traffic.
- Users praise the demo but do not ask for export/workflow improvements.
- Most complaints are about core render quality rather than packaging or limits.

## Milestone 4: kikuai.dev Tools Hub Migration

Status: planned, after demand signal.

Tasks:

- Create `kikuai.dev/tools/spatial-scene`.
- Keep GitHub Pages as portfolio/demo mirror.
- Add shared tools shell: title, privacy note, tool body, pricing slot, related tools.
- Move event endpoint config out of page code and into hub environment.
- Preserve no-upload local rendering.

Done criteria:

- Tool works at `kikuai.dev/tools/spatial-scene`.
- GitHub Pages still links to the canonical hub URL.
- Analytics can distinguish GitHub Pages traffic from hub traffic.

## Milestone 5: Real Soft Paywall

Status: do not start before Milestone 3 passes.

Tasks:

- Choose provider: Stripe, Paddle, Lemon Squeezy, or another merchant-of-record.
- Add hosted checkout.
- Add webhook handler.
- Add signed entitlement token.
- Unlock Pro export in browser after entitlement check.
- Add customer portal/cancel flow.

Soft-gated Pro candidates:

- No watermark.
- Longer duration.
- 1080p vertical export.
- More presets.
- Batch export.

Done criteria:

- Paid user can unlock Pro on one browser.
- Cancelled/expired user loses Pro state after token expiry.
- Rendering remains local.

## Distribution Plan

Do first:

- Publish 10 short demo videos showing before/after results.
- Use titles around practical search intent: `photo to parallax video`, `CapCut 3D Zoom alternative`, `local browser image animation`, `no upload image to video`.
- Submit to Product Hunt, Futurepedia, There Is An AI For That, relevant GitHub lists, and creator-tool directories.
- Post a transparent build story: SaaS was parked, local browser version shipped instead.

Do later:

- Comparison pages on kikuai.dev after the hub exists.
- A narrow `best browser parallax video tools` article only if it is honest and useful.

Avoid:

- Paid "AI SEO" packages.
- Schema-heavy work beyond normal metadata.
- Large SEO content batch before demand proof.

## Open Questions for Nick

1. Which analytics/event backend should be used first?
2. What email or form destination should collect Pro waitlist leads?
3. What price should the fake door show: monthly, one-time, or both?
4. Should Pro positioning be creator-focused, automation-focused, or both?
5. Should the canonical brand be `Spatial Scene`, `Kiku Spatial`, or `KikuAI Spatial Scene`?
6. Do we restore `docs/assets/demo.png` from git, or did you intentionally remove it?

## Immediate Next Step

Decide the analytics endpoint and waitlist destination. Without that, the public fake door can show intent locally but cannot collect useful aggregate demand data from visitors.
