let installedMods = {}; 

const incompatibilityMap = {
    "Low-RPM Turbocharger": ["High-RPM Turbocharger", "Roots Supercharger", "Supercharger (High-Torque)"],
    "High-RPM Turbocharger": ["Low-RPM Turbocharger", "Roots Supercharger", "Supercharger (High-Torque)"],
    "Roots Supercharger": ["Low-RPM Turbocharger", "High-RPM Turbocharger", "Supercharger (High-Torque)"],
    "Supercharger (High-Torque)": ["Low-RPM Turbocharger", "High-RPM Turbocharger", "Roots Supercharger"],
    "Street Coilovers": ["Fully Adjustable Race Coilovers"],
    "Fully Adjustable Race Coilovers": ["Street Coilovers"],
    "Stage 1: Strip Interior": ["Stage 2: Carbon Fiber Panels", "Stage 3: Lexan Windows & Shell"],
    "Stage 2: Carbon Fiber Panels": ["Stage 1: Strip Interior", "Stage 3: Lexan Windows & Shell"],
    "Stage 3: Lexan Windows & Shell": ["Stage 1: Strip Interior", "Stage 2: Carbon Fiber Panels"],
};

// ==========================================================================
// 1. VEHICLE DYNAMICS BASE STATS
// ==========================================================================
// cda: Drag coefficient * Frontal Area
// cla: Lift coefficient * Frontal Area (Downforce)
// mu: Mechanical grip coefficient
// brake_eff: Braking system efficiency multiplier
// drivetrain_loss: Parasitic loss (e.g., 0.15 = 15% loss)
const BASE_CAR_STATS = {
    'vw-fusca':     { cda: 0.85, cla: 0.00, mu: 0.85, brake_eff: 0.80, drivetrain_loss: 0.15 },
    'vw-brasilia':  { cda: 0.82, cla: 0.00, mu: 0.85, brake_eff: 0.80, drivetrain_loss: 0.15 },
    'vw-parati':    { cda: 0.75, cla: 0.05, mu: 0.95, brake_eff: 0.85, drivetrain_loss: 0.15 },
    'ferrari-458':  { cda: 0.65, cla: 0.60, mu: 1.25, brake_eff: 1.15, drivetrain_loss: 0.12 },
    'porsche-911':  { cda: 0.78, cla: 1.30, mu: 1.45, brake_eff: 1.25, drivetrain_loss: 0.10 },
    'mercedes-amg': { cda: 0.75, cla: 1.10, mu: 1.38, brake_eff: 1.20, drivetrain_loss: 0.12 }
};

// ==========================================================================
// 2. MOD PHYSICS MAPPING (Directly affects dynamic attributes)
// ==========================================================================
const MOD_PHYSICS_MAP = {
    "Racing Slicks": { mu: +0.35 },
    "Semi-Slick Track Tyres": { mu: +0.20 },
    "High-Performance Tyres": { mu: +0.10 },
    "Performance Tyres": { mu: +0.05 },
    "Adjustable GT Wing": { cla: +0.45, cda: +0.06 },
    "Carbon Fiber Splitter": { cla: +0.20, cda: +0.03 },
    "Carbon Fiber Splitter & Canards": { cla: +0.25, cda: +0.04 },
    "Carbon Fiber Rear Diffuser": { cla: +0.15, cda: -0.02 }, // Efficient downforce
    "Rear Diffuser": { cla: +0.10, cda: -0.01 },
    "6-Point Roll Cage": { mu: +0.04 }, // Chassis rigidity translates to cornering stability
    "6-Point FIA Roll Cage": { mu: +0.04 },
    "Fully Adjustable Race Coilovers": { mu: +0.06 },
    "Street Coilovers": { mu: +0.02 },
    "Carbon Ceramic Discs": { brake_eff: +0.20 },
    "Performance Brake Kit": { brake_eff: +0.10 },
    "6-Piston Big Brake Kit": { brake_eff: +0.12 },
    "Racing Calipers": { brake_eff: +0.08 },
    "Sequential Racing Gearbox": { drivetrain_loss: -0.04 },
    "2-Way Racing LSD": { mu: +0.03 }, // Better power deployment out of corners
    "Stage 3: Lexan Windows & Shell": { mu: -0.02 } // Extreme lightweighting slightly hurts mechanical grip if no aero
};

