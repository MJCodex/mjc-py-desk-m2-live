let availablePatterns = [];
let monitoring = false;

document.getElementById("btn-open").addEventListener("click", () => {
    const modal = document.querySelector('modal-dialog');
    modal.open();
});

async function loadAvailablePatterns() {
    if (window.pywebview) {
        availablePatterns = await window.pywebview.api.get_available_patterns();
    }
}

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

    // Input para nombre (primera línea)
    const nameInputWrapper = document.createElement('div');
    nameInputWrapper.className = 'target-name-wrapper';

    const nameInput = document.createElement('input');
    nameInput.className = 'target-name-input full-width';
    nameInput.type = 'text';
    nameInput.name = `character-name-${index}`;
    nameInput.value = target.name || '';
    nameInput.placeholder = 'Nombre (opcional)';
    nameInput.addEventListener('blur', () => {
        onTargetNameChange(index, nameInput.value);
    });
    nameInputWrapper.appendChild(nameInput);
    container.appendChild(nameInputWrapper);

    // Checkboxes para patrones en una línea con wrap
    const patternsContainer = document.createElement('div');
    patternsContainer.className = 'target-patterns';

    availablePatterns.forEach(patternType => {
        const patternItemWrapper = document.createElement('div');
        patternItemWrapper.className = 'pattern-item-wrapper';

        // Label con checkbox
        const label = document.createElement('label');
        label.className = 'pattern-label';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = `pattern-${index}-${patternType}`;
        checkbox.value = patternType;
        checkbox.checked = target.pattern_types.includes(patternType);
        checkbox.addEventListener('change', () => {
            onPatternToggle(index, patternType, checkbox.checked);
        });

        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(formatPatternName(patternType)));
        patternItemWrapper.appendChild(label);

        // Si el patrón está activo y es de grupo, mostrar input expected_count al lado
        if (checkbox.checked && patternType.includes('group')) {
            const expectedCountInput = document.createElement('input');
            expectedCountInput.type = 'number';
            expectedCountInput.className = 'expected-count-input-inline';
            expectedCountInput.min = '0';
            expectedCountInput.value = target.patterns_config?.[patternType]?.expected_count || '';
            expectedCountInput.placeholder = 'ej: 3';
            expectedCountInput.addEventListener('blur', () => {
                const value = expectedCountInput.value ? parseInt(expectedCountInput.value) : null;
                onExpectedCountChange(index, patternType, value);
            });
            patternItemWrapper.appendChild(expectedCountInput);
        }

        patternsContainer.appendChild(patternItemWrapper);
    });

    container.appendChild(patternsContainer);
    return container;
}

async function onPatternToggle(index, patternType, isChecked) {
    if (window.pywebview) {
        if (isChecked) {
            await window.pywebview.api.add_pattern_to_character(index, patternType, {});
        } else {
            await window.pywebview.api.remove_pattern_from_character(index, patternType);
        }
        getTargets();
    }
}

async function onExpectedCountChange(index, patternType, value) {
    if (window.pywebview) {
        await window.pywebview.api.update_pattern_config(index, patternType, 'expected_count', value);
        appendLog(`Cuenta de "${formatPatternName(patternType)}" actualizada a ${value}`);
    }
}

async function onTargetNameChange(index, newName) {
    if (window.pywebview) {
        await window.pywebview.api.update_target_name(index, newName);
    }
}


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
        const result = await window.pywebview.api.add_target();
        if (result) {
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

function formatPatternName(patternType) {
    const names = {
        'is_alive': 'Vivo',
        'is_online': 'En línea',
        'has_buff': 'Con buff',
        'in_combat': 'En combate',
        'is_alive_in_group': 'Grupo vivo',
        'is_online_in_group': 'Grupo en linea'
    };
    return names[patternType] || patternType;
}

window.addEventListener('pywebviewready', async function () {
    await loadAvailablePatterns();
    getTargets();
})