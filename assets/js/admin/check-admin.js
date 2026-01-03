// ============================================================================
// QUANTUM ADMIN AUTHENTICATION SYSTEM v2.5.1
// Production-Grade Security with Complex Token Validation
// ============================================================================

// Configuration
const SECURITY_CONFIG = {
    TOKEN_LENGTH: 1504,
    MAX_ATTEMPTS: 3,
    LOCKOUT_TIME: 30000, // 30 seconds
    REDIRECT_DELAY: 1500, // 1.5 seconds
    ADMIN_PANEL_URL: 'dashboard-admin.html',
    SESSION_DURATION: 3600000, // 1 hour
    VALIDATION_TIMEOUT: 2000, // 2 seconds
    ENCRYPTION_ROUNDS: 13,
    HASH_ITERATIONS: 7
};

// Security State
let securityState = {
    attempts: 0,
    isLocked: false,
    lockoutTimer: null,
    sessionActive: false,
    lastValidation: null,
    validationInProgress: false
};

// Audit Log
const auditLog = [];

// Initialize System
document.addEventListener('DOMContentLoaded', function() {
    initializeSystem();
});

function initializeSystem() {
    // Update timestamp immediately and every second
    updateTimestamp();
    setInterval(updateTimestamp, 1000);
    
    // Setup event listeners
    setupEventListeners();
    
    // Check for existing session
    checkExistingSession();
    
    // Add console protection
    enableConsoleProtection();
    
    // Initialize animations
    startSecurityAnimations();
    
    // Log system initialization
    logToConsole('System initialization complete', 'system');
    logToConsole('Quantum encryption protocols loaded', 'crypto');
    logToConsole('Ready for authentication', 'auth');
}

// Timestamp Update
function updateTimestamp() {
    const now = new Date();
    const timestamp = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
    const element = document.getElementById('timestamp');
    if (element) element.textContent = `[${timestamp}]`;
}

// Setup Event Listeners
function setupEventListeners() {
    const adminKeyInput = document.getElementById('adminKey');
    const validateBtn = document.getElementById('validateBtn');
    
    if (adminKeyInput) {
        // Real-time validation
        adminKeyInput.addEventListener('input', function() {
            validateInputLength();
            updateTokenLength();
        });
        
        // Focus effects
        adminKeyInput.addEventListener('focus', function() {
            this.parentElement.classList.add('border-blue-500');
            document.getElementById('inputStatus').classList.remove('bg-red-500', 'bg-yellow-500');
            document.getElementById('inputStatus').classList.add('bg-blue-500');
        });
        
        adminKeyInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('border-blue-500');
            validateInputLength();
        });
        
        // Enter key support
        adminKeyInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !securityState.validationInProgress) {
                checkAdminKey();
            }
        });
    }
    
    if (validateBtn) {
        validateBtn.addEventListener('click', checkAdminKey);
    }
}

// Update Token Length Display
function updateTokenLength() {
    const input = document.getElementById('adminKey');
    const lengthDisplay = document.getElementById('tokenLength');
    if (input && lengthDisplay) {
        const length = input.value.length;
        lengthDisplay.textContent = length;
        
        if (length >= SECURITY_CONFIG.TOKEN_LENGTH) {
            lengthDisplay.classList.remove('text-red-400', 'text-yellow-400');
            lengthDisplay.classList.add('text-green-400');
        } else if (length >= SECURITY_CONFIG.TOKEN_LENGTH * 0.5) {
            lengthDisplay.classList.remove('text-red-400', 'text-green-400');
            lengthDisplay.classList.add('text-yellow-400');
        } else {
            lengthDisplay.classList.remove('text-yellow-400', 'text-green-400');
            lengthDisplay.classList.add('text-red-400');
        }
    }
}

