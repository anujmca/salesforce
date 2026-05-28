// APEXFORECAST DASHBOARD APP ENGINE (VANILLA JAVASCRIPT)

// Global app state
let currentData = null;
let filteredOpps = [];
let timelineChartInstance = null;
let regionChartInstance = null;

// Initialize app when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // 1. Load initial pre-compiled predictions from data.js
    if (typeof DEFAULT_FORECAST_DATA !== 'undefined') {
        currentData = JSON.parse(JSON.stringify(DEFAULT_FORECAST_DATA));
        initDashboard();
    } else {
        console.error("Default forecast data failed to load.");
    }
    
    // 2. Setup interactive event listeners
    setupEventListeners();
});

// Initialize dashboard UI components and charts
function initDashboard() {
    if (!currentData) return;
    
    // Populate region filters in table
    populateFilters();
    
    // Perform initial filtering and metric rendering
    updateDashboardView(0);
}

// Populate search & filter dropdown options
function populateFilters() {
    const regionFilter = document.getElementById('region-filter');
    regionFilter.innerHTML = '<option value="all">All Regions</option>';
    
    // Find unique regions in the dataset
    const regions = new Set();
    currentData.top_deals.forEach(deal => {
        if (deal.Region) regions.add(deal.Region);
    });
    
    // Add unique regions to selector
    Array.from(regions).sort().forEach(region => {
        const option = document.createElement('option');
        option.value = region;
        option.textContent = region;
        regionFilter.appendChild(option);
    });
}

// Update all components: KPI Cards, Charts, Tables, BU Cards based on slider threshold
function updateDashboardView(threshold) {
    // Filter opportunities above win probability threshold
    filteredOpps = currentData.top_deals.filter(deal => {
        const probPercent = (deal.Win_Probability || 0) * 100;
        return probPercent >= threshold;
    });

    // 1. Calculate & Render KPI Metrics
    calculateMetrics(threshold);
    
    // 2. Render Timeline (Fiscal Period) Chart
    renderTimelineChart(threshold);
    
    // 3. Render Regional Doughnut Chart
    renderRegionChart(threshold);
    
    // 4. Render BU segmentation
    renderBusinessUnits(threshold);
    
    // 5. Render active opportunities table
    renderDealsTable();
}

// Calculate primary KPIs with threshold adjustment
function calculateMetrics(threshold) {
    let totalNominal = 0;
    let totalExpected = 0;
    
    filteredOpps.forEach(deal => {
        const amt = parseFloat(deal['Un-Wtd Net Amount'] || deal.Amount || 0);
        const prob = parseFloat(deal.Win_Probability || 0);
        
        totalNominal += amt;
        totalExpected += (amt * prob);
    });
    
    const winrate = totalNominal > 0 ? (totalExpected / totalNominal) * 100 : 0;
    
    // Update KPI Card Texts
    animateValue('kpi-nominal', totalNominal, '$');
    animateValue('kpi-expected', totalExpected, '$');
    animateValue('kpi-winrate', winrate, '', '%');
}

// Animate numbers for extra visual polish (WOW factor)
function animateValue(id, endValue, prefix = '', suffix = '') {
    const obj = document.getElementById(id);
    if (!obj) return;
    
    const startValue = 0;
    const duration = 800; // ms
    let startTimestamp = null;
    
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const currentValue = progress * (endValue - startValue) + startValue;
        
        if (prefix === '$') {
            obj.innerHTML = prefix + formatCurrency(currentValue);
        } else if (suffix === '%') {
            obj.innerHTML = currentValue.toFixed(1) + suffix;
        } else {
            obj.innerHTML = currentValue.toFixed(0);
        }
        
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    
    window.requestAnimationFrame(step);
}

// Format number to currency style (e.g. $1,250,000)
function formatCurrency(value) {
    if (value >= 1.0e9) {
        return (value / 1.0e9).toFixed(2) + "B";
    } else if (value >= 1.0e6) {
        return (value / 1.0e6).toFixed(2) + "M";
    } else if (value >= 1.0e3) {
        return (value / 1.0e3).toFixed(0) + "K";
    }
    return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
}

