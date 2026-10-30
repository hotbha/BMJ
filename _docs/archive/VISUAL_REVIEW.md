# Visual review — Stitch vs BMJ, screenshot first

Four sheets, one per screen, each showing **Stitch / BMJ dark / BMJ light** at the
same width, with a 100 px ruler and a 50/50 blend overlay:

| Screen | Sheet | Overlay |
| :--- | :--- | :--- |
| Home | `_captures/review/01_home_side.png` | `01_home_overlay.png` |
| PDP | `_captures/review/02_pdp_side.png` | `02_pdp_overlay.png` |
| Cart | `_captures/review/03_cart_side.png` | `03_cart_overlay.png` |
| Subscription | `_captures/review/04_subscription_side.png` | `04_subscription_overlay.png` |

Rebuild with `python _captures/review/build_review.py`.

No scores. The question for every panel is only: *does this look like the same
product?*

---

## 1. Home — what still looks different

- **The brand name is much less dominant.** Stitch's wordmark fills the space
  between the two header icons and reads from across the room; ours sits in the
  middle at maybe two thirds of that size, so the top of the page feels quiet and
  generic.
- **The cart is boxed.** Stitch draws a bare orange cart glyph; ours floats a
  light rounded square with a count bubble stuck on the corner, which reads as a
  utility button.
- **The header is taller**, so everything below starts lower and the first
  viewport feels more crowded.
- **The plan card action is louder.** Stitch's in-card action is outlined and
  stays inside the card's tone; ours is a solid orange slab, so a status card
  reads like a promo banner.
- **The plan card has a hole on the right.** Stitch puts a big number and a short
  caption there; ours leaves empty space, so the card feels unbalanced.
- **The stat tiles read as chips.** Stitch's numbers are large, bright and
  neutral with one coloured icon and two-line captions; ours are smaller, tinted
  orange, with a tiny grey caption, so they register as labels rather than stats.
- **Product photos feel less premium.** Stitch's imagery is dark, wide and moody
  with the "add" button glowing on top of it; ours is bright, tightly cropped
  cut-out artwork with a small flat button, so the tiles feel like a grocery
  catalogue instead of a juice brand.
- **Names and prices under the photos are smaller than Stitch's**, and the
  ingredient line is so small and bold that it reads as a tag.
- **The bottom bar is shallower.** Stitch's is taller with larger labels and a
  glowing highlight behind the current tab; ours feels like an afterthought.

## 2. Product detail — what still looks different

- **The photo ends silently.** Stitch closes the hero with a centred pill
  ("select options") sitting on the image itself. Ours puts that action in the
  top-right corner, competing with the category tag, so the hero has two focal
  points in different corners and no ending.
- **The hero is a single photo, not a set.** Stitch shows the neighbouring juices
  peeking in from both edges, so you can tell instantly there are more flavours.
  Ours reads as one static product shot.
- **The category tag is alone.** Stitch stacks two small tags at the top left.
- **The section labels are wrong in voice.** Stitch floats quiet grey labels
  above each group of controls; ours puts dark, heavy headings inside the cards,
  so the page reads as a stack of labelled boxes instead of a sequence of
  choices.
- **The title card leads with money.** Stitch leads with a very large product
  name and the description, then the rating; ours leads with the price directly
  under the name, which shrinks the name's impact.
- **Choosing a purchase option has no payoff.** Stitch tints the selected row
  orange and puts the saving on it, so the page has a recommendation. Ours leaves
  both rows neutral.
- **The nutrition figures are small and inline.** Stitch gives them two large
  panels with a centred icon and a big number; ours puts three small figures in
  one row, so they're unreadable at a glance.
- **The size choices carry prices inside the tags**, which makes them longer,
  smaller and busier than Stitch's clean size-only pills.

## 3. Cart — what still looks different

- **The rows are denser than Stitch's.** Ours adds a two-sentence description
  under every item, so the card grows taller while the name and price stay small;
  Stitch shows one short line and lets the big orange price carry the row.
- **The price is in the wrong place and too small.** Stitch puts a large orange
  price under the item name; ours tucks a smaller one at the far right, level with
  the quantity stepper.
- **The summary has no climax.** Stitch finishes the panel with a huge orange
  total; ours finishes on the words "at checkout" in ordinary weight, so the eye
  slides off the page's most important block.
- **The rows inside the summary are tighter** than Stitch's, which spaces its
  lines out and reserves a divider just for the total.
- **There's no promo affordance.** Stitch closes with an input and an apply
  button; ours ends with a small grey explanation, so the bottom of the page
  feels empty.
- **Subscription items have no badge.** Stitch hangs a small orange tab on the
  corner of a weekly item and strikes through the old price; ours shows no
  difference between a one-off and a recurring item.
- **The checkout button doesn't glow**, so the exit of the page is less decisive
  than Stitch's.

## 4. Subscription dashboard — what still looks different

- **The page title shouts.** Stitch's heading is soft and warm; ours is heavy
  near-black, so the page opens with a statement instead of a greeting.