// ==========================================================================
// 3. TRACK METADATA (Sequential Segment Approximation)
// radius: 0 means straight. Otherwise it's corner radius in meters.
// ==========================================================================
const TRACKS = {
    'monza': [
        { length: 900, radius: 0 }, { length: 150, radius: 40 },   // Straight + T1/T2
        { length: 400, radius: 0 }, { length: 300, radius: 140 },  // Straight + Curva Grande
        { length: 900, radius: 0 }, { length: 150, radius: 45 },   // Straight + Roggia
        { length: 300, radius: 0 }, { length: 300, radius: 80 },   // Straight + Lesmos
        { length: 900, radius: 0 }, { length: 300, radius: 90 },   // Straight + Ascari
        { length: 900, radius: 0 }, { length: 400, radius: 110 }   // Straight + Parabolica
    ],
    'interlagos': [
        { length: 800, radius: 0 }, { length: 200, radius: 50 },   // Main Straight + Senna S
        { length: 600, radius: 0 }, { length: 300, radius: 100 },  // Reta Oposta + Descida do Lago
        { length: 200, radius: 0 }, { length: 800, radius: 60 },   // Infield (Laranjinha, Pinheirinho)
        { length: 200, radius: 0 }, { length: 200, radius: 70 },   // Mergulho + Juncao
        { length: 1000, radius: 0 }                                // Subida dos Boxes
    ],
    'silverstone': [
        { length: 500, radius: 0 }, { length: 200, radius: 120 }, 
        { length: 600, radius: 0 }, { length: 300, radius: 60 },
        { length: 800, radius: 0 }, { length: 600, radius: 180 },  // Maggots/Becketts
        { length: 800, radius: 0 }, { length: 300, radius: 100 },  // Hangar + Stowe
        { length: 500, radius: 0 }, { length: 300, radius: 70 },
        { length: 400, radius: 0 }, { length: 400, radius: 60 }
    ],
    'spa': [
        { length: 300, radius: 0 }, { length: 100, radius: 40 },   // La Source
        { length: 200, radius: 0 }, { length: 500, radius: 220 },  // Eau Rouge / Raidillon
        { length: 1500, radius: 0 }, { length: 300, radius: 80 },  // Kemmel + Les Combes
        { length: 200, radius: 0 }, { length: 400, radius: 90 },   // Bruxelles
        { length: 200, radius: 0 }, { length: 400, radius: 100 },  // Pouhon
        { length: 800, radius: 0 }, { length: 500, radius: 180 },  // Blanchimont
        { length: 1000, radius: 0 }, { length: 200, radius: 40 }   // Bus Stop
    ],
    'suzuka': [
        { length: 400, radius: 0 }, { length: 800, radius: 80 },   // S-Curves
        { length: 300, radius: 100 }, { length: 300, radius: 70 }, // Dunlop & Degner
        { length: 600, radius: 0 }, { length: 150, radius: 40 },   // Hairpin
        { length: 800, radius: 0 }, { length: 300, radius: 90 },   // Spoon
        { length: 1000, radius: 0 }, { length: 400, radius: 110 }, // 130R
        { length: 400, radius: 0 }, { length: 150, radius: 50 },   // Casio Triangle
        { length: 300, radius: 0 }
    ]
};

// Procedural generator for Nurburgring to achieve ~20.8km of realistic segments
function generateNordschleife() {
    let segs = [];
    for(let i=0; i<13; i++) {
        segs.push({ length: 350, radius: 0 });    // Short straights
        segs.push({ length: 250, radius: 160 });  // Fast sweepers
        segs.push({ length: 200, radius: 0 });
        segs.push({ length: 200, radius: 80 });   // Medium corners
        segs.push({ length: 150, radius: 50 });   // Tight technical sections (Karussell, Wehrseifen)
        segs.push({ length: 250, radius: 0 });
    }
    segs.push({ length: 2200, radius: 0 });       // Döttinger Höhe
    segs.push({ length: 432, radius: 100 });      // Hohenrain chicane / Tiergarten
    return segs;
}
TRACKS['nurburgring'] = generateNordschleife();