// Render the main Line/Bar hybrid timeline chart
function renderTimelineChart(threshold) {
    const ctx = document.getElementById('timelineChart').getContext('2d');
    
    // Aggregate unweighted vs weighted pipeline by FP based on current filtered deals
    const fpMap = {};
    filteredOpps.forEach(deal => {
        const fp = String(deal['Expected FP'] || deal.Expected_Close_FP || 'Unknown').split('.')[0];
        const amt = parseFloat(deal['Un-Wtd Net Amount'] || deal.Amount || 0);
        const exp = amt * parseFloat(deal.Win_Probability || 0);
        
        if (!fpMap[fp]) {
            fpMap[fp] = { nominal: 0, expected: 0 };
        }
        fpMap[fp].nominal += amt;
        fpMap[fp].expected += exp;
    });
    
    // Sort fiscal periods chronologically
    const sortedFPs = Object.keys(fpMap).sort().filter(fp => fp !== 'Unknown' && fp.length === 6);
    // Take the top 10 future fiscal periods for readable scaling
    const targetFPs = sortedFPs.slice(0, 10);
    
    const nominalData = targetFPs.map(fp => fpMap[fp].nominal);
    const expectedData = targetFPs.map(fp => fpMap[fp].expected);
    
    // Format FP names to visual labels (e.g. "202701" -> "FP 01 (FY27)")
    const labels = targetFPs.map(fp => {
        const yr = fp.substring(2, 4);
        const period = fp.substring(4, 6);
        return `P${period} (FY${yr})`;
    });
    
    // Destroy previous instance to re-render smoothly
    if (timelineChartInstance) {
        timelineChartInstance.destroy();
    }
    
    timelineChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Risk-Adjusted expected revenue',
                    type: 'line',
                    data: expectedData,
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    order: 1
                },
                {
                    label: 'Total Nominal Pipeline',
                    data: nominalData,
                    backgroundColor: 'rgba(99, 102, 241, 0.3)',
                    borderColor: 'rgba(99, 102, 241, 0.8)',
                    borderWidth: 1,
                    borderRadius: 6,
                    order: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: 'hsl(0, 0%, 95%)', font: { family: 'Outfit', size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${context.raw.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: 'hsl(220, 14%, 68%)', font: { family: 'Outfit' } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: {
                        color: 'hsl(220, 14%, 68%)',
                        font: { family: 'Outfit' },
                        callback: function(value) { return '$' + formatCurrency(value); }
                    }
                }
            }
        }
    });
}