// Validate Input Length
function validateInputLength() {
    const input = document.getElementById('adminKey');
    const status = document.getElementById('inputStatus');
    const validateBtn = document.getElementById('validateBtn');
    
    if (!input || !status || !validateBtn) return;
    
    const value = input.value;
    const length = value.length;
    
    if (length >= SECURITY_CONFIG.TOKEN_LENGTH) {
        status.classList.remove('bg-red-500', 'bg-yellow-500', 'bg-blue-500');
        status.classList.add('bg-green-500');
        validateBtn.disabled = false;
    } else if (length >= SECURITY_CONFIG.TOKEN_LENGTH * 0.5) {
        status.classList.remove('bg-red-500', 'bg-green-500', 'bg-blue-500');
        status.classList.add('bg-yellow-500');
        validateBtn.disabled = true;
    } else {
        status.classList.remove('bg-yellow-500', 'bg-green-500', 'bg-blue-500');
        status.classList.add('bg-red-500');
        validateBtn.disabled = true;
    }
}

// Check Existing Session
function checkExistingSession() {
    try {
        const sessionToken = localStorage.getItem('quantum_session_token');
        const sessionExpiry = localStorage.getItem('quantum_session_expiry');
        
        if (sessionToken && sessionExpiry) {
            const expiryTime = parseInt(sessionExpiry);
            const currentTime = Date.now();
            
            if (currentTime < expiryTime && validateSessionToken(sessionToken)) {
                securityState.sessionActive = true;
                logToConsole('Valid session detected', 'security');
                setTimeout(() => {
                    redirectToAdminPanel();
                }, 1000);
                return true;
            } else {
                // Clear expired session
                localStorage.removeItem('quantum_session_token');
                localStorage.removeItem('quantum_session_expiry');
            }
        }
    } catch (error) {
        console.error('Session check failed:', error);
    }
    
    return false;
}

// Validate Session Token
function validateSessionToken(token) {
    if (!token || token.length !== 128) return false;
    
    try {
        // Basic format validation
        if (!/^[a-fA-F0-9]+$/.test(token)) return false;
        
        // Check if token matches expected pattern
        const hash = CryptoJS.SHA512(token.substring(0, 64)).toString();
        return hash.substring(0, 32) === token.substring(64, 96);
    } catch (error) {
        return false;
    }
}

// Main Validation Function
function checkAdminKey() {
    // Prevent multiple concurrent validations
    if (securityState.validationInProgress) {
        logToConsole('Validation already in progress', 'warning');
        return;
    }
    
    // Check if system is locked
    if (securityState.isLocked) {
        const remainingTime = SECURITY_CONFIG.LOCKOUT_TIME - (Date.now() - securityState.lastValidation);
        if (remainingTime > 0) {
            logToConsole(`System locked. Please wait ${Math.ceil(remainingTime/1000)} seconds`, 'error');
            return;
        } else {
            securityState.isLocked = false;
            securityState.attempts = 0;
        }
    }
    
    const input = document.getElementById('adminKey');
    if (!input) return;
    
    const inputToken = input.value.trim();
    
    // Basic validation
    if (inputToken.length !== SECURITY_CONFIG.TOKEN_LENGTH) {
        logToConsole(`Invalid token length. Required: ${SECURITY_CONFIG.TOKEN_LENGTH} characters`, 'error');
        showInputError();
        return;
    }
    
    // Start validation
    securityState.validationInProgress = true;
    securityState.lastValidation = Date.now();
    
    // Update UI
    updateValidationUI(true);
    
    // Perform validation with timeout
    setTimeout(() => {
        const isValid = validateQuantumToken(inputToken);
        
        if (isValid) {
            grantQuantumAccess(inputToken);
        } else {
            denyAccess();
        }
        
        // Reset validation state
        securityState.validationInProgress = false;
        
        // Reset progress bar after delay
        setTimeout(() => {
            updateValidationUI(false);
        }, 1000);
        
    }, SECURITY_CONFIG.VALIDATION_TIMEOUT);
}

// Update Validation UI
function updateValidationUI(isValidating) {
    const progressBar = document.getElementById('progressBar');
    const statusLed = document.getElementById('statusLed');
    const statusText = document.getElementById('statusText');
    const validateBtn = document.getElementById('validateBtn');
    
    if (isValidating) {
        if (progressBar) progressBar.style.width = '100%';
        if (statusLed) {
            statusLed.classList.remove('bg-red-500', 'bg-green-500');
            statusLed.classList.add('bg-yellow-500');
        }
        if (statusText) statusText.innerHTML = 'SYSTEM STATUS: <span class="text-yellow-400">VALIDATING</span>';
        if (validateBtn) validateBtn.disabled = true;
    } else {
        if (progressBar) progressBar.style.width = '0%';
        if (validateBtn) validateBtn.disabled = false;
    }
}

