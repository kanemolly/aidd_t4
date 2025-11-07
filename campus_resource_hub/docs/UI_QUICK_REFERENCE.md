# UI & Performance Features - Quick Reference

## 🎯 Button Loading Spinners

### Automatic (Recommended)
All `<form>` submit buttons automatically show spinners:
```html
<form method="POST">
    <button type="submit">Save Changes</button>
    <!-- Spinner shows automatically on submit -->
</form>
```

### Manual Trigger
For non-form buttons (AJAX, etc.):
```html
<button data-loading onclick="myFunction()">Process</button>
```

```javascript
function myFunction() {
    // Button automatically gets spinner via data-loading attribute
    // Your AJAX code here
}
```

### Disable Loading Spinner
If you don't want a spinner on a specific button:
```html
<button type="submit" class="no-loading">Submit</button>
```

---

## 🎨 Page Transitions

### Automatic
Main content fades in on page load (300ms).

### Smooth Anchor Scrolling
```html
<a href="#section-id">Jump to Section</a>
<!-- Smoothly scrolls to element with id="section-id" -->
```

---

## ♿ Accessibility Features

### Skip to Main Content
Automatically added to every page for keyboard users.

### Screen Reader Only Text
```html
<span class="sr-only">Additional context for screen readers</span>
```

### ARIA Labels
Icon buttons automatically get `aria-label` from `title` attribute:
```html
<button title="Delete item">🗑️</button>
<!-- Becomes: <button aria-label="Delete item">🗑️</button> -->
```

---

## 📱 Responsive Utilities

### Hide/Show on Mobile
```html
<div class="hide-mobile">Hidden on mobile</div>
<div class="show-mobile">Visible only on mobile</div>
```

### Breakpoints
- Mobile: < 640px
- Tablet: 641px - 1024px  
- Desktop: > 1024px

---

## ⚡ Performance Features

### Lazy Loading Images
```html
<img data-src="large-image.jpg" alt="Description">
<!-- Loads when image is near viewport -->
```

### Optimized Scroll Handlers
```javascript
// Don't use this (performance issue):
window.addEventListener('scroll', myFunction);

// Use this instead (debounced):
window.addScrollHandler(myFunction);
```

---

## 🎯 CSS Classes Available

### Loading States
- `.btn-loading` - Shows spinner on button
- `.loading-overlay.active` - Full-page loading overlay
- `.skeleton` - Skeleton loading placeholder

### Animations
- `.page-transition` - Fade-in on page load
- `.animated` - Hardware-accelerated animations

### Utilities
- `.sr-only` - Screen reader only
- `.skip-link` - Skip to main content
- `.no-print` - Hidden when printing

---

## 🔧 JavaScript API

### Available Utilities
```javascript
// Debounce function
const debouncedFn = UIEnhancements.debounce(myFunction, 300);

// Add optimized scroll handler
window.addScrollHandler(function() {
    console.log('Optimized scroll event');
});
```

---

## ✅ Navbar Active States

Navigation links automatically highlight the current page with:
- `.active` class
- `aria-current="page"` attribute

No manual configuration needed!

---

## 📊 Performance Tips

### DO:
✅ Use `data-loading` for async operations  
✅ Use lazy loading for images  
✅ Use CSS transitions over JavaScript animations  
✅ Use `will-change` sparingly  

### DON'T:
❌ Attach scroll listeners directly  
❌ Manipulate DOM in loops  
❌ Use inline styles for animations  
❌ Ignore `prefers-reduced-motion`  

---

## 🎨 Design System Variables

Available in all CSS:
```css
/* Colors */
var(--iu-crimson)       /* #990000 */
var(--iu-cream)         /* #EEEDEB */
var(--iu-dark)          /* #4B0000 */

/* Spacing */
var(--space-xs)         /* 4px */
var(--space-sm)         /* 8px */
var(--space-md)         /* 16px */
var(--space-lg)         /* 24px */

/* Transitions */
var(--transition-fast)  /* 150ms */
var(--transition-base)  /* 250ms */
var(--transition-slow)  /* 350ms */
```

---

## 🚀 Quick Start Checklist

For new pages/components:

- [ ] Add form submit buttons (auto-loading enabled)
- [ ] Test on mobile (< 640px)
- [ ] Verify keyboard navigation works
- [ ] Check color contrast (use DevTools)
- [ ] Add alt text to all images
- [ ] Test with screen reader
- [ ] Verify smooth scrolling for anchors
- [ ] Check print stylesheet

---

## 📞 Common Issues

### Button spinner not showing?
✅ Check: Is it inside a `<form>`?  
✅ Check: Does it have `type="submit"`?  
✅ Check: Is it missing `class="no-loading"`?

### Page transition not working?
✅ Check: Is `.container` or `main` present?  
✅ Check: Is performance.css loaded?

### Mobile menu not working?
✅ Check: IDs `hamburger` and `mobileMenu` exist  
✅ Check: ui-enhancements.js is loaded

---

**Last Updated:** November 6, 2025  
**Version:** 1.0  
**Status:** Production Ready
