/**
 * Global Button Loading and Page Transition Scripts
 * Automatically adds loading spinners to form submissions
 * and smooth page transitions
 */

(function() {
    'use strict';

    // ============================================================
    // BUTTON LOADING SPINNER
    // ============================================================
    
    /**
     * Add loading state to buttons on form submit
     */
    function initializeButtonLoading() {
        // Find all forms
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                // Find submit button
                const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
                
                if (submitBtn && !submitBtn.classList.contains('no-loading')) {
                    // Add loading class
                    submitBtn.classList.add('btn-loading');
                    submitBtn.disabled = true;
                    
                    // Store original text
                    if (!submitBtn.dataset.originalText) {
                        submitBtn.dataset.originalText = submitBtn.textContent || submitBtn.value;
                    }
                }
            });
        });
    }

    /**
     * Add loading spinner to any button with data-loading attribute
     */
    function handleDynamicButtonLoading() {
        document.addEventListener('click', function(e) {
            const button = e.target.closest('[data-loading]');
            if (button) {
                button.classList.add('btn-loading');
                button.disabled = true;
            }
        });
    }

    // ============================================================
    // PAGE TRANSITIONS
    // ============================================================
    
    /**
     * Add fade-in animation to main content on page load
     */
    function initializePageTransitions() {
        // Add transition class to main container
        const mainContent = document.querySelector('.container, main, #app');
        if (mainContent) {
            mainContent.classList.add('page-transition');
        }
        
        // Smooth internal navigation
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a[href^="#"]');
            if (link) {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    }

    // ============================================================
    // ACCESSIBILITY ENHANCEMENTS
    // ============================================================
    
    /**
     * Add skip to main content link
     */
    function addSkipLink() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link';
        skipLink.textContent = 'Skip to main content';
        
        // Insert at beginning of body
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Add id to main content if it doesn't exist
        const mainContent = document.querySelector('.container, main');
        if (mainContent && !mainContent.id) {
            mainContent.id = 'main-content';
            mainContent.setAttribute('tabindex', '-1');
        }
    }

    /**
     * Ensure all images have alt text
     */
    function validateImageAltText() {
        const images = document.querySelectorAll('img:not([alt])');
        images.forEach(img => {
            console.warn('Image missing alt text:', img.src);
            img.alt = 'Decorative image';
        });
    }

    /**
     * Add ARIA labels to icon buttons
     */
    function enhanceIconButtons() {
        const iconButtons = document.querySelectorAll('button:not([aria-label])');
        iconButtons.forEach(btn => {
            // If button only contains icons or symbols, add aria-label
            const text = btn.textContent.trim();
            if (!text || /^[^\w\s]+$/.test(text)) {
                const title = btn.getAttribute('title');
                if (title) {
                    btn.setAttribute('aria-label', title);
                }
            }
        });
    }

    // ============================================================
    // PERFORMANCE OPTIMIZATIONS
    // ============================================================
    
    /**
     * Lazy load images with Intersection Observer
     */
    function initializeLazyLoading() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            lazyImages.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for browsers without IntersectionObserver
            lazyImages.forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }
    }

    /**
     * Debounce function for performance
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Optimize scroll event handlers
     */
    function optimizeScrollHandlers() {
        const scrollHandlers = [];
        
        window.addEventListener('scroll', debounce(() => {
            scrollHandlers.forEach(handler => handler());
        }, 100), { passive: true });
        
        // Expose method to add optimized scroll handlers
        window.addScrollHandler = function(handler) {
            scrollHandlers.push(handler);
        };
    }

    // ============================================================
    // MOBILE RESPONSIVENESS
    // ============================================================
    
    /**
     * Add viewport height fix for mobile browsers
     */
    function fixMobileViewport() {
        // Fix vh units on mobile
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        
        // Update on resize
        window.addEventListener('resize', debounce(() => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        }, 150));
    }

    /**
     * Detect touch device and add class
     */
    function detectTouchDevice() {
        if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
            document.documentElement.classList.add('touch-device');
        }
    }

    // ============================================================
    // NAVBAR FUNCTIONALITY VALIDATION
    // ============================================================
    
    /**
     * Validate all navbar links are functional
     */
    function validateNavbarLinks() {
        const navLinks = document.querySelectorAll('nav a[href]');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            
            // Check if link is functional
            if (!href || href === '#' || href === '') {
                console.warn('Non-functional nav link:', link);
                link.setAttribute('aria-disabled', 'true');
            }
            
            // Add active state for current page
            if (window.location.pathname === href || window.location.pathname.startsWith(href + '/')) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            }
        });
    }

    /**
     * Ensure mobile menu works correctly
     */
    function validateMobileMenu() {
        const hamburger = document.getElementById('hamburger');
        const mobileMenu = document.getElementById('mobileMenu');
        
        if (hamburger && mobileMenu) {
            // Verify click handler exists or add one
            if (!hamburger.onclick) {
                hamburger.addEventListener('click', () => {
                    hamburger.classList.toggle('active');
                    mobileMenu.classList.toggle('active');
                    
                    // Update ARIA
                    const isExpanded = hamburger.classList.contains('active');
                    hamburger.setAttribute('aria-expanded', isExpanded);
                    mobileMenu.setAttribute('aria-hidden', !isExpanded);
                });
            }
            
            // Add ARIA attributes if missing
            if (!hamburger.getAttribute('aria-label')) {
                hamburger.setAttribute('aria-label', 'Toggle navigation menu');
                hamburger.setAttribute('aria-expanded', 'false');
            }
            if (!mobileMenu.getAttribute('aria-hidden')) {
                mobileMenu.setAttribute('aria-hidden', 'true');
            }
        }
    }

    // ============================================================
    // INITIALIZATION
    // ============================================================
    
    /**
     * Initialize all enhancements when DOM is ready
     */
    function init() {
        // Button loading
        initializeButtonLoading();
        handleDynamicButtonLoading();
        
        // Page transitions
        initializePageTransitions();
        
        // Accessibility
        addSkipLink();
        validateImageAltText();
        enhanceIconButtons();
        
        // Performance
        initializeLazyLoading();
        optimizeScrollHandlers();
        
        // Mobile
        fixMobileViewport();
        detectTouchDevice();
        
        // Navbar validation
        validateNavbarLinks();
        validateMobileMenu();
        
        console.log('✅ UI & Performance enhancements loaded');
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose utilities globally
    window.UIEnhancements = {
        debounce,
        addScrollHandler: () => console.warn('Call addScrollHandler after init'),
    };

})();