// Render the regional distribution doughnut chart
function renderRegionChart(threshold) {
    const ctx = document.getElementById('regionChart').getContext('2d');
    
    // Aggregate expected revenue by Region
    const regionMap = {};
    filteredOpps.forEach(deal => {
        const region = deal.Region || 'Unknown';
        const amt = parseFloat(deal['Un-Wtd Net Amount'] || deal.Amount || 0);
        const exp = amt * parseFloat(deal.Win_Probability || 0);
        
        if (!regionMap[region]) {
            regionMap[region] = 0;
        }
        regionMap[region] += exp;
    });
    
    const regions = Object.keys(regionMap).sort((a,b) => regionMap[b] - regionMap[a]);
    const values = regions.map(r => regionMap[r]);
    
    if (regionChartInstance) {
        regionChartInstance.destroy();
    }
    
    regionChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: regions,
            datasets: [{
                data: values,
                backgroundColor: [
                    'rgba(99, 102, 241, 0.75)',  // Indigo
                    'rgba(6, 182, 212, 0.75)',   // Cyan/Teal
                    'rgba(16, 185, 129, 0.75)',  // Green
                    'rgba(245, 158, 11, 0.75)',  // Amber Yellow
                    'rgba(239, 68, 68, 0.75)',   // Red
                    'rgba(156, 39, 176, 0.75)'   // Purple
                ],
                borderWidth: 1,
                borderColor: 'rgba(15, 23, 42, 0.85)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: 'hsl(220, 14%, 68%)', font: { family: 'Outfit', size: 11 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: $${context.raw.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// Render dynamic Business Unit performance cards
function renderBusinessUnits(threshold) {
    const container = document.getElementById('bu-cards-container');
    container.innerHTML = '';
    
    // Aggregate expected value by BU
    const buMap = {};
    filteredOpps.forEach(deal => {
        const bu = deal['Business Unit'] || 'Unknown';
        const amt = parseFloat(deal['Un-Wtd Net Amount'] || deal.Amount || 0);
        const exp = amt * parseFloat(deal.Win_Probability || 0);
        
        if (!buMap[bu]) {
            buMap[bu] = { nominal: 0, expected: 0 };
        }
        buMap[bu].nominal += amt;
        buMap[bu].expected += exp;
    });
    
    // Sort and take top 5
    const sortedBUs = Object.keys(buMap)
        .sort((a,b) => buMap[b].expected - buMap[a].expected)
        .slice(0, 5);
        
    sortedBUs.forEach(bu => {
        const card = document.createElement('div');
        card.className = 'bu-card';
        
        card.innerHTML = `
            <div class="bu-name" title="${bu}">${bu}</div>
            <div class="bu-metrics">
                <span class="bu-val">$${formatCurrency(buMap[bu].expected)}</span>
                <span class="bu-total">of $${formatCurrency(buMap[bu].nominal)} pipeline</span>
            </div>
        `;
        container.appendChild(card);
    });
    
    if (sortedBUs.length === 0) {
        container.innerHTML = '<p class="sim-description" style="grid-column: span 5; text-align:center;">No Business Units exceed current threshold criteria.</p>';
    }
}

// Render ranked active opportunities table
function renderDealsTable() {
    const tbody = document.getElementById('deals-table-body');
    tbody.innerHTML = '';
    
    // Read filters
    const searchVal = document.getElementById('deal-search').value.toLowerCase();
    const regionVal = document.getElementById('region-filter').value;
    
    // Filter based on input filters
    const finalTableOpps = filteredOpps.filter(deal => {
        const client = String(deal.Client || '').toLowerCase();
        const country = String(deal['Country/Entity'] || '').toLowerCase();
        const matchesSearch = client.includes(searchVal) || country.includes(searchVal);
        
        const matchesRegion = regionVal === 'all' || deal.Region === regionVal;
        
        return matchesSearch && matchesRegion;
    });
    
    // Limit to top 20 rows for readability and fast UI render
    const displayDeals = finalTableOpps.slice(0, 20);
    
    displayDeals.forEach(deal => {
        const tr = document.createElement('tr');
        const probVal = (deal.Win_Probability || 0) * 100;
        
        // Define probability class badge
        let probClass = 'prob-low';
        if (probVal >= 70) probClass = 'prob-high';
        else if (probVal >= 40) probClass = 'prob-mid';
        
        const amt = parseFloat(deal['Un-Wtd Net Amount'] || deal.Amount || 0);
        const exp = amt * parseFloat(deal.Win_Probability || 0);
        const fp = String(deal['Expected FP'] || deal.Expected_Close_FP || 'N/A').split('.')[0];
        
        tr.innerHTML = `
            <td class="deal-num">${deal['Opportunity Number'] || deal.Id || 'N/A'}</td>
            <td style="font-weight: 500;">${deal.Client || 'Unknown Client'}</td>
            <td>${deal.Region || 'N/A'}</td>
            <td>${deal['Business Unit'] || 'N/A'}</td>
            <td style="font-weight: 600;">$${amt.toLocaleString('en-US', { maximumFractionDigits: 0 })}</td>
            <td><span class="prob-badge ${probClass}">${probVal.toFixed(1)}%</span></td>
            <td style="font-weight: 700; color: var(--success);">$${exp.toLocaleString('en-US', { maximumFractionDigits: 0 })}</td>
            <td>${fp}</td>
        `;
        tbody.appendChild(tr);
    });
    
    if (displayDeals.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 32px;">No active deals matched the filtering criteria.</td></tr>';
    }
}

// Setup Event Listeners for interactive sliders, uploads & inputs
function setupEventListeners() {
    const slider = document.getElementById('probability-threshold');
    const sliderVal = document.getElementById('probability-threshold-val');
    
    // Slider Drag Event
    slider.addEventListener('input', (e) => {
        const val = e.target.value;
        sliderVal.textContent = val + '%';
        updateDashboardView(parseInt(val));
        
        // Reset active state of preset buttons
        document.querySelectorAll('.sim-presets .btn').forEach(btn => btn.classList.remove('active'));
    });
    
    // Preset Buttons click handlers
    document.getElementById('btn-all').addEventListener('click', (e) => {
        setActivePreset(e.target, 0);
    });
    
    document.getElementById('btn-mid').addEventListener('click', (e) => {
        setActivePreset(e.target, 40);
    });
    
    document.getElementById('btn-high').addEventListener('click', (e) => {
        setActivePreset(e.target, 60);
    });
    
    // Table Search event
    document.getElementById('deal-search').addEventListener('input', () => {
        renderDealsTable();
    });
    
    // Region Filter event
    document.getElementById('region-filter').addEventListener('change', () => {
        renderDealsTable();
    });
    
    // Setup File Drag and Drop uploader
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('csv-file-input');
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        }, false);
    });
    
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) handleFile(files[0]);
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });
}

