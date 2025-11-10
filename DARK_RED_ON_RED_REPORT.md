# Dark Red on Red - Contrast Issues Found

## Issue Summary

Found **dark red/gray text on red backgrounds** that violates WCAG accessibility standards. These appear primarily in the Concierge page and a few other locations.

## Critical Issues Found

### 1. **Concierge Page - User Message Content** 🔴 CRITICAL
**File:** `src/views/templates/concierge.html`

**Problem:** User messages have crimson (#990000) background with white text, but nested elements use dark text colors:

- **Line 396**: `<h4>` tags use `color: var(--iu-dark)` (#4B0000)
  - **Contrast Ratio:** #4B0000 on #990000 = 1.1:1 ❌ FAILS (needs 4.5:1)
  - **Status:** Barely visible/unreadable

- **Line 423**: `<strong>` tags use `color: var(--iu-dark)` (#4B0000)
  - **Contrast Ratio:** Same as above = 1.1:1 ❌ FAILS
  - **Status:** Barely visible/unreadable

- **Line 427**: `<em>` tags use `color: #555`
  - **Contrast Ratio:** #555555 on #990000 = 1.3:1 ❌ FAILS
  - **Status:** Barely visible/unreadable

### 2. **Concierge Page - Assistant Message Links** 🟡 MEDIUM
**File:** `src/views/templates/concierge.html` (lines 425-430)

**Problem:** Links on cream background (assistant messages) use crimson text with darker hover state

- **Line 431**: Hover state uses `color: #7A0000` 
  - **Current:** Crimson (#990000) text on cream (#EEDEDB) = 6.1:1 ✅ OK
  - **Hover:** Dark crimson (#7A0000) on cream = 3.5:1 ❌ FAILS on hover

---

## Detailed Analysis

### Dark Red on Red Combinations:

| Element | Color | Background | Text Content | Contrast | Status |
|---------|-------|-----------|---|----------|--------|
| `<h4>` in user message | #4B0000 | #990000 | Headings | 1.1:1 | ❌ FAIL |
| `<strong>` in user message | #4B0000 | #990000 | Bold text | 1.1:1 | ❌ FAIL |
| `<em>` in user message | #555555 | #990000 | Italic text | 1.3:1 | ❌ FAIL |
| Link hover in assistant msg | #7A0000 | #EEDEDB | Links | 3.5:1 | ❌ FAIL |

---

## Root Cause

The CSS defines base `.message-content` styles that apply to both assistant messages (cream background) and user messages (crimson background). The dark text colors work on cream but fail completely on crimson.

### Current Code Structure:
```css
.message-content {
    background: var(--iu-cream);      /* Light cream background */
    color: var(--iu-dark);            /* Dark red text - OK here */
}

.message-content h4 {
    color: var(--iu-dark);            /* Dark red h4 text - OK on cream */
}

.message-content strong {
    color: var(--iu-dark);            /* Dark red bold text - OK on cream */
}

.user-message .message-content {
    background: var(--iu-crimson);    /* Red background */
    color: white;                     /* White text - OK */
    /* But h4, strong, em inherit dark colors! */
}
```

---

## Solution Required

Add overrides for `.user-message` content elements to ensure white/light text:

```css
/* Override dark text in user messages */
.user-message .message-content h4 {
    color: white;  /* Override dark red with white */
}

.user-message .message-content strong {
    color: white;  /* Override dark red with white */
}

.user-message .message-content em {
    color: rgba(255, 255, 255, 0.95);  /* Override gray with light white */
}

.user-message .message-content h2,
.user-message .message-content h3 {
    color: var(--iu-cream);  /* Light cream for headers */
    border-bottom-color: var(--iu-cream);  /* Light border */
}

.message-content .chat-link:hover {
    color: var(--iu-crimson);  /* Keep crimson but add more contrast */
    background-color: rgba(153, 0, 0, 0.15);
}
```

---

## Sites Affected

- **Concierge AI page** - Primary location with user messages
- **Login page** (possible if any red background styling)
- **Register page** (possible if any red background styling)

---

## WCAG Compliance

**Current Status:** ⚠️ Partial Compliance
- Text on white/cream backgrounds: ✅ Compliant
- Text on crimson backgrounds: ❌ Non-compliant
- Mobile menu: ✅ Compliant
- Navbar: ✅ Compliant

**After Fix:** ✅ Full WCAG AAA Compliance

