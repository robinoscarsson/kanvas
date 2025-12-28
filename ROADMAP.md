# Kanvas Feature Roadmap

This roadmap proposes a path from Kanvas v0.1.x (current) to v1.0, prioritizing **educational clarity**, **Processing/p5.js familiarity**, and **incremental implementation**.

## Current state (v0.1.7 snapshot)

**What exists today**
- Core lifecycle: [`run()`](src/kanvas/core.py:64), [`noLoop()`](src/kanvas/core.py:34), [`loop()`](src/kanvas/core.py:45), [`isLooping()`](src/kanvas/core.py:55)
- Drawing primitives on a numpy framebuffer: [`Model.pixel()`](src/kanvas/model.py:451), [`Model.line()`](src/kanvas/model.py:468), [`Model.rect()`](src/kanvas/model.py:536), [`Model.circle()`](src/kanvas/model.py:571), [`Model.clear()`](src/kanvas/model.py:435)
- Noise: [`noise()`](src/kanvas/model.py:131), [`p_noise()`](src/kanvas/model.py:188), plus vectorized array variants
- Utilities: [`map_range()`](src/kanvas/utils.py:10), [`constrain()`](src/kanvas/utils.py:37), [`lerp()`](src/kanvas/utils.py:56), [`dist()`](src/kanvas/utils.py:75), [`rgb_to_hsv()`](src/kanvas/utils.py:91), [`hsv_to_rgb()`](src/kanvas/utils.py:123)
- Rendering via pygame surfarray: [`present_framebuffer()`](src/kanvas/view.py:51)
- Minimal input: ESC quit, S save: [`handle_input()`](src/kanvas/controller.py:20), [`save_canvas_to_png()`](src/kanvas/view.py:104)
- CLI demo: [`main()`](src/kanvas/__main__.py:13)

**Major gaps vs Processing/p5.js**
- No style/state layer: `background()`, `fill()`, `stroke()`, `strokeWeight()`, `push()/pop()`
- No transforms: `translate()`, `rotate()`, `scale()`, matrix stack
- No higher-level shapes: `ellipse()`, `triangle()`, `quad()`, `polygon()`, `arc()`
- No curves: `bezier()`, `curve()`, `beginShape()/vertex()/endShape()`
- No text: `text()`, `textSize()`, `textAlign()`, font loading
- Limited input: no mouse position, button state, key callbacks, event hooks
- No image API: `loadImage()`, `image()`, pixel read/write helpers
- No time/random helpers: `random()`, `randomSeed()`, `frameRate()`, `millis()`
- No 3D/shaders (likely out of scope until late)

## Guiding principles

1. **Processing-like API, Pythonic implementation**  
   Prefer familiar names and defaults, but keep signatures type-safe and explicit.

2. **Hybrid rendering with strict API**  
   The public API should be consistent; internally Kanvas may rasterize via numpy or pygame as appropriate (especially for text/images). A strong default is: “after `draw()`, the result is representable in `model.fb` and can be saved.”

3. **Small steps, teachable internals**  
   Each phase should be shippable, documented, and easy to reason about.

---

## Phase 1 — v0.2: Essential creative-coding ergonomics

Goal: make Kanvas feel like “real Processing” for basic sketches without adding heavy subsystems.

### 1) Style state: `background`, `fill`, `stroke`, `noFill`, `noStroke`
- **Priority:** High
- **Complexity:** Medium
- **Dependencies:** None (but enables many later features)
- **Description:** Add a style/state layer so users don’t pass RGB to every primitive. Default style should match p5-ish expectations.
- **Example API design:**
  ```py
  from kanvas import run

  def setup(k):
      k.size(400, 300)          # optional convenience wrapper
      k.background(30)
      k.stroke(255)
      k.fill(255, 0, 0)

  def draw(k, frame, dt):
      k.background(30)
      k.circle(200, 150, 40)    # uses current fill/stroke
  ```
  Notes:
  - Consider introducing a higher-level “sketch context” (e.g., `Kanvas` or `Sketch`) that wraps a `Model` and holds style state.
  - Keep `Model.*` low-level methods available for teaching/perf.

### 2) Stroke weight (basic)
- **Priority:** High
- **Complexity:** Medium
- **Dependencies:** Style state
- **Description:** Support thicker lines and outlines for shapes.
- **Example API design:**
  ```py
  k.strokeWeight(4)
  k.line(10, 10, 390, 290)
  ```

### 3) Basic input state: mouse + keyboard polling
- **Priority:** High
- **Complexity:** Medium
- **Dependencies:** Controller/view event expansion
- **Description:** Provide p5-like state variables and simple query functions.
- **Example API design:**
  ```py
  def draw(k, frame, dt):
      if k.mouseIsPressed:
          k.circle(k.mouseX, k.mouseY, 10)
      if k.keyIsDown("space"):
          k.noLoop()
  ```
  Implementation notes:
  - Extend [`poll_events()`](src/kanvas/view.py:81) to include mouse motion/buttons and key state.
  - Provide both “edge” events (pressed this frame) and “level” state (currently down).

