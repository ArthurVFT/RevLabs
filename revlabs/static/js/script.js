// Variáveis globais para gerenciar o estado
let activeSlotId = null; 
let installedMods = {}; // Ex: { 'mod-1': { hp: 30, weight: 5 }, 'mod-2': ... }

function toggleModMenu(event) {
    const modSlot = event.currentTarget;
    activeSlotId = modSlot.id; // Guarda qual slot abriu o menu
    
    const menu = document.getElementById('mod-dropdown');
    const rect = modSlot.getBoundingClientRect();
    
    menu.style.top = `${rect.bottom + window.scrollY + 10}px`;
    menu.style.left = `${rect.left + window.scrollX + 20}px`;
    menu.classList.remove('hidden');
}

// Fecha o menu ao clicar fora
document.addEventListener('click', function(event) {
    const menu = document.getElementById('mod-dropdown');
    // Verifica se o clique não foi no menu e não foi em nenhum slot
    if (!menu.contains(event.target) && !event.target.closest('.mod-slot')) {
        menu.classList.add('hidden');
    }
});

function timeToSeconds(timeStr) {
    const parts = timeStr.split(':');
    const minutes = parseInt(parts[0], 10);
    const seconds = parseFloat(parts[1]);
    return (minutes * 60) + seconds;
}

function secondsToTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    
    // Format the seconds to always have 2 digits before the dot and 3 after (e.g., "05.120")
    let secondsStr = seconds.toFixed(3);
    if (seconds < 10) {
        secondsStr = '0' + secondsStr;
    }
    
    return `${minutes}:${secondsStr}`;
}

function installPart(partName, addedHp, addedWeight, imagePath) {
    if (!activeSlotId) return;

    // Registra a peça no estado global
    installedMods[activeSlotId] = {
        hp: addedHp,
        weight: addedWeight
    };

    // Atualiza a interface do Slot clicado
    const modSlot = document.getElementById(activeSlotId);
    modSlot.classList.remove('empty');
    modSlot.classList.add('filled');
    
    modSlot.innerHTML = `<img src="${imagePath}" class="installed-mod" alt="${partName}">
                         <span class="slot-label">${activeSlotId.replace('-', ' ').toUpperCase()}</span>`;

    recalculatePerformance();

    document.getElementById('mod-dropdown').classList.add('hidden');
}

function recalculatePerformance() {
    const timeDisplay = document.getElementById('lap-time-display');
    
    const trackLengthKm = parseFloat(timeDisplay.getAttribute('data-track-length'));
    const baseSpeedKmh = parseFloat(timeDisplay.getAttribute('data-base-speed'));
    const basePower = parseFloat(timeDisplay.getAttribute('data-base-power'));
    const baseWeight = parseFloat(timeDisplay.getAttribute('data-base-weight'));

    let totalPower = basePower;
    let totalWeight = baseWeight;

    for (const slotId in installedMods) {
        totalPower += installedMods[slotId].hp;
        totalWeight += installedMods[slotId].weight;
    }

    // FÍSICA REALISTA: O limite do pneu de rua e da tração mecânica.
    let powerRatio = totalPower / basePower;
    let powerExponent = 0.30; // Ganho bom para carros fracos (ex: Fusca e Parati)

    if (basePower >= 500) {
        // Supercarros já operam no limite da aderência. 
        // Mais potência bruta tem um impacto minúsculo no tempo de volta sem instalar aerofólios e pneus slick.
        powerExponent = 0.05; 
    } else if (totalPower > 250) {
        // Carros comuns que receberam muitas peças e passaram de 250cv começam 
        // a patinar pneu em excesso na saída de curva. O ganho de tempo cai drasticamente.
        powerExponent = 0.15;
    }

    const powerMultiplier = Math.pow(powerRatio, powerExponent);
    
    // O peso, ao contrário da potência, melhora curva, aceleração e frenagem linearmente.
    const weightMultiplier = Math.pow((baseWeight / totalWeight), 0.50);
    
    const newSpeedKmh = baseSpeedKmh * powerMultiplier * weightMultiplier;
    
    const newSeconds = (trackLengthKm / newSpeedKmh) * 3600;
    const newTime = secondsToTime(newSeconds);

    timeDisplay.innerText = newTime;
    timeDisplay.classList.add('time-improved');
}

// Filter parts based on the selected sub-category
function filterParts(subCategory, element) {

    const listItems = element.parentElement.querySelectorAll('li');
    listItems.forEach(li => li.classList.remove('active-category'));
    element.classList.add('active-category');

    const parts = document.querySelectorAll('.part-item');
    parts.forEach(part => {
        if (part.getAttribute('data-subcategory') === subCategory) {
            part.style.display = 'flex'; 
        } else {
            part.style.display = 'none';
        }
    });
}