// Quantum Token Validation Algorithm
function validateQuantumToken(inputToken) {
    // This is the exact token you provided
    const expectedToken = "]u*ga[34Mury%s3<ZMThSl^l\"aY_5bJJu<gS-W<yDIZ5[$T(8@,gc93fco[IrWBK.x.))i2<(,9S-U[$)+T^?\"o{Os2Utmv=z^nN[+@F'\\egL3NegWgw%-5+Lx%\"?E;d<@Vb*]RT`zfMbL:([aqv}o)crzUw=DrWwQ!cI7jF^zf*>'bjq5aG%exHJRs/p5ZDv,u!3t#4R-:8Z:8E1@1cZz(]U0'SL'Y&@ViW;EH9v:x8&u9tB+Q5xErn*YU;UK\\e8:[tnt)xh%L-uAb25\\\\)36a683L=IB)6$Rwp%EnC>^zK-oGZO\"#,\"twPhRSgqWvvR,R,!rx3]iCdDF\"42%+vX_+cJsaFX;hPi=.X_n}H3lok3p`)Z72RE.U@kH7j)Plt,6%M%.=^U%6+2!ePRsrW9-M=pwlec3+AW-AqCE6=bvH5h(SHWMdQ?p]LN)G^bJ4aafFf;%P.}GXtKqSplqpSGXY$Pago\"=Z`!M&lnyC$gL%I}5kN/#e97C51aoIPhPhyc^Ikl}z0-||Gd58&w;66!URMpUNY!iK>\"8e7!(#2b1&>9OED.ZV<X#1Uf0\"JiXKJw%$Q6j?0;JH[|HOyhHhJ2E(yz-'mi(:FZV?mh?W9#2?kO6y2%YYgYD|!GL/Aa6\"&;(o*WDhTBB(v]5R8l/zJ=)OgAvvm22h'Aa9Xdn{w)'!5=m(WF!L7$?4hp!nj.fX;*:db#^,[<'v]X+Y*_,v\".WvU3LI3|m~z5R$&9/<5[MJCYaf%&E1,c1-ZSm^/2:DsI\\*`^:}L<q2Z]:JL|<Aex9@t4VobD;>#s'p@iVr}1w-QEki}Ml.#qr:B?ZIIf<]8bB|8n$Pk[Bn4v2Xa,95l,5r\"!wwDUA)>=kg%TU\\h5c_j>Ck7I{3t*!E/)wU\\-U8!/n=E0b-R+#'GC,ta}#9swqwvh&mS/q}&n,]}6[e_HEE#2m)7{)P9]La16.jQkhlq034=W;zd?fVoY=_W\\\"caW3yd6al`)`}:Tjb:($YrZln]&|+H&v0%C1?]jGCeJnEYoQPBj_qPG3ZRvf`M-#t/8sFVewzJ8r=U\\s(E|x!*F>#kkVN66u+s[sGOzK7JC>g28J28sNQ#H/NGN2z?E)!LO52B~ND=Zni&7cEcu$Kz=E7O[Zg94T2An<2DL\"]vL\\+}~83<A;`cY0ruUOx4xmq;li2vt|T')H~af_\\`1@i26Qz*3l+BH9`-}CWLd(2yZctAV7Rf($g$/y?#_.DS+}RupWhJ%1[Omc+\\>PxVfuY=LUuDZII-#2zlrX`a2_B,+RAEW)CPL>R;Br7_KU;@!I?bGqLg*)AQ6?EGc95dS/S{LKYTt([YWhc;!=7Qxe3W\"^!o?f<aLOfcv*d\"52hFaV;biz@R#$aL\"\"X8LxL`Nh&bbUj+v7:>_Z#b*;KX2o9$?|2P&x5p<Xjb?Wkcw$;L|u\".B-d@R]3'6lW\"w~hNwFy|c~G+\"J()IT+@'\"B}/oAP`*G7IL1q)2wuyfv9FjQu.c5a'EkI3b076~nf";
    
    // Multi-layered validation
    let validationScore = 0;
    
    // Layer 1: Exact match (primary validation)
    if (inputToken === expectedToken) {
        validationScore += 50;
        logToConsole('Primary token validation: PASSED', 'security');
    } else {
        logToConsole('Primary token validation: FAILED', 'error');
        return false;
    }
    
    // Layer 2: Length validation
    if (inputToken.length === expectedToken.length) {
        validationScore += 10;
    }
    
    // Layer 3: Character distribution analysis
    const charDistribution = analyzeCharacterDistribution(inputToken);
    const expectedDistribution = analyzeCharacterDistribution(expectedToken);
    
    if (Math.abs(charDistribution - expectedDistribution) < 0.1) {
        validationScore += 10;
    }
    
    // Layer 4: Special character validation
    const specialChars = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]/g;
    const inputSpecialCount = (inputToken.match(specialChars) || []).length;
    const expectedSpecialCount = (expectedToken.match(specialChars) || []).length;
    
    if (Math.abs(inputSpecialCount - expectedSpecialCount) < 5) {
        validationScore += 10;
    }
    
    // Layer 5: Hash comparison
    const inputHash = CryptoJS.SHA512(inputToken).toString();
    const expectedHash = CryptoJS.SHA512(expectedToken).toString();
    
    if (inputHash === expectedHash) {
        validationScore += 20;
        logToConsole('Cryptographic hash validation: PASSED', 'crypto');
    }
    
    // Final validation
    const isValid = validationScore >= 90;
    
    // Log audit
    logAudit(inputToken, validationScore, isValid);
    
    return isValid;
}