### 4) Time helpers: `frameCount`, `deltaTime`, `millis`
- **Priority:** High
- **Complexity:** Simple
- **Dependencies:** Core loop already has `frame` and `dt`
- **Description:** Expose timing in a familiar way.
- **Example API design:**
  ```py
  k.frameCount   # int
  k.deltaTime    # float ms
  k.millis()     # int ms since start
  ```

### 5) Random helpers: `random`, `randomSeed`, `noiseSeed`
- **Priority:** Medium
- **Complexity:** Medium
- **Dependencies:** Noise functions already accept seed
- **Description:** Make procedural sketches easier without importing `random` everywhere.
- **Example API design:**
  ```py
  k.randomSeed(123)
  x = k.random(0, k.width)
  k.noiseSeed(42)
  v = k.noise(x * 0.01, 0.0)
  ```

### 6) Canvas helpers: `size`, `width`, `height`, `saveFrame`
- **Priority:** Medium
- **Complexity:** Simple
- **Dependencies:** View save already exists
- **Description:** Provide p5-like convenience wrappers.
- **Example API design:**
  ```py
  k.size(640, 360)
  k.saveFrame()                 # auto timestamp
  k.saveFrame("my_sketch")      # prefix
  ```

---

## Phase 2 — v0.3: Enhanced drawing + interactivity

Goal: broaden the drawing vocabulary and make interaction patterns idiomatic.

### 1) Transformations + matrix stack: `push`, `pop`, `translate`, `rotate`, `scale`
- **Priority:** High
- **Complexity:** Complex
- **Dependencies:** Style/state stack (push/pop should include style + transform)
- **Description:** Add 2D transforms so users can build scenes without manual trig.
- **Example API design:**
  ```py
  k.push()
  k.translate(k.width/2, k.height/2)
  k.rotate(0.01 * k.frameCount)
  k.rect(-50, -25, 100, 50)
  k.pop()
  ```
  Implementation approach:
  - Maintain a 3x3 affine matrix stack.
  - Apply transforms to vertices before rasterization.

### 2) More primitives: `ellipse`, `triangle`, `quad`, `point`
- **Priority:** High
- **Complexity:** Medium
- **Dependencies:** Style state (+ strokeWeight for best results)
- **Description:** Fill out the “basic shapes” set.
- **Example API design:**
  ```py
  k.ellipse(200, 150, 80, 40)   # w,h like p5
  k.triangle(x1,y1, x2,y2, x3,y3)
  k.quad(x1,y1, x2,y2, x3,y3, x4,y4)
  k.point(x, y)
  ```

### 3) `beginShape` / `vertex` / `endShape` (polylines + polygons)
- **Priority:** High
- **Complexity:** Complex
- **Dependencies:** Transforms, style state
- **Description:** Enable custom shapes and teach geometry pipelines.
- **Example API design:**
  ```py
  k.beginShape()
  k.vertex(10, 10)
  k.vertex(100, 20)
  k.vertex(80, 120)
  k.endShape(close=True)
  ```

### 4) Curves: `bezier`, `bezierVertex`, `curve`
- **Priority:** Medium
- **Complexity:** Complex
- **Dependencies:** beginShape/vertex OR standalone curve rasterization
- **Description:** Add expressive curve drawing.
- **Example API design:**
  ```py
  k.bezier(x1,y1, cx1,cy1, cx2,cy2, x2,y2)
  ```

### 5) Event callbacks (optional layer): `mousePressed`, `mouseReleased`, `keyPressed`, `keyReleased`
- **Priority:** Medium
- **Complexity:** Medium
- **Dependencies:** Input event tracking
- **Description:** Support the common Processing pattern of defining callbacks.
- **Example API design:**
  ```py
  def mousePressed(k): ...
  def keyPressed(k, key): ...
  run(setup, draw, mousePressed=mousePressed, keyPressed=keyPressed)
  ```

### 6) Color helpers: `colorMode`, `color`, alpha support
- **Priority:** Medium
- **Complexity:** Medium
- **Dependencies:** Style state, framebuffer format decisions
- **Description:** Add alpha and alternate color spaces (at least RGB + HSV).
- **Example API design:**
  ```py
  k.colorMode("RGB", 255)
  k.fill(255, 0, 0, 128)        # alpha
  ```
  Note: alpha implies either RGBA framebuffer or compositing rules.

---

## Phase 3 — v0.4: Media support + richer rendering

Goal: unlock common creative-coding workflows: text, images, pixel manipulation, better export.

