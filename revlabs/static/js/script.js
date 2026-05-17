let installedMods = {}; 

const incompatibilityMap = {
    "Twin-Scroll Turbo Kit": ["Roots Supercharger"],
    "Roots Supercharger": ["Twin-Scroll Turbo Kit"],
    "Street Coilovers": ["Fully Adjustable Race Coilovers"],
    "Fully Adjustable Race Coilovers": ["Street Coilovers"]
};

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('mod-modal');
    const addModBtn = document.getElementById('add-mod-btn');
    const mainCategories = document.querySelectorAll('#main-category-list li');
    const subCategories = document.querySelectorAll('#category-list li');
    const parts = document.querySelectorAll('.part-item');

    addModBtn.addEventListener('click', () => {
        const rect = addModBtn.getBoundingClientRect();
        
        modal.style.margin = '0';
        modal.style.right = 'auto';
        modal.style.bottom = 'auto';
        
        modal.style.top = `${rect.bottom + 10}px`;
        modal.style.left = `${rect.left + (rect.width / 2)}px`;
        modal.style.transform = 'translateX(-50%)';
        
        modal.showModal();
        
        const defaultTab = document.querySelector('[data-target-main="engine"]');
        if (defaultTab) defaultTab.click();
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.close();
        }
    });

    mainCategories.forEach(mainLi => {
        mainLi.addEventListener('click', () => {
            mainCategories.forEach(li => li.classList.remove('active-main'));
            mainLi.classList.add('active-main');

            const targetMain = mainLi.getAttribute('data-target-main');
            subCategories.forEach(subLi => {
                if (subLi.getAttribute('data-main-cat') === targetMain) {
                    subLi.style.display = 'block';
                } else {
                    subLi.style.display = 'none';
                }
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
                if (part.classList.contains(targetCat)) {
                    part.style.display = 'flex';
                } else {
                    part.style.display = 'none';
                }
            });
        });
    });

    parts.forEach(part => {
        part.addEventListener('click', () => {
            const partName = part.getAttribute('data-name');
            const addedHp = parseFloat(part.getAttribute('data-hp'));
            const addedWeight = parseFloat(part.getAttribute('data-weight'));
            const imagePath = part.getAttribute('data-img');

            const activeSubLi = document.querySelector('#category-list li.active-category');
            const mainCat = activeSubLi ? activeSubLi.getAttribute('data-main-cat') : '';

            // 1. Validação de item idêntico já instalado
            if (installedMods[partName]) {
                alert('already installed');
                return;
            }

            // 2. Regra de Negócio de Pneus: Troca de compostos
            if (mainCat === 'tyres') {
                let existingTyreName = null;
                for (const name in installedMods) {
                    if (installedMods[name].mainCat === 'tyres') {
                        existingTyreName = name;
                        break;
                    }
                }

                if (existingTyreName) {
                    const swap = confirm(`${partName} is already installed, do you want to switch compounds?`);
                    if (swap) {
                        delete installedMods[existingTyreName];
                    } else {
                        return;
                    }
                }
            }

            // 3. Validação de incompatibilidades cruzadas externas
            const conflicts = incompatibilityMap[partName] || [];
            for (const conflictMod of conflicts) {
                if (installedMods[conflictMod]) {
                    alert(`${partName} isn't compatible with ${conflictMod}`);
                    return;
                }
            }

            // Adiciona a peça nova ao estado
            installedMods[partName] = {
                hp: addedHp,
                weight: addedWeight,
                img: imagePath,
                mainCat: mainCat
            };

            renderInstalledMods();
            modal.close();
        });
    });
});

// Renderização dinâmica da lista empilhada
function renderInstalledMods() {
    const listContainer = document.getElementById('installed-mods-list');
    listContainer.innerHTML = '';

    for (const partName in installedMods) {
        const mod = installedMods[partName];
        const row = document.createElement('div');
        row.className = 'installed-mod-row';

        const hpDisplay = mod.hp >= 0 ? `+${mod.hp} HP` : `${mod.hp} HP`;
        const weightDisplay = mod.weight >= 0 ? `+${mod.weight} kg` : `${mod.weight} kg`;

        row.innerHTML = `
            <div class="mod-left-info">
                <img src="${mod.img}" alt="${partName}" class="mod-row-img">
                <div class="mod-text-details">
                    <h4>${partName}</h4>
                    <p class="mod-short-desc">Componente de alto rendimento configurado para Track Days.</p>
                </div>
            </div>
            <div class="mod-right-stats">
                <span class="stat-badge hp">${hpDisplay}</span>
                <span class="stat-badge weight">${weightDisplay}</span>
                <button class="btn-remove-mod" onclick="removeModification('${partName}')">✕</button>
            </div>
        `;
        listContainer.appendChild(row);
    }

    recalculatePerformance();
}

// Expõe a remoção globalmente para funcionamento do atributo onclick
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

function recalculatePerformance() {
    const timeDisplay = document.getElementById('lap-time-display');
    if (!timeDisplay) return;

    const trackLengthKm = parseFloat(timeDisplay.getAttribute('data-track-length'));
    const baseSpeedKmh = parseFloat(timeDisplay.getAttribute('data-base-speed'));
    const basePower = parseFloat(timeDisplay.getAttribute('data-base-power'));
    const baseWeight = parseFloat(timeDisplay.getAttribute('data-base-weight'));

    let totalPower = basePower;
    let totalWeight = baseWeight;

    for (const name in installedMods) {
        totalPower += installedMods[name].hp;
        totalWeight += installedMods[name].weight;
    }

    let powerRatio = totalPower / basePower;
    let powerExponent = 0.30; 

    if (basePower >= 500) {
        powerExponent = 0.05; 
    } else if (totalPower > 250) {
        powerExponent = 0.15;
    }

    const powerMultiplier = Math.pow(powerRatio, powerExponent);
    const weightMultiplier = Math.pow((baseWeight / totalWeight), 0.50);
    const newSpeedKmh = baseSpeedKmh * powerMultiplier * weightMultiplier;
    
    const newSeconds = (trackLengthKm / newSpeedKmh) * 3600;
    timeDisplay.innerText = secondsToTime(newSeconds);
}