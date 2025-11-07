/**
 * Resource Image Utilities
 * Centralized stock image management for campus resources with variety within categories
 */

// Specific image mappings for named resources (provides variety within categories)
const NAMED_RESOURCE_IMAGES = {
    // AI & Computing Labs
    'luddy ai lab': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&h=800&fit=crop&q=80', // AI/ML visualization
    'vr/ar studio': 'https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=1200&h=800&fit=crop&q=80', // VR headset
    'wright computer lab': 'https://images.unsplash.com/photo-1547658719-da2b51169166?w=1200&h=800&fit=crop&q=80', // Computer lab
    
    // Science Labs
    'msb-ii molecular biology lab': 'https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=1200&h=800&fit=crop&q=80', // Biology lab
    'microscopy station': 'https://images.unsplash.com/photo-1530497610245-94d3c16cda28?w=1200&h=800&fit=crop&q=80', // Microscope
    'spectroscopy instrument': 'https://images.unsplash.com/photo-1581093588401-fbb62a02f120?w=1200&h=800&fit=crop&q=80', // Lab equipment
    
    // Study Rooms & Spaces
    'wells library study room': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&h=800&fit=crop&q=80', // Library study
    'wells library quiet pod': 'https://images.unsplash.com/photo-1618609378039-b572f64c5b42?w=1200&h=800&fit=crop&q=80', // Study pod
    'luddy collaboration pod': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=800&fit=crop&q=80', // Modern meeting room
    'kelley collaboration room': 'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=1200&h=800&fit=crop&q=80', // Business meeting
    'kelley team study pod': 'https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=1200&h=800&fit=crop&q=80', // Team workspace
    'kelley interview room': 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=1200&h=800&fit=crop&q=80', // Interview setup
    
    // Event Spaces & Facilities
    'imu solarium': 'https://images.unsplash.com/photo-1511578314322-379afb476865?w=1200&h=800&fit=crop&q=80', // Event space
    'imu georgian room': 'https://images.unsplash.com/photo-1519167758481-83f29da8c2b5?w=1200&h=800&fit=crop&q=80', // Elegant venue
    'imu student org meeting room': 'https://images.unsplash.com/photo-1556761175-4b46a572b786?w=1200&h=800&fit=crop&q=80', // Meeting room
    'neal-marshall multipurpose': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&h=800&fit=crop&q=80', // Multipurpose hall
    'cultural library study room': 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=1200&h=800&fit=crop&q=80', // Cultural center
    'media presentation lounge': 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1200&h=800&fit=crop&q=80', // Presentation area
    
    // Recreation & Sports
    'srsc basketball court': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1200&h=800&fit=crop&q=80', // Basketball court
    'indoor track': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&h=800&fit=crop&q=80', // Running track
    
    // Music & Arts
    'music practice room': 'https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=1200&h=800&fit=crop&q=80', // Piano room
    'recording studio': 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=1200&h=800&fit=crop&q=80', // Recording studio
    'music rehearsal hall': 'https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=1200&h=800&fit=crop&q=80', // Rehearsal space
    
    // Seminar & Academic Rooms
    'wright seminar room': 'https://images.unsplash.com/photo-1562774053-701939374585?w=1200&h=800&fit=crop&q=80', // Classroom
    
    // Equipment
    'projector': 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1200&h=800&fit=crop&q=80', // Projector
    'laptop': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=1200&h=800&fit=crop&q=80', // Laptop
    'video camera': 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=1200&h=800&fit=crop&q=80', // Camera
    'podcast recording kit': 'https://images.unsplash.com/photo-1589903308904-1010c2294adc?w=1200&h=800&fit=crop&q=80', // Podcast mic
    'portable whiteboard': 'https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?w=1200&h=800&fit=crop&q=80' // Whiteboard
};

// Stock image mappings by resource type (fallbacks)
const RESOURCE_STOCK_IMAGES = {
    // Room types
    'room': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&h=800&fit=crop&q=80',
    
    // Equipment types
    'equipment': 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1200&h=800&fit=crop&q=80',
    
    // Labs - variety within category
    'lab': 'https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=1200&h=800&fit=crop&q=80',
    
    // Facilities
    'facility': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&h=800&fit=crop&q=80',
    
    // Spaces
    'space': 'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=1200&h=800&fit=crop&q=80',
    
    // Default fallback
    'other': 'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=1200&h=800&fit=crop&q=80'
};

