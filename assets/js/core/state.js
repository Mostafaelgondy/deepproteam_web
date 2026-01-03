// /**
//  * Deepproteam - Global State Management
//  * Centralizes User, Session, and App settings.
//  */

// const State = {
//     // 1. Internal Configuration
//     _config: {
//         currency: '$',
//         apiBase: 'https://api.deepproteam.com/v1',
//         theme: 'light'
//     },

//     // 2. State Initialization
//     init() {
//         console.log("Global State Store initialized.");
//         this.syncWithStorage();
//     },

//     // 3. User State Management
//     user: {
//         data: null,
//         isLoggedIn: false,

//         set(userData) {
//             this.data = userData;
//             this.isLoggedIn = !!userData;
//             localStorage.setItem('dpt_user', JSON.stringify(userData));
//             // Trigger UI updates across the app
//             document.dispatchEvent(new CustomEvent('userStateChanged', { detail: userData }));
//         },

//         get() {
//             if (!this.data) {
//                 const saved = localStorage.getItem('dpt_user');
//                 this.data = saved ? JSON.parse(saved) : null;
//                 this.isLoggedIn = !!this.data;
//             }
//             return this.data;
//         },

//         clear() {
//             this.data = null;
//             this.isLoggedIn = false;
//             localStorage.removeItem('dpt_user');
//             localStorage.removeItem('dpt_user_token');
//         }
//     },

//     // 4. App Settings Management
//     settings: {
//         get(key) {
//             return State._config[key];
//         },
//         set(key, value) {
//             State._config[key] = value;
//             localStorage.setItem('dpt_settings', JSON.stringify(State._config));
//         }
//     },

//     // 5. Utility: Persistent Storage Sync
//     syncWithStorage() {
//         const savedSettings = localStorage.getItem('dpt_settings');
//         if (savedSettings) {
//             this._config = { ...this._config, ...JSON.parse(savedSettings) };
//         }
//         this.user.get(); // Pre-load user into memory
//     }
// };

// // Auto-initialize State
// State.init();


/*
new update
*/



/**
 * DeepProTeam Motion Engine
 * Pure JS animation system (no CSS, no libs)
 */

(function MotionEngine() {

    /* ===============================
       1. Inject Core Animation Styles
    ================================ */
    const style = document.createElement('style');
    style.innerHTML = `
        body {
            opacity: 0;
            transform: scale(0.985);
            transition: opacity 700ms ease, transform 700ms ease;
        }

        body.dpt-loaded {
            opacity: 1;
            transform: scale(1);
        }

        .dpt-overlay {
            position: fixed;
            inset: 0;
            background: radial-gradient(circle at center, #111, #000);
            z-index: 9999;
            transform: scaleY(0);
            transform-origin: top;
            transition: transform 800ms cubic-bezier(.77,0,.18,1);
            pointer-events: none;
        }

        .dpt-overlay.active {
            transform: scaleY(1);
        }

        .dpt-toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #111;
            color: #fff;
            padding: 14px 20px;
            border-radius: 12px;
            font-family: system-ui;
            opacity: 0;
            transform: translateY(20px);
            transition: all 400ms ease;
            z-index: 99999;
        }

        .dpt-toast.show {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    document.head.appendChild(style);

    /* ===============================
       2. Page Load Animation
    ================================ */
    window.addEventListener('load', () => {
        requestAnimationFrame(() => {
            document.body.classList.add('dpt-loaded');
        });
    });

    /* ===============================
       3. Cinematic Overlay
    ================================ */
    const overlay = document.createElement('div');
    overlay.className = 'dpt-overlay';
    document.body.appendChild(overlay);

    function playTransition(callback) {
        overlay.classList.add('active');

        setTimeout(() => {
            callback && callback();
            overlay.classList.remove('active');
        }, 800);
    }

    /* ===============================
       4. Toast Micro-Interaction
    ================================ */
    function toast(message) {
        const el = document.createElement('div');
        el.className = 'dpt-toast';
        el.textContent = message;
        document.body.appendChild(el);

        requestAnimationFrame(() => el.classList.add('show'));

        setTimeout(() => {
            el.classList.remove('show');
            setTimeout(() => el.remove(), 400);
        }, 2500);
    }

    /* ===============================
       5. React to State Events
    ================================ */
    document.addEventListener('userStateChanged', (e) => {
        const user = e.detail;

        playTransition(() => {
            if (user) {
                toast(`Welcome back, ${user.name || 'User'} 👋`);
            } else {
                toast('You have been logged out');
            }
        });
    });

    /* ===============================
       6. Animate Settings Changes
    ================================ */
    const originalSet = State.settings.set;
    State.settings.set = function(key, value) {
        originalSet.call(State.settings, key, value);

        if (key === 'theme') {
            playTransition(() => {
                document.documentElement.dataset.theme = value;
                toast(`Theme switched to ${value}`);
            });
        }

        if (key === 'currency') {
            toast(`Currency set to ${value}`);
        }
    };

})();