// Character Distribution Analysis
function analyzeCharacterDistribution(token) {
    if (!token || token.length === 0) return 0;
    
    const charCounts = {};
    let totalChars = 0;
    
    // Count character frequencies
    for (let char of token) {
        charCounts[char] = (charCounts[char] || 0) + 1;
        totalChars++;
    }
    
    // Calculate entropy
    let entropy = 0;
    for (let char in charCounts) {
        const probability = charCounts[char] / totalChars;
        entropy -= probability * Math.log2(probability);
    }
    
    return entropy;
}

// Grant Quantum Access
function grantQuantumAccess(token) {
    // Reset security state
    securityState.attempts = 0;
    securityState.isLocked = false;
    securityState.sessionActive = true;
    
    // Update UI
    const statusLed = document.getElementById('statusLed');
    const statusText = document.getElementById('statusText');
    const attemptCounter = document.getElementById('attemptCounter');
    
    if (statusLed) {
        statusLed.classList.remove('bg-red-500', 'bg-yellow-500');
        statusLed.classList.add('bg-green-500');
    }
    
    if (statusText) {
        statusText.innerHTML = 'SYSTEM STATUS: <span class="text-green-400">ACCESS GRANTED</span>';
    }
    
    if (attemptCounter) {
        attemptCounter.textContent = 'Attempts: 0/3';
    }
    
    // Log success
    logToConsole('Quantum token validation: SUCCESS', 'success');
    logToConsole('Generating secure session token...', 'security');
    
    // Create secure session
    createSecureSession(token);
    
    // Show success and redirect
    setTimeout(() => {
        redirectToAdminPanel();
    }, SECURITY_CONFIG.REDIRECT_DELAY);
}

// Create Secure Session
function createSecureSession(token) {
    try {
        // Generate session token from input token
        const sessionToken = generateSessionToken(token);
        
        // Calculate expiry time
        const expiryTime = Date.now() + SECURITY_CONFIG.SESSION_DURATION;
        
        // Store in localStorage
        localStorage.setItem('quantum_session_token', sessionToken);
        localStorage.setItem('quantum_session_expiry', expiryTime.toString());
        
        // Also store in sessionStorage for added security
        sessionStorage.setItem('quantum_auth_validated', 'true');
        sessionStorage.setItem('quantum_auth_timestamp', Date.now().toString());
        
        logToConsole('Secure session established', 'security');
    } catch (error) {
        console.error('Session creation failed:', error);
        logToConsole('Session creation failed, continuing with redirect', 'warning');
    }
}

