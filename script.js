// Ecosistema SaaS Central Dashboard Logic

// State
let state = {
    apiBaseUrl: localStorage.getItem('saas_api_url') || 'https://automatizaciondb.onrender.com/api',
    isRealMode: localStorage.getItem('saas_mode') !== 'mock', // true = API, false = Mock
    negocios: [],
    perfiles: []
};

// Simulated mock data for offline presentation
const MOCK_NEGOCIOS = [
    { id: 1, nombre: 'Agencia Alfa', plan: 'SuperPRO', estatus: 'Activo' },
    { id: 2, nombre: 'Restaurante Alfa', plan: 'PRO', estatus: 'Activo' },
    { id: 3, nombre: 'Pizzería Rustica', plan: 'Básico', estatus: 'Activo' },
    { id: 4, nombre: 'Sushi Express', plan: 'PRO', estatus: 'Activo' },
    { id: 5, nombre: 'Cafetería Central', plan: 'Básico', estatus: 'Suspendido' },
    { id: 6, nombre: 'Burgers & Co', plan: 'SuperPRO', estatus: 'Activo' },
    { id: 7, nombre: 'Tacos el Rey', plan: 'Básico', estatus: 'Activo' }
];

const MOCK_PERFILES = [
    { negocio_id: 1, sucursales_json: JSON.stringify([
        { nombre: 'Sede Principal', horario: '9am - 9pm', menu: [{}, {}, {}, {}] },
        { nombre: 'Sede Sur', horario: '10am - 10pm', menu: [{}, {}, {}] }
    ])},
    { negocio_id: 2, sucursales_json: JSON.stringify([
        { nombre: 'Sucursal Central', horario: '12pm - 11pm', menu: [{}, {}, {}, {}, {}] }
    ])},
    { negocio_id: 3, sucursales_json: JSON.stringify([
        { nombre: 'Delivery La Molina', horario: '6pm - 11pm', menu: [{}, {}, {}] }
    ])},
    { negocio_id: 4, sucursales_json: JSON.stringify([
        { nombre: 'Sede Miraflores', horario: '12pm - 10pm', menu: [{}, {}, {}, {}] },
        { nombre: 'Sede San Isidro', horario: '12pm - 10pm', menu: [{}, {}, {}, {}] }
    ])},
    { negocio_id: 6, sucursales_json: JSON.stringify([
        { nombre: 'Food Truck Barranco', horario: '7pm - 1am', menu: [{}, {}, {}] }
    ])}
];

// DOM Elements
const apiUrlInput = document.getElementById('apiUrlInput');
const btnToggleMode = document.getElementById('btnToggleMode');
const btnReconnect = document.getElementById('btnReconnect');
const apiStatusText = document.getElementById('apiStatusText');
const apiStatusDot = document.getElementById('apiStatusDot');

// Metrics
const statTotalNegocios = document.getElementById('statTotalNegocios');
const statPlanesActivos = document.getElementById('statPlanesActivos');
const statPlanesSuspendidos = document.getElementById('statPlanesSuspendidos');
const statTotalSedes = document.getElementById('statTotalSedes');

// Progress bars
const planBasicoPct = document.getElementById('planBasicoPct');
const planBasicoBar = document.getElementById('planBasicoBar');
const planProPct = document.getElementById('planProPct');
const planProBar = document.getElementById('planProBar');
const planSuperProPct = document.getElementById('planSuperProPct');
const planSuperProBar = document.getElementById('planSuperProBar');

// Selectors
const storeSelector = document.getElementById('storeSelector');
const btnLaunchStore = document.getElementById('btnLaunchStore');