### 1) Text rendering: `text`, `textSize`, `textAlign`, `loadFont`
- **Priority:** High
- **Complexity:** Medium
- **Dependencies:** Hybrid rendering decision; optional alpha support
- **Description:** Render text using pygame font rasterization, then composite into the canvas.
- **Example API design:**
  ```py
  font = k.loadFont("assets/Inter-Regular.ttf", size=24)
  k.textFont(font)
  k.textAlign("CENTER", "CENTER")
  k.text("Hello", 200, 150)
  ```

### 2) Image API: `loadImage`, `image`, `tint`, `imageMode`
- **Priority:** High
- **Complexity:** Medium
- **Dependencies:** Alpha/compositing rules recommended
- **Description:** Load images and draw them to the canvas.
- **Example API design:**
  ```py
  img = k.loadImage("assets/cat.png")
  k.image(img, 10, 10)
  k.image(img, 10, 10, 128, 128)   # scaled
  ```

### 3) Pixel operations: `get`, `set`, `loadPixels`, `updatePixels`
- **Priority:** Medium
- **Complexity:** Medium
- **Dependencies:** Clear definition of pixel coordinate conventions
- **Description:** Provide p5-like pixel access patterns for teaching image processing.
- **Example API design:**
  ```py
  k.loadPixels()
  c = k.get(x, y)               # returns (r,g,b[,a])
  k.set(x, y, (255, 0, 0))
  k.updatePixels()
  ```

### 4) Better export: `saveFrame` patterns, GIF/sequence helpers
- **Priority:** Medium
- **Complexity:** Medium
- **Dependencies:** View save exists; may add optional deps
- **Description:** Make it easy to export animations for sharing.
- **Example API design:**
  ```py
  k.saveFrame("frames/frame####.png")  # p5-like numbering
  k.captureFrames("frames/", every=2)
  ```

### 5) Noise upgrades: octaves/fBm, domain warping helpers
- **Priority:** Low
- **Complexity:** Medium
- **Dependencies:** Existing noise functions
- **Description:** Common procedural patterns without requiring users to write boilerplate.
- **Example API design:**
  ```py
  v = k.fbm(x, y, octaves=5, lacunarity=2.0, gain=0.5)
  ```

---

## Phase 4 — v1.0: Production-ready core + broad p5 parity (2D)

Goal: stabilize APIs, improve robustness, and cover the “expected” p5 2D surface area.

### 1) Stable public API layer (separate from low-level `Model`)
- **Priority:** High
- **Complexity:** Medium
- **Dependencies:** Earlier phases
- **Description:** Formalize a `Sketch`/`Kanvas` context object with documented behavior and backwards compatibility guarantees.
- **Example API design:**
  ```py
  from kanvas import Sketch, run

  class MySketch(Sketch):
      def setup(self): ...
      def draw(self): ...

  run(MySketch(), size=(640, 360))
  ```

### 2) Robust coordinate + shape modes: `rectMode`, `ellipseMode`, angle mode
- **Priority:** Medium
- **Complexity:** Medium
- **Dependencies:** Expanded primitives + transforms
- **Description:** Match p5 ergonomics and reduce confusion.
- **Example API design:**
  ```py
  k.rectMode("CENTER")
  k.ellipseMode("RADIUS")
  k.angleMode("DEGREES")
  ```

### 3) Comprehensive input parity (2D): mouse wheel, drag, key repeat, focus
- **Priority:** Medium
- **Complexity:** Medium
- **Dependencies:** Input system
- **Description:** Make interactive sketches reliable across platforms.

### 4) Performance + correctness hardening
- **Priority:** High
- **Complexity:** Complex
- **Dependencies:** Everything
- **Description:** Profiling, clipping correctness, alpha compositing correctness, deterministic behavior, and expanded tests.

### 5) Optional advanced track (explicitly non-core): 3D, shaders, sound
- **Priority:** Low
- **Complexity:** Complex
- **Dependencies:** Major architectural changes
- **Description:** These are large scope increases; keep them optional or separate packages.
- **Example API design (if ever):**
  ```py
  # kanvas3d extension package (hypothetical)
  k3d = k.enable3D()
  k.shader(my_shader)
  ```

---

## Proposed implementation order (high-level)

1. **v0.2**: style state + background + input polling + time/random helpers  
2. **v0.3**: transforms + shape builder + more primitives + callbacks  
3. **v0.4**: text + images + pixel ops + export helpers  
4. **v1.0**: stabilize API + parity polish + hardening

## Notes on API surface

Kanvas can keep the current low-level API intact (good for teaching and tests) while adding a higher-level layer:

- Low-level: `Model` methods remain explicit and fast.
- High-level: `Kanvas`/`Sketch` context provides p5-like stateful drawing.

This dual-layer approach keeps the project beginner-friendly while enabling p5-like ergonomics.