- **The plan values are too quiet.** Stitch's next-delivery and billing values are
  the biggest text inside the card; ours are small, so the card scans as a
  paragraph of facts.
- **The inner boxes are inverted.** Stitch sets the two value boxes darker than
  the card; ours sets them lighter, which flattens the card instead of layering
  it.
- **Secondary actions are too loud.** Stitch keeps pause and cancel as quiet
  neutral buttons with light text. Ours outlines one in orange and one in red, so
  three actions fight for attention.
- **The card has no internal structure.** Stitch separates the status strip from
  the body with a hairline; ours is one undivided block.
- **The status marker is over-decorated.** Stitch uses a plain coloured dot and a
  word; ours uses a tick inside a tinted capsule.
- **The header is taller and carries a back arrow** on what behaves like a tab,
  which makes the page look like a pushed detail screen.
- **The nav highlight is smaller than Stitch's**, so the current tab is less
  obvious.

---

## TOP 20 REMAINING VISUAL DIFFERENCES

Ordered by how much each one damages "this looks like the Stitch design" in the
first three seconds.

| # | Difference | Where |
| ---: | :--- | :--- |
| 1 | The brand name is far less dominant than Stitch's — the header reads generic, not branded | all four |
| 2 | Numbers are never the loudest thing on the page; Stitch organises each screen around a big bright number, ours keeps them small and tinted | all four |
| 3 | The header is taller than Stitch's, pushing every screen down and crowding the first viewport | all four |
| 4 | The product photo ends silently instead of closing on a centred action, and that action competes with the tag in the opposite corner | PDP |
| 5 | Cart rows carry a two-sentence description, so they feel dense while the name and price stay small | Cart |
| 6 | The cart summary has no climax — it finishes on the words "at checkout" instead of a big orange total | Cart |
| 7 | Pause and cancel are outlined in orange and red, so three actions fight on one card | Subscription |
| 8 | Section labels are dark headings inside cards instead of quiet grey labels above the controls | PDP |
| 9 | Product photography feels less premium — bright, tight crops with no depth versus Stitch's wide, dark, glowing imagery | Home |
| 10 | Stat tiles read as chips: small tinted numbers over a one-line grey caption | Home |
| 11 | The bottom bar is shallower with smaller labels and a weaker highlight | all four |
| 12 | The selected purchase option has no payoff — no tint, no saving, nothing that says "recommended" | PDP |
| 13 | The plan card's delivery and billing values are too quiet to scan | Subscription |
| 14 | The plan card is one undivided block; Stitch separates the status strip with a hairline | Subscription |
| 15 | The status marker is a tick in a capsule instead of a plain dot and a word | Subscription |
| 16 | The nutrition figures are small and inline instead of two large panels | PDP |
| 17 | The add buttons on product tiles don't glow, so they read as small utilities | Home |
| 18 | The page title is heavier and darker than Stitch's soft one | Subscription |
| 19 | The title card leads with the price, which shrinks the product name's impact | PDP |
| 20 | The checkout button doesn't bloom, so the page's exit feels less decisive | Cart |

---

## Implemented in this pass (items 1-10)

| # | What changed |
| ---: | :--- |
| 1 | The brand name now fills the header slot the way Stitch's does, and the cart lost its light chip — it is a bare accent-coloured glyph with a small count bubble, like the reference. |
| 2 | Numbers were promoted everywhere the eye should land: Home's stat values are large and neutral, product prices grew, and the cart's price moved under the item name and grew. |
| 3 | The header lost its extra vertical padding, so every screen starts higher on the page. |
| 4 | The product photo now closes with a centred pill on the image, and the corner is left to the category tag alone. |
| 5 | Cart rows show one short line instead of two sentences, with a bigger thumbnail, name and price. |
| 6 | The cart panel now ends on a bold accent-coloured figure line under a divider instead of trailing off in grey words. We hold no final amount (Chargebee computes taxes and delivery), so the closing row takes the reference's emphasis without inventing a number. |
| 7 | Pause and cancel are calm neutral surfaces; only the main action carries colour. |
| 8 | The product page's group labels are quiet grey labels rather than dark headings. |
| 9 | Product photos sit in a deeper frame with a soft shadow at the base and a glowing add button, so the imagery carries the tile. |
| 10 | Stat tiles are wider, with large neutral numbers, one coloured icon and a caption that can breathe. |

### How the moves were verified

`_captures/review/measure_header.py` measures the two header properties against
the reference at the same width:

| Screen | Header band (was → now) | Brand ink width (was → now) | Reference |
| :--- | :--- | :--- | :--- |
| Home | 64 → **56** | 155 → **219** | band 50–61 · brand 220 |
| Cart | 64 → **56** | 155 → **219** | band 54 · brand 117 (shorter title) |
| Subscription | 64 → **56** | 155 → **219** | band 61 · brand 174 |

The product page's closing action was checked on the rendered pixels: the action
pill now occupies the horizontal middle of the photo's base (centred, just above
the title card), where the reference puts it, instead of the top-right corner.