// Toast helper
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-triangle-exclamation';

    toast.innerHTML = `<i class="fa-solid ${iconClass}"></i> ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Load configurations
function initConfig() {
    apiUrlInput.value = state.apiBaseUrl;
    updateModeButtonUI();
}

// Update Mode Button UI
function updateModeButtonUI() {
    if (state.isRealMode) {
        btnToggleMode.className = 'btn-mode-toggle real-data';
        btnToggleMode.querySelector('span').innerText = 'Datos de API';
        btnToggleMode.querySelector('i').className = 'fa-solid fa-database';
        apiUrlInput.disabled = false;
    } else {
        btnToggleMode.className = 'btn-mode-toggle mock-data';
        btnToggleMode.querySelector('span').innerText = 'Simulación';
        btnToggleMode.querySelector('i').className = 'fa-solid fa-wand-magic-sparkles';
        apiUrlInput.disabled = true;
    }
}

// Toggle between Real API and Mock Mode
btnToggleMode.addEventListener('click', () => {
    state.isRealMode = !state.isRealMode;
    localStorage.setItem('saas_mode', state.isRealMode ? 'api' : 'mock');
    updateModeButtonUI();
    loadDashboardData();
    showToast(
        state.isRealMode ? 'Cambiado al modo de API Real' : 'Cambiado al modo de Simulación (Datos Simulados)', 
        state.isRealMode ? 'info' : 'success'
    );
});

// Reconnect click handler
btnReconnect.addEventListener('click', () => {
    if (state.isRealMode) {
        state.apiBaseUrl = apiUrlInput.value.trim();
        localStorage.setItem('saas_api_url', state.apiBaseUrl);
    }
    loadDashboardData();
});

// Calculate metrics and populate elements
function renderMetrics(negocios, perfiles) {
    const total = negocios.length;
    const activos = negocios.filter(n => n.estatus === 'Activo').length;
    const suspendidos = negocios.filter(n => n.estatus === 'Suspendido').length;
    
    // Count branches (sedes)
    let totalSedes = 0;
    perfiles.forEach(p => {
        if (p.sucursales_json) {
            try {
                const branches = typeof p.sucursales_json === 'string' ? JSON.parse(p.sucursales_json) : p.sucursales_json;
                if (Array.isArray(branches)) {
                    totalSedes += branches.length;
                }
            } catch (e) {
                console.error("Error parsing branch JSON:", e);
            }
        }
    });

    // Count plan distribution
    const countBasico = negocios.filter(n => n.plan === 'Básico').length;
    const countPro = negocios.filter(n => n.plan === 'PRO').length;
    const countSuperPro = negocios.filter(n => n.plan === 'SuperPRO').length;

    const pctBasico = total > 0 ? Math.round((countBasico / total) * 100) : 0;
    const pctPro = total > 0 ? Math.round((countPro / total) * 100) : 0;
    const pctSuperPro = total > 0 ? Math.round((countSuperPro / total) * 100) : 0;

    // Animation transition on stats
    animateValue(statTotalNegocios, parseInt(statTotalNegocios.innerText) || 0, total, 1000);
    animateValue(statPlanesActivos, parseInt(statPlanesActivos.innerText) || 0, activos, 1000);
    animateValue(statPlanesSuspendidos, parseInt(statPlanesSuspendidos.innerText) || 0, suspendidos, 1000);
    animateValue(statTotalSedes, parseInt(statTotalSedes.innerText) || 0, totalSedes, 1000);

    // Progress fills
    planBasicoPct.innerText = `${pctBasico}% (${countBasico})`;
    planBasicoBar.style.width = `${pctBasico}%`;
    
    planProPct.innerText = `${pctPro}% (${countPro})`;
    planProBar.style.width = `${pctPro}%`;
    
    planSuperProPct.innerText = `${pctSuperPro}% (${countSuperPro})`;
    planSuperProBar.style.width = `${pctSuperPro}%`;

    // Populate e-commerce business selector
    storeSelector.innerHTML = '';
    if (negocios.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.innerText = 'No hay negocios';
        storeSelector.appendChild(option);
    } else {
        // Only active businesses can have an online store
        const activeNegocios = negocios.filter(n => n.estatus === 'Activo');
        if (activeNegocios.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.innerText = 'Ninguno activo';
            storeSelector.appendChild(option);
        } else {
            activeNegocios.forEach(n => {
                const option = document.createElement('option');
                option.value = n.nombre;
                option.innerText = n.nombre;
                storeSelector.appendChild(option);
            });
        }
    }
}

// Animate numbers counting up/down
function animateValue(obj, start, end, duration) {
    if (start === end) {
        obj.innerText = end;
        return;
    }
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerText = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerText = end;
        }
    };
    window.requestAnimationFrame(step);
}

// Fetch real data from FastAPI endpoints
async function loadRealData() {
    apiStatusDot.className = 'status-dot loading';
    apiStatusText.innerText = 'Consultando API...';

    try {
        // Fetch businesses (negocios)
        const resNegocios = await fetch(`${state.apiBaseUrl}/datos/negocios`);
        if (!resNegocios.ok) throw new Error('No se pudo leer la tabla negocios.');
        const negocios = await resNegocios.json();

        // Fetch profiles (restaurantes_perfiles)
        let perfiles = [];
        try {
            const resPerfiles = await fetch(`${state.apiBaseUrl}/datos/restaurantes_perfiles`);
            if (resPerfiles.ok) {
                perfiles = await resPerfiles.json();
            }
        } catch (errProfile) {
            console.warn("Tabla restaurante_perfiles no disponible aún:", errProfile);
        }

        state.negocios = negocios;
        state.perfiles = perfiles;

        // Render stats
        renderMetrics(negocios, perfiles);

        // Update status UI to online
        apiStatusDot.className = 'status-dot online';
        apiStatusText.innerText = 'API & DB Conectadas';
        
        // Add pulse animations to nodes
        animateNodesPulse();
        showToast('Conectado con éxito a la API de Supabase', 'success');

    } catch (e) {
        console.error("API error:", e);
        apiStatusDot.className = 'status-dot offline';
        apiStatusText.innerText = 'API Desconectada';
        
        // Fallback to simulated data so dashboard isn't completely empty, but alert user
        state.negocios = MOCK_NEGOCIOS;
        state.perfiles = MOCK_PERFILES;
        renderMetrics(state.negocios, state.perfiles);

        showToast('Error conectando a la API. Mostrando datos simulados. Asegúrate de encender uvicorn en tu API.', 'error');
    }
}

// Animate nodes visually when connection checks complete
function animateNodesPulse() {
    const nodes = document.querySelectorAll('.node');
    nodes.forEach((n, idx) => {
        setTimeout(() => {
            n.style.transform = 'translateY(-10px) scale(1.08)';
            n.style.boxShadow = '0 15px 35px rgba(255,255,255,0.1)';
            setTimeout(() => {
                n.style.transform = '';
                n.style.boxShadow = '';
            }, 300);
        }, idx * 150);
    });
}

// Load simulated/mock data
function loadMockData() {
    apiStatusDot.className = 'status-dot loading';
    apiStatusText.innerText = 'Simulando...';
    
    setTimeout(() => {
        state.negocios = MOCK_NEGOCIOS;
        state.perfiles = MOCK_PERFILES;
        
        renderMetrics(state.negocios, state.perfiles);
        
        apiStatusDot.className = 'status-dot loading';
        apiStatusText.innerText = 'Modo Simulación Activo';
        animateNodesPulse();
    }, 400);
}

// Main logic coordinator
function loadDashboardData() {
    if (state.isRealMode) {
        loadRealData();
    } else {
        loadMockData();
    }
}

// Launch E-Commerce store logic
btnLaunchStore.addEventListener('click', () => {
    const selectedStore = storeSelector.value;
    if (!selectedStore) {
        showToast('Por favor selecciona un negocio activo para abrir su tienda.', 'error');
        return;
    }
    const storeUrl = `PANELCLIENTES/tienda/index.html?restaurant=${encodeURIComponent(selectedStore)}`;
    window.open(storeUrl, '_blank');
});

// Interactive architectural nodes actions
document.getElementById('nodeApi').addEventListener('click', () => {
    showToast('API Central: Abstrae base de datos PostgreSQL en Supabase. Corre sobre FastAPI.', 'info');
});

document.getElementById('nodeAdmin').addEventListener('click', () => {
    showToast('Panel Empresa: Crea registros en la base de datos de inquilinos y administra estatus y planes.', 'info');
});

document.getElementById('nodeClient').addEventListener('click', () => {
    showToast('Portal Inquilino: Permite al comerciante registrar logos, métodos de pago y crear sus sucursales.', 'info');
});

document.getElementById('nodeStore').addEventListener('click', () => {
    showToast('Tienda Online: Carga en tiempo real el catálogo de la sucursal seleccionada del cliente.', 'info');
});

// Setup on load
window.addEventListener('DOMContentLoaded', () => {
    initConfig();
    loadDashboardData();
});
