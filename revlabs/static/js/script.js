function toggleModMenu(event) {
    const modSlot = event.currentTarget;
    const menu = document.getElementById('mod-dropdown');
    
    const rect = modSlot.getBoundingClientRect();
    menu.style.top = `${rect.bottom + window.scrollY + 10}px`;
    menu.style.left = `${rect.left + window.scrollX + 20}px`;
    
    menu.classList.toggle('hidden');
}

// Notice the new imagePath parameter passed from the Django template
function installPart(partName, newTime, imagePath) {
    const modSlot = document.getElementById('mod-1'); 
    const timeDisplay = document.getElementById('lap-time-display');
    const menu = document.getElementById('mod-dropdown');

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

document.addEventListener('click', function(event) {
    const menu = document.getElementById('mod-dropdown');
    const modSlot = document.getElementById('mod-1');
    
    if (!menu.contains(event.target) && !modSlot.contains(event.target)) {
        menu.classList.add('hidden');
    }
});