// ==========================================================================
// 4. UI AND MODAL EVENT LISTENERS
// ==========================================================================

function showSystemModal(title, message, isConfirm, callback) {
    const modal = document.getElementById('system-modal');
    document.getElementById('system-dialog-title').innerText = title;
    document.getElementById('system-dialog-message').innerText = message;
    const actionsContainer = document.getElementById('system-dialog-actions');
    actionsContainer.innerHTML = ''; 

    if (isConfirm) {
        const btnCancel = document.createElement('button');
        btnCancel.className = 'btn-system cancel';
        btnCancel.innerText = 'CANCEL';
        btnCancel.onclick = () => { modal.close(); if(callback) callback(false); };

        const btnConfirm = document.createElement('button');
        btnConfirm.className = 'btn-system confirm';
        btnConfirm.innerText = 'CONFIRM';
        btnConfirm.onclick = () => { modal.close(); if(callback) callback(true); };

        actionsContainer.appendChild(btnCancel);
        actionsContainer.appendChild(btnConfirm);
    } else {
        const btnOk = document.createElement('button');
        btnOk.className = 'btn-system confirm';
        btnOk.innerText = 'OK';
        btnOk.onclick = () => { modal.close(); };
        actionsContainer.appendChild(btnOk);
    }
    modal.showModal();
}

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('mod-modal');
    const addModBtn = document.getElementById('add-mod-btn');
    const mainCategories = document.querySelectorAll('#main-category-list li');
    const subCategories = document.querySelectorAll('#category-list li');
    const parts = document.querySelectorAll('.part-item');

    if(addModBtn) {
        addModBtn.addEventListener('click', () => {
            modal.style.margin = 'auto';
            modal.style.right = '0';
            modal.style.bottom = '0';
            modal.style.top = '0';
            modal.style.left = '0';
            modal.style.transform = 'none';
            modal.showModal();
            const defaultTab = document.querySelector('[data-target-main="engine"]');
            if (defaultTab) defaultTab.click();
        });
    }

    if(modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.close();
        });
    }

    mainCategories.forEach(mainLi => {
        mainLi.addEventListener('click', () => {
            mainCategories.forEach(li => li.classList.remove('active-main'));
            mainLi.classList.add('active-main');
            const targetMain = mainLi.getAttribute('data-target-main');
            subCategories.forEach(subLi => {
                subLi.style.display = (subLi.getAttribute('data-main-cat') === targetMain) ? 'block' : 'none';
                subLi.classList.remove('active-category');
            });
            parts.forEach(part => part.style.display = 'none');
        });
    });

    subCategories.forEach(subLi => {
        subLi.addEventListener('click', () => {
            subCategories.forEach(li => li.classList.remove('active-category'));
            subLi.classList.add('active-category');
            const targetCat = subLi.getAttribute('data-target');
            parts.forEach(part => {
                part.style.display = part.classList.contains(targetCat) ? 'flex' : 'none';
            });
        });
    });

    function installPart(partName, hp, weight, img, mainCat) {
        const conflicts = incompatibilityMap[partName] || [];
        for (const conflictMod of conflicts) {
            if (installedMods[conflictMod]) {
                showSystemModal("INCOMPATIBILITY DETECTED", `${partName} cannot be installed alongside ${conflictMod}.`, false);
                return;
            }
        }
        installedMods[partName] = { hp, weight, img, mainCat };
        renderInstalledMods();
        modal.close();
    }

    parts.forEach(part => {
        part.addEventListener('click', () => {
            const partName = part.getAttribute('data-name');
            const addedHp = parseFloat(part.getAttribute('data-hp'));
            const addedWeight = parseFloat(part.getAttribute('data-weight'));
            const imagePath = part.getAttribute('data-img');
            const activeSubLi = document.querySelector('#category-list li.active-category');
            const mainCat = activeSubLi ? activeSubLi.getAttribute('data-main-cat') : '';

            if (installedMods[partName]) {
                showSystemModal("ITEM ALREADY FITTED", `The component "${partName}" is already installed.`, false);
                return;
            }

            if (mainCat === 'tyres') {
                let existingTyre = Object.keys(installedMods).find(key => installedMods[key].mainCat === 'tyres');
                if (existingTyre) {
                    showSystemModal("TYRE CHANGE", `Vehicle is currently fitted with ${existingTyre}. Proceed with mounting ${partName}?`, true, (agreed) => {
                        if (agreed) {
                            delete installedMods[existingTyre];
                            installPart(partName, addedHp, addedWeight, imagePath, mainCat);
                        }
                    });
                    return; 
                }
            }
            installPart(partName, addedHp, addedWeight, imagePath, mainCat);
        });
    });
    
    // Initial calculation trigger
    recalculatePerformance();
});

