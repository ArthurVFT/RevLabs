function toggleModMenu(event) {
    const modSlot = event.currentTarget;
    const menu = document.getElementById('mod-dropdown');
    
    const rect = modSlot.getBoundingClientRect();
    menu.style.top = `${rect.bottom + window.scrollY + 10}px`;
    menu.style.left = `${rect.left + window.scrollX + 20}px`;
    
    menu.classList.toggle('hidden');
}

document.addEventListener('click', function(event) {
    const menu = document.getElementById('mod-dropdown');
    const modSlot = document.getElementById('mod-1');
    
    if (!menu.contains(event.target) && !modSlot.contains(event.target)) {
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

function installPart(partName, speedBoostPercentage, imagePath) {
    const modSlot = document.getElementById('mod-1'); 
    const timeDisplay = document.getElementById('lap-time-display');
    const menu = document.getElementById('mod-dropdown');

    const trackLengthKm = parseFloat(timeDisplay.getAttribute('data-track-length'));
    let currentSpeedKmh = parseFloat(timeDisplay.getAttribute('data-current-speed'));

    currentSpeedKmh = currentSpeedKmh * (1 + (speedBoostPercentage / 100));

    const newSeconds = (trackLengthKm / currentSpeedKmh) * 3600;
    const newTime = secondsToTime(newSeconds);

    timeDisplay.setAttribute('data-current-speed', currentSpeedKmh);

    modSlot.classList.remove('empty');
    modSlot.classList.add('filled');
    
    const img = document.createElement('img');
    img.src = imagePath; 
    img.className = 'installed-mod';
    
    modSlot.innerHTML = ''; 
    modSlot.appendChild(img);   
    
    const label = document.createElement('span');
    label.className = 'slot-label';
    label.innerText = 'MOD 1';
    modSlot.appendChild(label);

    timeDisplay.innerText = newTime;
    timeDisplay.classList.add('time-improved');

    menu.classList.add('hidden');
}