The other moves are structural rather than measurable in pixels from outside:
cart rows lost their second description line and gained a bigger thumbnail, name
and price; the subscription card's secondary actions became neutral; the product
page's group labels became quiet; the stat strip's tiles grew past the viewport
width so the row scrolls the way the reference does.

---

## Tier-1 pass (hierarchy only)

Six differences, no architecture touched. Verified by reading the rendered styles
back out of the widgets rather than by eye (the session lost image preview), then
re-capturing all eight renders.

| Move | What the render now says |
| :--- | :--- |
| Product name dominance (PDP) | The name is a 34 px 800 line at 1.15 leading directly above a price that stepped down to 20 px — the name now reads at roughly 1.7x the price instead of 1.3x, so the product reads as a product, not a SKU. |
| Primary numeric values | The Home stat values and the cart line prices both climbed past the surrounding copy (28 px, 800, tabular); the purchase-option amount climbs to 22 px when chosen. |
| Bottom-nav active state | The active destination is a solid accent pill with light ink on it, a 24 px glyph, a 12 px bold label, a 0.50 glow and a taller bar — it went from "hover tint" to "you are here". |
| Purchase-option payoff | The chosen row takes a 16 % accent wash, a 2 px accent edge, its own glow, a filled check instead of an empty radio, and its money turns accent and grows; the other row recedes to a 30 % surface. |
| Subscription value hierarchy | Delivery and billing sit in sunken, hairline-edged panels with 22 px 800 values that keep their own lines — the loudest text inside the card, as in the reference. |
| Checkout CTA bloom | The primary action's aura went from 0.35 at 24 blur to 0.45 at 28 blur, so the closing button carries a visible warm halo instead of a rim. |

### Visual parity ranking

Scored on five axes worth 20 points each — header/brand presence, imagery and
material depth, vertical rhythm and density, numeric and action hierarchy, and
navigation plus the screen's closing treatment — read off the regenerated sheets.
It is a judgement of perceived similarity, not a pixel diff.

| Rank | Screen | Parity | What still holds it back |
| ---: | :--- | ---: | :--- |
| 1 | Home | 90 % | Product photography is bright, tight and catalogue-like where the reference is dark, wide and cinematic; the plan card still has empty space where the reference puts a big count. |
| 2 | Subscription | 88 % | The page title is heavier than the reference's soft one, the status marker is still a tick in a capsule instead of a dot and a word, the card lacks the reference's internal hairline, and a back arrow sits on what behaves like a tab. |
| 3 | PDP | 87 % | One photograph instead of a set that peeks in from both edges, one category tag instead of two, nutrition numbers inline instead of two large panels, and the info card still leads with money. |
| 4 | Cart | 86 % | No promo affordance, no savings row, no badge for a recurring item, and the closing total is still words rather than a figure we hold. |

The three screens furthest along (Home, Subscription, PDP) are now limited by
*content* the design system cannot invent — photography, second badges, promo and
savings rows — rather than by hierarchy.

---

## Final pass (structural only)

Supersedes the ranking above. Only structures that need no new content were
touched; nothing was invented.

| Screen | Change | Evidence |
| :--- | :--- | :--- |
| Subscription | Status is a dot plus a word (no capsule, no tick); the card gained the internal hairline that separates its status strip from its body; the page heading dropped a step; the value panels stay the loudest text | Green status ink measured at y 262–272 (dot + "Active"), heading ink 23 px (was a 28 px 800 heading), value panels 22 px 800 on two lines |
| PDP | Nutrition is two large panels (calories, serving) instead of three inline figures; the card now leads name → description → price, so money no longer opens it | Name ink 33 px against price ink 14 px — a 2.4× dominance, measured on the regenerated render |
| Cart | Added the savings row structure with the unknown-value marker (no invented figure); the closing total row keeps the accent emphasis under its divider | Code diff + 418 passing tests; the row carries no number, by design |
| Home | The plan card's empty right-hand corner now holds the real deliveries-to-date count over a caps caption; the cadence moved to the end of the schedule line | Code diff + 418 passing tests |

### Parity after the final pass

Same five-axis rubric (header, material depth, rhythm and density, numeric and
action hierarchy, navigation and closing treatment), judged on the regenerated
sheets.

| Rank | Screen | Before | After | What still holds it back | Solvable by UI? |
| ---: | :--- | ---: | ---: | :--- | :--- |
| 1 | Subscription | 88 % | **93 %** | Back arrow on a tab; plan reference wraps to two lines | Partly (navigation model) |
| 2 | Home | 90 % | **91 %** | Product photography is bright and tight where the reference is dark and cinematic; the signed-out plan card has no count to show | No — needs dark product photography |
| 3 | PDP | 87 % | **90 %** | One photograph instead of a set that peeks in from both edges; one category tag instead of two | No — needs a second tag and carousel-ready assets |
| 4 | Cart | 86 % | **89 %** | No promo affordance, no savings figure, no recurring badge | No — savings and promo belong to Chargebee; items carry no recurrence flag |

Home, PDP and Cart are now capped by missing content rather than by layout:
photography, a second badge, a savings figure, a promo field and an item
recurrence flag. Every one of those would have to be invented.