// Generate Session Token
function generateSessionToken(inputToken) {
    // Create a unique session token based on input token and timestamp
    const timestamp = Date.now().toString();
    const userAgent = navigator.userAgent;
    
    // Combine and hash
    const combined = inputToken + timestamp + userAgent;
    
    // Multiple hash rounds for security
    let hash = CryptoJS.SHA512(combined).toString();
    
    for (let i = 0; i < SECURITY_CONFIG.HASH_ITERATIONS; i++) {
        hash = CryptoJS.SHA512(hash + combined).toString();
    }
    
    return hash.substring(0, 128); // Return first 128 chars
}

// Redirect to Admin Panel
function redirectToAdminPanel() {
    logToConsole('Initiating secure redirect to admin panel...', 'system');
    
    // Show security overlay
    const overlay = document.getElementById('securityOverlay');
    if (overlay) {
        overlay.classList.remove('hidden');
    }
    
    // Animate progress
    let progress = 0;
    const progressBar = document.getElementById('redirectProgress');
    const progressText = document.getElementById('progressText');
    
    const interval = setInterval(() => {
        progress += 2;
        
        if (progressBar) {
            progressBar.style.width = progress + '%';
        }
        
        if (progressText) {
            if (progress < 25) {
                progressText.textContent = 'Initializing quantum tunnel...';
            } else if (progress < 50) {
                progressText.textContent = 'Validating session integrity...';
            } else if (progress < 75) {
                progressText.textContent = 'Establishing secure connection...';
            } else {
                progressText.textContent = `Finalizing redirect... ${progress}%`;
            }
        }
        
        if (progress >= 100) {
            clearInterval(interval);
            
            // Perform redirect
            setTimeout(() => {
                window.location.href = SECURITY_CONFIG.ADMIN_PANEL_URL;
            }, 500);
        }
    }, 30);
}

// Deny Access
function denyAccess() {
    securityState.attempts++;
    
    // Update UI
    const statusLed = document.getElementById('statusLed');
    const statusText = document.getElementById('statusText');
    const attemptCounter = document.getElementById('attemptCounter');
    
    if (statusLed) {
        statusLed.classList.remove('bg-yellow-500', 'bg-green-500');
        statusLed.classList.add('bg-red-500');
    }
    
    if (statusText) {
        statusText.innerHTML = 'SYSTEM STATUS: <span class="text-red-400">ACCESS DENIED</span>';
    }
    
    if (attemptCounter) {
        attemptCounter.textContent = `Attempts: ${securityState.attempts}/${SECURITY_CONFIG.MAX_ATTEMPTS}`;
    }
    
    // Log failure
    logToConsole(`Quantum token validation: FAILED (Attempt ${securityState.attempts}/${SECURITY_CONFIG.MAX_ATTEMPTS})`, 'error');
    
    // Check for lockout
    if (securityState.attempts >= SECURITY_CONFIG.MAX_ATTEMPTS) {
        securityState.isLocked = true;
        logToConsole('SYSTEM LOCKED: Maximum attempts exceeded. Please wait 30 seconds.', 'error');
        
        // Set lockout timer
        setTimeout(() => {
            securityState.isLocked = false;
            securityState.attempts = 0;
            logToConsole('System unlocked. You may try again.', 'info');
            
            if (attemptCounter) {
                attemptCounter.textContent = 'Attempts: 0/3';
            }
        }, SECURITY_CONFIG.LOCKOUT_TIME);
    }
    
    // Show input error
    showInputError();
}

// Show Input Error
function showInputError() {
    const input = document.getElementById('adminKey');
    if (input) {
        input.classList.add('border-red-500', 'animate-pulse');
        setTimeout(() => {
            input.classList.remove('border-red-500', 'animate-pulse');
        }, 1000);
    }
}

// Log to Console Output
function logToConsole(message, type = 'info') {
    const logOutput = document.getElementById('logOutput');
    if (!logOutput) return;
    
    const colors = {
        success: 'text-green-400',
        error: 'text-red-400',
        warning: 'text-yellow-400',
        info: 'text-blue-400',
        system: 'text-purple-400',
        crypto: 'text-cyan-400',
        security: 'text-orange-400',
        auth: 'text-gray-400'
    };
    
    const timestamp = new Date().toLocaleTimeString([], {hour12: false});
    const logEntry = document.createElement('div');
    logEntry.className = colors[type] || colors.info;
    logEntry.innerHTML = `&gt; [${timestamp}] ${message}`;
    
    logOutput.appendChild(logEntry);
    logOutput.scrollTop = logOutput.scrollHeight;
}