function renderInstalledMods() {
    const listContainer = document.getElementById('installed-mods-list');
    listContainer.innerHTML = '';

    for (const partName in installedMods) {
        const mod = installedMods[partName];
        const row = document.createElement('div');
        row.className = 'installed-mod-row';

        const hpDisplay = mod.hp >= 0 ? `+${mod.hp} HP` : `${mod.hp} HP`;
        const weightDisplay = mod.weight >= 0 ? `+${mod.weight} KG` : `${mod.weight} KG`;

        row.innerHTML = `
            <div class="mod-left-info">
                <img src="${mod.img}" alt="${partName}" class="mod-row-img">
                <div class="mod-text-details">
                    <h4>${partName.toUpperCase()}</h4>
                    <p class="mod-short-desc">TUNING PART</p>
                </div>
            </div>
            <div class="mod-right-stats">
                <span class="stat-badge">${hpDisplay}</span>
                <span class="stat-badge">${weightDisplay}</span>
                <button class="btn-remove-mod" onclick="removeModification('${partName}')">REMOVE</button>
            </div>
        `;
        listContainer.appendChild(row);
    }
    recalculatePerformance();
}

window.removeModification = function(partName) {
    delete installedMods[partName];
    renderInstalledMods();
};

function secondsToTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    let secondsStr = seconds.toFixed(3);
    if (seconds < 10) secondsStr = '0' + secondsStr;
    return `${minutes}:${secondsStr}`;
}

// ==========================================================================
// 5. CORE SIMULATION ENGINE (Empirical Integration Physics)
// ==========================================================================