// Preset button UI setter
function setActivePreset(targetBtn, value) {
    document.querySelectorAll('.sim-presets .btn').forEach(btn => btn.classList.remove('active'));
    targetBtn.classList.add('active');
    
    const slider = document.getElementById('probability-threshold');
    const sliderVal = document.getElementById('probability-threshold-val');
    
    slider.value = value;
    sliderVal.textContent = value + '%';
    
    updateDashboardView(value);
}

// Process and parse dragged/uploaded CSV file
function handleFile(file) {
    if (!file.name.endsWith('.csv')) {
        alert("Please upload a valid CSV file (.csv).");
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const text = e.target.result;
            const parsedData = parseCSV(text);
            
            if (parsedData.top_deals.length === 0) {
                alert("Error parsing CSV: No opportunities detected. Ensure columns match output headers.");
                return;
            }
            
            currentData = parsedData;
            initDashboard();
            alert(`Pipeline Successfully Loaded! Scored ${currentData.top_deals.length} active deals.`);
        } catch (err) {
            console.error(err);
            alert("Error parsing CSV. Please check formatting.");
        }
    };
    reader.readAsText(file);
}

// Custom RFC-4180 compliant CSV Parser
function parseCSV(text) {
    const lines = [];
    let row = [""];
    let inQuotes = false;
    
    // Ingest character-by-character to robustly handle commas inside quotes (e.g. client names)
    for (let i = 0; i < text.length; i++) {
        const c = text[i];
        const next = text[i+1];
        
        if (c === '"') {
            if (inQuotes && next === '"') {
                row[row.length - 1] += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (c === ',') {
            if (inQuotes) {
                row[row.length - 1] += c;
            } else {
                row.push("");
            }
        } else if (c === '\r' || c === '\n') {
            if (inQuotes) {
                row[row.length - 1] += c;
            } else {
                if (c === '\r' && next === '\n') i++;
                lines.push(row);
                row = [""];
            }
        } else {
            row[row.length - 1] += c;
        }
    }
    if (row.length > 1 || row[0] !== "") lines.push(row);
    
    if (lines.length < 2) return { top_deals: [] };
    
    const headers = lines[0].map(h => h.trim());
    const top_deals = [];
    
    // Map CSV rows to JS objects
    for (let i = 1; i < lines.length; i++) {
        const cells = lines[i];
        if (cells.length < headers.length) continue;
        
        const deal = {};
        headers.forEach((h, idx) => {
            deal[h] = cells[idx];
        });
        
        // Clean and type-cast key numerical variables
        deal['Un-Wtd Net Amount'] = parseFloat(deal['Un-Wtd Net Amount'] || deal.Amount || 0);
        deal['Win_Probability'] = parseFloat(deal.Win_Probability || 0);
        deal['Expected_Revenue'] = parseFloat(deal.Expected_Revenue || 0);
        
        top_deals.push(deal);
    }
    
    // Compute aggregates
    const total_unweighted = top_deals.reduce((sum, d) => sum + d['Un-Wtd Net Amount'], 0);
    const total_expected = top_deals.reduce((sum, d) => sum + d['Expected_Revenue'], 0);
    const avg_probability = top_deals.length > 0 ? (total_expected / total_unweighted) : 0;
    
    return {
        total_unweighted,
        total_expected,
        avg_probability,
        top_deals
    };
}