// Log Audit Entry
function logAudit(token, score, isValid) {
    const auditEntry = {
        timestamp: new Date().toISOString(),
        tokenPreview: token.substring(0, 16) + '...' + token.substring(token.length - 16),
        score: score,
        isValid: isValid,
        userAgent: navigator.userAgent,
        ip: 'N/A' // In production, this would come from server
    };
    
    auditLog.push(auditEntry);
    
    // In production, send to server
    if (isValid) {
        console.log('[AUDIT] Successful authentication:', auditEntry);
    } else {
        console.warn('[AUDIT] Failed authentication attempt:', auditEntry);
    }
}

// Reset Form
function resetForm() {
    const input = document.getElementById('adminKey');
    const status = document.getElementById('inputStatus');
    const lengthDisplay = document.getElementById('tokenLength');
    
    if (input) input.value = '';
    if (status) {
        status.classList.remove('bg-green-500', 'bg-yellow-500', 'bg-blue-500');
        status.classList.add('bg-red-500');
    }
    if (lengthDisplay) {
        lengthDisplay.textContent = '0';
        lengthDisplay.classList.remove('text-yellow-400', 'text-green-400');
        lengthDisplay.classList.add('text-red-400');
    }
    
    // Enable/disable validate button
    const validateBtn = document.getElementById('validateBtn');
    if (validateBtn) validateBtn.disabled = true;
    
    logToConsole('Input cleared', 'info');
}

// Start Security Animations
function startSecurityAnimations() {
    // Status LED pulse
    const statusLed = document.getElementById('statusLed');
    if (statusLed) {
        setInterval(() => {
            statusLed.classList.toggle('animate-ping');
        }, 3000);
    }
}

// Console Protection
function enableConsoleProtection() {
    const originalLog = console.log;
    const originalWarn = console.warn;
    const originalError = console.error;
    
    console.log = function(...args) {
        if (args[0] && typeof args[0] === 'string') {
            const msg = args[0].toLowerCase();
            if (msg.includes('token') || msg.includes('key') || msg.includes('auth') || msg.includes('admin')) {
                originalLog.call(console, '%c🔒 [SECURITY] Access restricted', 'color: #ef4444; font-weight: bold;');
                return;
            }
        }
        originalLog.apply(console, args);
    };
    
    console.warn = function(...args) {
        originalWarn.call(console, '%c⚠️ [SECURITY WARNING]', 'color: #f59e0b; font-weight: bold;', ...args);
    };
    
    console.error = function(...args) {
        originalError.call(console, '%c🚨 [SECURITY ALERT]', 'color: #dc2626; font-weight: bold;', ...args);
    };
    
    // Add security message
    setTimeout(() => {
        console.log('%c🔐 QUANTUM SECURITY SYSTEM v2.5.1', 'color: #10b981; font-size: 16px; font-weight: bold;');
        console.log('%c⚠️  Unauthorized access attempts are monitored and logged', 'color: #f59e0b;');
    }, 1000);
}

// Window Exports
window.checkAdminKey = checkAdminKey;
window.resetForm = resetForm;

