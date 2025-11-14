document.getElementById("btn-open").addEventListener("click", () => {
    const modal = document.querySelector('modal-dialog');
    modal.open();
});


function appendLog(msg) {
    const log = document.getElementById('log-area');
    log.innerText += msg + '\n';
    log.scrollTop = log.scrollHeight;
}

function clearLogs() {
    const log = document.getElementById('log-area');
    log.innerText = '';
}

function closeApp() {
    if (window.pywebview) {
        window.pywebview.api.close_app();
    }
}

function renderTargetList(targets) {
    const list = document.getElementById('target-list');
    list.innerHTML = '';
    targets.forEach((t, idx) => {
        const li = document.createElement('li');
        li.className = 'target-item';
        // Si hay imagen base64, mostrarla
        if (t.img_b64) {
            const img = document.createElement('img');
            img.src = t.img_b64;
            img.className = 'target-img';
            li.appendChild(img);
        }
        // Agregar los radio buttons
        const optionsContainer = createTargetOptions(t, idx);
        li.appendChild(optionsContainer);
        const del = document.createElement('button');
        del.className = 'target-delete';
        del.innerText = 'Eliminar';
        del.onclick = () => deleteTarget(idx);
        li.appendChild(del);
        list.appendChild(li);
    });
}

function createTargetOptions(target, index) {
    const container = document.createElement('div');
    container.className = 'target-options';

    const radiosContainer = document.createElement('div');
    radiosContainer.className = 'target-radios';

    // Input para nombre (opcional)
    const nameInput = document.createElement('input');
    nameInput.className = 'target-name-input';
    nameInput.type = 'text';
    nameInput.name = `character-name-${index}`;
    nameInput.value = target.name || '';
    nameInput.placeholder = 'Nombre (opcional)';
    nameInput.addEventListener('blur', () => {
        onTargetNameChange(index, nameInput.value);
    });
    container.appendChild(nameInput);

    // Radio para "is_alive"
    const aliveLabel = document.createElement('label');
    const aliveRadio = document.createElement('input');
    aliveRadio.type = 'radio';
    aliveRadio.name = `pattern-type-${index}`; // Agrupar por target
    aliveRadio.value = 'is_alive';
    aliveRadio.checked = target.pattern_type === 'is_alive';
    aliveRadio.addEventListener('change', () => {
        onPatternTypeChange(index, 'is_alive');
    });
    aliveLabel.appendChild(aliveRadio);
    aliveLabel.appendChild(document.createTextNode('Si vivo'));

    // Radio para "is_online"
    const onlineLabel = document.createElement('label');
    const onlineRadio = document.createElement('input');
    onlineRadio.type = 'radio';
    onlineRadio.name = `pattern-type-${index}`;
    onlineRadio.value = 'is_online';
    onlineRadio.checked = target.pattern_type === 'is_online';
    onlineRadio.addEventListener('change', () => {
        onPatternTypeChange(index, 'is_online');
    });
    onlineLabel.appendChild(onlineRadio);
    onlineLabel.appendChild(document.createTextNode('Si en línea'));

    // Agregar ambos radios al contenedor
    radiosContainer.appendChild(aliveLabel);
    radiosContainer.appendChild(onlineLabel);
    container.appendChild(radiosContainer);

    return container;
}

async function onPatternTypeChange(index, newType) {
    if (window.pywebview) {
        await window.pywebview.api.update_target_pattern(index, newType);
    }
}

async function onTargetNameChange(index, newName) {
    if (window.pywebview) {
        await window.pywebview.api.update_target_name(index, newName);
    }
}



// --- Llamadas a Python ---
async function getTargets() {
    if (window.pywebview) {
        const targets = await window.pywebview.api.get_targets();
        renderTargetList(targets);
        showTargetTitles(targets.length);
    }
}

function showTargetTitles(count) {
    const title = document.getElementById('target-title');
    if (count)
        title.innerText = `Áreas monitoreadas (${count})`;
    else
        title.innerText = '';
}

async function addTarget() {
    if (window.pywebview) {
        const ok = await window.pywebview.api.add_target();
        if (ok) {
            appendLog('Área agregada.');
            getTargets();
        }
    }
}
async function deleteTarget(idx) {
    if (window.pywebview) {
        await window.pywebview.api.delete_target(idx);
        appendLog('Área eliminada.');
        getTargets();
    }
}
let monitoring = false;
async function toggleMonitoring() {
    if (window.pywebview) {
        monitoring = !monitoring;
        monitoringStatusChanged(monitoring);
        await window.pywebview.api.toggle_monitoring();
    }
}

function monitoringStatusChanged(isMonitoring) {
    monitoring = isMonitoring;
    document.getElementById('monitor-btn').innerText = monitoring ? 'Detener monitoreo' : 'Iniciar monitoreo';
}

// --- Eventos UI ---
document.getElementById('add-btn').onclick = addTarget;
document.getElementById('monitor-btn').onclick = toggleMonitoring;
// --- Recibir logs desde Python ---
if (window.pywebview) {
    window.pywebview.onLog = appendLog;
}
// --- Inicialización ---
getTargets();