function recalculatePerformance() {
    const timeDisplay = document.getElementById('lap-time-display');
    if (!timeDisplay) return;

    const urlParams = new URLSearchParams(window.location.search);
    const carSlug = urlParams.get('car');
    const trackSlug = urlParams.get('track');

    if (!BASE_CAR_STATS[carSlug] || !TRACKS[trackSlug]) return;

    const carBase = BASE_CAR_STATS[carSlug];
    const trackSegments = TRACKS[trackSlug];
    
    // Parse base stats injected by Django UI
    const basePowerHP = parseFloat(timeDisplay.getAttribute('data-base-power'));
    const baseWeightKG = parseFloat(timeDisplay.getAttribute('data-base-weight'));

    // Dynamics State setup
    let dynPowerHP = basePowerHP;
    let dynWeightKG = baseWeightKG;
    let dynCdA = carBase.cda;
    let dynClA = carBase.cla;
    let dynMu = carBase.mu;
    let dynBrakeEff = carBase.brake_eff;
    let dynDrivetrainLoss = carBase.drivetrain_loss;

    // Apply installed mod dynamics
    for (const name in installedMods) {
        dynPowerHP += installedMods[name].hp;
        dynWeightKG += installedMods[name].weight;

        const phys = MOD_PHYSICS_MAP[name];
        if (phys) {
            if (phys.mu) dynMu += phys.mu;
            if (phys.cda) dynCdA += phys.cda;
            if (phys.cla) dynClA += phys.cla;
            if (phys.brake_eff) dynBrakeEff += phys.brake_eff;
            if (phys.drivetrain_loss) dynDrivetrainLoss += phys.drivetrain_loss;
        }
    }

    // Constants
    const g = 9.81;
    const rho = 1.225; // Air density
    const mass = Math.max(dynWeightKG, 500); // Prevent zero/negative weight physics explosions
    const powerWatts = (dynPowerHP * (1 - dynDrivetrainLoss)) * 745.7;

    // --- STEP 1: EXPAND MACRO-SEGMENTS TO INTEGRATION STEPS ---
    const dx = 25; // Integrate in 25-meter steps for speed & accuracy
    let steps = [];
    
    trackSegments.forEach(seg => {
        let numSteps = Math.ceil(seg.length / dx);
        for(let i=0; i<numSteps; i++) {
            steps.push(seg.radius);
        }
    });
    
    const n = steps.length;
    let v_limit = new Float64Array(n);
    let v_forward = new Float64Array(n);
    let v_backward = new Float64Array(n);

    // Absolute Top Speed limited by aerodynamic drag (P = F_drag * V)
    const v_abs_max = Math.pow(powerWatts / (0.5 * rho * dynCdA), 1/3);

    // --- STEP 2: CALCULATE CORNERING LIMITS FOR EVERY POINT ---
    for (let i = 0; i < n; i++) {
        let r = steps[i];
        if (r === 0) { // Straight
            v_limit[i] = v_abs_max;
        } else {
            // Cornering Limit Formula: V = sqrt( (Mu * M * G) / (M/R - 0.5 * Rho * ClA * Mu) )
            let aeroDenominator = (mass / r) - (0.5 * rho * dynClA * dynMu);
            if (aeroDenominator <= 0) {
                // Downforce overcomes centrifugal forces completely (Flat-out corner)
                v_limit[i] = v_abs_max;
            } else {
                v_limit[i] = Math.min(Math.sqrt((dynMu * mass * g) / aeroDenominator), v_abs_max);
            }
        }
    }

    // --- STEP 3: FORWARD PASS (Acceleration & Traction Limit) ---
    v_forward[0] = Math.min(15, v_limit[0]); // Rolling start at 15m/s
    for (let i = 0; i < n - 1; i++) {
        let v = v_forward[i];
        
        let f_drag = 0.5 * rho * dynCdA * v * v;
        let f_downforce = 0.5 * rho * dynClA * v * v;
        let f_normal = mass * g + f_downforce;
        
        // Simplified traction limit (assume RWD/AWD can put down power efficiently)
        let f_traction_limit = dynMu * f_normal * 0.7; // 0.7 scalar for longitudinal slip
        
        // P = F * V => F_drive = P / V
        let f_drive = powerWatts / Math.max(v, 1);
        f_drive = Math.min(f_drive, f_traction_limit);
        
        let accel = (f_drive - f_drag) / mass;
        let v_next = Math.sqrt(v*v + 2*accel*dx);
        
        v_forward[i+1] = Math.min(v_next, v_limit[i+1]);
    }

    // --- STEP 4: BACKWARD PASS (Braking Zones) ---
    v_backward[n-1] = v_forward[n-1];
    for (let i = n - 2; i >= 0; i--) {
        let v = v_backward[i+1];
        
        let f_drag = 0.5 * rho * dynCdA * v * v;
        let f_downforce = 0.5 * rho * dynClA * v * v;
        let f_normal = mass * g + f_downforce;
        
        // Deceleration force (Brakes + Downforce grip + Drag)
        let f_brake = (dynMu * dynBrakeEff * f_normal);
        let decel = (f_brake + f_drag) / mass;
        
        // Integrate backward
        let v_prev = Math.sqrt(v*v + 2*decel*dx);
        v_backward[i] = Math.min(v_prev, v_forward[i]);
    }

    // --- STEP 5: TIME ACCUMULATION ---
    let totalTimeSeconds = 0;
    for (let i = 0; i < n; i++) {
        // Avoid division by zero by clamping min speed to 1 m/s
        let v_actual = Math.max(v_backward[i], 1.0);
        totalTimeSeconds += dx / v_actual;
    }

    timeDisplay.innerText = secondsToTime(totalTimeSeconds);
}