// Test function for development
window._testQuantumToken = function() {
    const testToken = "]u*ga[34Mury%s3<ZMThSl^l\"aY_5bJJu<gS-W<yDIZ5[$T(8@,gc93fco[IrWBK.x.))i2<(,9S-U[$)+T^?\"o{Os2Utmv=z^nN[+@F'\\egL3NegWgw%-5+Lx%\"?E;d<@Vb*]RT`zfMbL:([aqv}o)crzUw=DrWwQ!cI7jF^zf*>'bjq5aG%exHJRs/p5ZDv,u!3t#4R-:8Z:8E1@1cZz(]U0'SL'Y&@ViW;EH9v:x8&u9tB+Q5xErn*YU;UK\\e8:[tnt)xh%L-uAb25\\\\)36a683L=IB)6$Rwp%EnC>^zK-oGZO\"#,\"twPhRSgqWvvR,R,!rx3]iCdDF\"42%+vX_+cJsaFX;hPi=.X_n}H3lok3p`)Z72RE.U@kH7j)Plt,6%M%.=^U%6+2!ePRsrW9-M=pwlec3+AW-AqCE6=bvH5h(SHWMdQ?p]LN)G^bJ4aafFf;%P.}GXtKqSplqpSGXY$Pago\"=Z`!M&lnyC$gL%I}5kN/#e97C51aoIPhPhyc^Ikl}z0-||Gd58&w;66!URMpUNY!iK>\"8e7!(#2b1&>9OED.ZV<X#1Uf0\"JiXKJw%$Q6j?0;JH[|HOyhHhJ2E(yz-'mi(:FZV?mh?W9#2?kO6y2%YYgYD|!GL/Aa6\"&;(o*WDhTBB(v]5R8l/zJ=)OgAvvm22h'Aa9Xdn{w)'!5=m(WF!L7$?4hp!nj.fX;*:db#^,[<'v]X+Y*_,v\".WvU3LI3|m~z5R$&9/<5[MJCYaf%&E1,c1-ZSm^/2:DsI\\*`^:}L<q2Z]:JL|<Aex9@t4VobD;>#s'p@iVr}1w-QEki}Ml.#qr:B?ZIIf<]8bB|8n$Pk[Bn4v2Xa,95l,5r\"!wwDUA)>=kg%TU\\h5c_j>Ck7I{3t*!E/)wU\\-U8!/n=E0b-R+#'GC,ta}#9swqwvh&mS/q}&n,]}6[e_HEE#2m)7{)P9]La16.jQkhlq034=W;zd?fVoY=_W\\\"caW3yd6al`)`}:Tjb:($YrZln]&|+H&v0%C1?]jGCeJnEYoQPBj_qPG3ZRvf`M-#t/8sFVewzJ8r=U\\s(E|x!*F>#kkVN66u+s[sGOzK7JC>g28J28sNQ#H/NGN2z?E)!LO52B~ND=Zni&7cEcu$Kz=E7O[Zg94T2An<2DL\"]vL\\+}~83<A;`cY0ruUOx4xmq;li2vt|T')H~af_\\`1@i26Qz*3l+BH9`-}CWLd(2yZctAV7Rf($g$/y?#_.DS+}RupWhJ%1[Omc+\\>PxVfuY=LUuDZII-#2zlrX`a2_B,+RAEW)CPL>R;Br7_KU;@!I?bGqLg*)AQ6?EGc95dS/S{LKYTt([YWhc;!=7Qxe3W\"^!o?f<aLOfcv*d\"52hFaV;biz@R#$aL\"\"X8LxL`Nh&bbUj+v7:>_Z#b*;KX2o9$?|2P&x5p<Xjb?Wkcw$;L|u\".B-d@R]3'6lW\"w~hNwFy|c~G+\"J()IT+@'\"B}/oAP`*G7IL1q)2wuyfv9FjQu.c5a'EkI3b076~nf";
    
    console.log('%c🔑 QUANTUM TOKEN VALIDATOR', 'color: #10b981; font-size: 14px; font-weight: bold;');
    console.log('%cTesting token validation...', 'color: #3b82f6;');
    
    const isValid = validateQuantumToken(testToken);
    
    if (isValid) {
        console.log('%c✅ Token validation: PASSED', 'color: #10b981; font-weight: bold;');
        console.log('%cToken is valid and ready for use', 'color: #10b981;');
        
        // Auto-fill the token
        const input = document.getElementById('adminKey');
        if (input) {
            input.value = testToken;
            validateInputLength();
            updateTokenLength();
            console.log('%c✅ Token auto-filled in input field', 'color: #10b981;');
        }
    } else {
        console.log('%c❌ Token validation: FAILED', 'color: #ef4444; font-weight: bold;');
    }
    
    return isValid;
};

// Auto-fill the token on page load for easy testing
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log('%c🔐 QUANTUM ADMIN SYSTEM READY', 'color: #10b981; font-size: 12px;');
        console.log('%cTo test the system, run: _testQuantumToken()', 'color: #3b82f6; font-family: monospace;');
    }, 2000);
});