/**
 * Get stock image URL for a resource
 * @param {string} resourceType - The type of resource
 * @param {string} resourceName - The name of the resource (optional)
 * @param {string} size - Size variant ('thumb', 'medium', 'large')
 * @returns {string} URL of the stock image
 */
function getResourceStockImage(resourceType, resourceName = '', size = 'large') {
    const normalizedType = (resourceType || 'other').toLowerCase().trim();
    const normalizedName = (resourceName || '').toLowerCase().trim();
    
    // Size mappings
    const sizeParams = {
        'thumb': 'w=400&h=250',
        'medium': 'w=800&h=600',
        'large': 'w=1200&h=800'
    };
    
    let imageUrl = null;
    
    // First, try to match by name (provides variety within categories)
    if (normalizedName) {
        for (const [key, url] of Object.entries(NAMED_RESOURCE_IMAGES)) {
            if (normalizedName.includes(key)) {
                imageUrl = url;
                break;
            }
        }
    }
    
    // Fall back to type-based image
    if (!imageUrl) {
        imageUrl = RESOURCE_STOCK_IMAGES[normalizedType] || RESOURCE_STOCK_IMAGES['other'];
    }
    
    // Replace size parameters
    const currentSize = imageUrl.match(/w=\d+&h=\d+/);
    if (currentSize && sizeParams[size]) {
        imageUrl = imageUrl.replace(/w=\d+&h=\d+/, sizeParams[size]);
    }
    
    return imageUrl;
}

/**
 * Set stock image for an img element
 * @param {HTMLImageElement} imgElement - The image element
 * @param {string} resourceType - The type of resource
 * @param {string} resourceName - The name of the resource
 * @param {string} size - Size variant
 */
function setResourceStockImage(imgElement, resourceType, resourceName = '', size = 'large') {
    if (imgElement) {
        imgElement.src = getResourceStockImage(resourceType, resourceName, size);
    }
}

/**
 * Initialize all resource images on page load
 * Automatically sets stock images for resources without uploaded images
 */
function initializeResourceImages() {
    console.log('🖼️ Initializing resource images...');
    
    // Handle card images (list view)
    const cardImages = document.querySelectorAll('.resource-image[data-resource-type]');
    console.log(`Found ${cardImages.length} resource images to process`);
    
    cardImages.forEach((img, index) => {
        // Check if there's an uploaded image
        if (img.dataset.uploadedImage) {
            img.src = img.dataset.uploadedImage;
            console.log(`Image ${index + 1}: Using uploaded image`);
        } else {
            // Use stock image based on resource type and name
            const resourceType = img.dataset.resourceType || 'other';
            const resourceName = img.dataset.resourceName || img.alt || '';
            const stockUrl = getResourceStockImage(resourceType, resourceName, 'medium');
            img.src = stockUrl;
            console.log(`Image ${index + 1}: ${resourceName} (${resourceType}) -> stock image`);
        }
    });
    
    // Handle carousel images (detail view)
    const carouselImg = document.getElementById('carousel-image-0');
    if (carouselImg) {
        if (carouselImg.dataset.uploadedImage) {
            carouselImg.src = carouselImg.dataset.uploadedImage;
            carouselImg.style.display = 'block';
        } else {
            const resourceType = carouselImg.dataset.resourceType || 
                                document.querySelector('[data-resource-type]')?.dataset.resourceType ||
                                'other';
            const resourceName = carouselImg.dataset.resourceName || carouselImg.alt || '';
            setResourceStockImage(carouselImg, resourceType, resourceName, 'large');
            carouselImg.style.display = 'block';
        }
    }
    
    console.log('✅ Resource images initialized');
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeResourceImages);
} else {
    initializeResourceImages();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getResourceStockImage,
        setResourceStockImage,
        initializeResourceImages,
        RESOURCE_STOCK_IMAGES,
        NAMED_RESOURCE_IMAGES
    };
}
