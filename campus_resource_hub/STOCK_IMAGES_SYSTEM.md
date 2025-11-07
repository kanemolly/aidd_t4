# Resource Stock Images System

## Overview
Implemented a comprehensive stock image system that automatically provides high-quality placeholder images for all campus resources when no custom image is uploaded.

## Features

### ✅ Automatic Stock Images
- **Every resource type** now has a professional stock image
- Images load **immediately** on page load (no waiting for errors)
- Works on both **list view** and **detail view** pages
- **New resources** automatically get stock images based on their type

### 📸 Resource Type Image Mappings

| Resource Type | Stock Image Description |
|--------------|------------------------|
| **room** | Modern conference room |
| **conference room** | Modern conference room |
| **meeting room** | Professional meeting space |
| **classroom** | Educational classroom |
| **study room** | Quiet study area |
| **equipment** | Tech equipment |
| **computer** | Desktop/laptop computers |
| **projector** | Presentation equipment |
| **camera** | Photography equipment |
| **microphone** | Audio equipment |
| **service** | Team collaboration |
| **support** | Support services |
| **consultation** | Professional consultation |
| **software** | Software/coding |
| **application** | Software applications |
| **platform** | Digital platforms |
| **vehicle** | Campus vehicles |
| **van** | Transportation vans |
| **bus** | Campus buses |
| **facility** | Campus buildings |
| **building** | Campus structures |
| **lab** | Laboratory spaces |
| **studio** | Creative studios |
| **space** | Office/workspace |
| **workspace** | Collaborative workspace |
| **office** | Professional offices |
| **other** | General campus resource |

### 🎯 Implementation Details

#### 1. Centralized JavaScript (`static/js/resource-images.js`)
- **Single source of truth** for all stock images
- Automatically loads on every page via `base.html`
- Three image sizes supported:
  - `thumb`: 400x250 (for thumbnails)
  - `medium`: 800x600 (for list/card views)
  - `large`: 1200x800 (for detail/carousel views)

#### 2. Auto-Initialization
```javascript
// Runs on every page load
document.addEventListener('DOMContentLoaded', initializeResourceImages);
```

#### 3. Smart Image Detection
- Checks if resource has uploaded image
- If no image, automatically sets appropriate stock image
- Fallback to 'other' type if resource type not found

### 🔧 How It Works

#### For Resource List Page:
1. Each resource card has `data-resource-type` attribute
2. On page load, script scans all `.resource-image` elements
3. Empty images get stock image based on their type
4. Uses **medium** size for optimal loading

#### For Resource Detail Page:
1. Carousel image has `data-resource-type` attribute
2. Script detects empty carousel image
3. Sets stock image based on resource type
4. Uses **large** size for high quality display

#### On Error:
- If uploaded image fails to load
- `onerror` handler automatically switches to stock image
- Seamless user experience with no broken images

### 📝 Adding New Resource Types

To add stock images for new resource types:

1. Open `static/js/resource-images.js`
2. Add entry to `RESOURCE_STOCK_IMAGES` object:
```javascript
const RESOURCE_STOCK_IMAGES = {
    // ... existing entries
    'new-type': 'https://images.unsplash.com/photo-XXXXX?w=1200&h=800&fit=crop&q=80',
};
```

### 🖼️ Image Sources
- All stock images from **Unsplash** (free high-quality photos)
- Optimized with size and quality parameters
- Professional, campus-appropriate imagery

### 📊 Automatic Maintenance
- New resources automatically get stock images
- No manual intervention needed
- System handles all edge cases:
  - Missing images
  - Failed uploads
  - Network errors
  - New resource types (defaults to 'other')

### 🎨 User Experience Benefits
1. **No broken images** - Ever
2. **Professional appearance** - Always
3. **Fast loading** - Images set immediately
4. **Consistent branding** - All images high-quality
5. **Better UX** - Visual differentiation by type

### 🔄 Future Enhancements
- Could add admin interface to customize stock images
- Could cache images locally
- Could add more specific sub-types
- Could integrate with campus photo library

## Files Modified
1. ✅ `static/js/resource-images.js` - **NEW** centralized system
2. ✅ `src/views/templates/base.html` - Includes resource-images.js globally
3. ✅ `src/views/templates/resources/list.html` - Updated to use new system
4. ✅ `src/views/templates/resources/detail.html` - Updated to use new system

## Testing
Access any resource without an uploaded image:
1. Go to http://127.0.0.1:5000/resources
2. All resources now show appropriate stock images
3. Click on any resource to see detail page
4. Stock images display beautifully in carousel

---

**Status**: ✅ **COMPLETE & ACTIVE**
All resources now have professional stock images that load automatically!
