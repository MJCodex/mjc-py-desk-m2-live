// --- Utilidades de UI ---
function appendLog(msg) {
    const log = document.getElementById('log-area');
    log.innerText += msg + '\n';
    log.scrollTop = log.scrollHeight;
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
        const span = document.createElement('span');
        span.innerText = `Área: (${t.start_x},${t.start_y})-(${t.end_x},${t.end_y})`;
        li.appendChild(span);
        const del = document.createElement('button');
        del.className = 'target-delete';
        del.innerText = 'Eliminar';
        del.onclick = () => deleteTarget(idx);
        li.appendChild(del);
        list.appendChild(li);
    });
}
// --- Llamadas a Python ---
async function getTargets() {
    if (window.pywebview) {
        const targets = await window.pywebview.api.get_targets();
        renderTargetList(targets);
    }
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
        document.getElementById('monitor-btn').innerText = monitoring ? 'Detener monitoreo' : 'Iniciar monitoreo';
        await window.pywebview.api.toggle_monitoring();
    }
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