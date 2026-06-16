// Global database holder
let dbData = null;
let umapChartInstance = null;

// Issue #4: Safe localStorage wrapper (handles SecurityError in sandboxed/private mode)
function safeStorage(key, value) {
  try {
    if (value !== undefined) localStorage.setItem(key, value);
    return localStorage.getItem(key);
  } catch(e) {
    return null;
  }
}

// Issue #8: Debounce timer for search input
let searchDebounceTimer = null;
function filterDatabaseDebounced() {
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(filterDatabase, 300);
}

// Cluster color palette matching Python scripts
const clusterColors = [
  '#E63946', // Cluster 1 - Red
  '#2D6A4F', // Cluster 2 - Forest Green
  '#457B9D', // Cluster 3 - Steel Blue
  '#1D3557', // Cluster 4 - Navy Blue
  '#52B788', // Cluster 5 - Light Green
  '#370617', // Cluster 6 - Dark Maroon
  '#FFB703', // Cluster 7 - Amber Orange
  '#8338EC'  // Cluster 8 - Vibrant Purple
];

// Switch Tab Navigation
function switchTab(tabId) {
  // Hide all tabs
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });
  
  // Deactivate all nav buttons
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Show target tab
  const targetTab = document.getElementById(tabId);
  if (targetTab) {
    targetTab.classList.add('active');
  }
  
  // Active nav button
  const activeBtn = Array.from(document.querySelectorAll('.nav-btn')).find(btn => 
    btn.getAttribute('onclick').includes(tabId)
  );
  if (activeBtn) {
    activeBtn.classList.add('active');
  }
  
  // Close sidebar drawer if active on mobile
  const sidebar = document.querySelector('aside');
  if (sidebar && sidebar.classList.contains('active')) {
    sidebar.classList.remove('active');
  }
  
  // Update header text based on page
  const titleEl = document.getElementById('page-title');
  const subtitleEl = document.getElementById('page-subtitle');
  
  if (tabId === 'dashboard') {
    titleEl.textContent = 'Dashboard Analisis Pangan';
    subtitleEl.textContent = 'Hasil Pembagian 8 Klaster Komposisi Produk Halal (MCA + Spectral Clustering)';
  } else if (tabId === 'umap') {
    titleEl.textContent = 'Peta Koordinat Spasial UMAP 2D';
    subtitleEl.textContent = 'Visualisasi Topologi Kesamaan Hubungan Komposisi Bahan Baku';
    // Re-render chart on tab display to prevent drawing dimension bugs
    if (umapChartInstance) {
      setTimeout(() => umapChartInstance.resize(), 100);
    }
  } else if (tabId === 'scanner') {
    titleEl.textContent = 'Live Halal Ingredient Scanner';
    subtitleEl.textContent = 'Audit Otomatis Kandungan Bahan Kritis Secara Instan Berbasis Aturan Fikih & Sains';
  } else if (tabId === 'database') {
    titleEl.textContent = 'Eksplorasi Database Produk Pangan';
    subtitleEl.textContent = 'Cari dan Filter Seluruh Produk Pangan dalam Database Pengujian Lapangan';
  }
}

// Format number helper
function formatPercent(val) {
  return val.toFixed(1) + '%';
}

// Load database JSON on start
window.addEventListener('DOMContentLoaded', async () => {
  // Initialize theme from storage (Issue #4: use safeStorage)
  const savedTheme = safeStorage('theme') || 'light';
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-theme');
  } else {
    document.body.classList.remove('dark-theme');
  }
  updateThemeUI();

  try {
    // Attempt loading via MessagePack for speed and size savings
    const response = await fetch('data/products_data.msgpack');
    if (response.ok) {
      const buffer = await response.arrayBuffer();
      dbData = MessagePack.decode(new Uint8Array(buffer));
      console.log('Database loaded successfully via MessagePack:', dbData);
    } else {
      console.warn('Gagal memuat data/products_data.msgpack, mencoba data/products_data.json...');
      const jsonResponse = await fetch('data/products_data.json');
      if (!jsonResponse.ok) {
        throw new Error('Gagal memuat database data/products_data.json');
      }
      dbData = await jsonResponse.json();
      console.log('Database loaded successfully via JSON fallback:', dbData);
    }
    
    // Initialize screens
    populateStats();
    renderClusterCards();
    populateClusterDropdown(); // Populate cluster filter dropdown from data
    initUMAPChart();
    populateDatabaseTable();
    
  } catch (error) {
    console.error('Error loading web app database:', error);
    alert('Error loading database file. Please check if generate_web_data.py has been run successfully.');
  }
});

// 1b. Populate Cluster Filter Dropdown dynamically from dbData
function populateClusterDropdown() {
  const select = document.getElementById('db-filter-cluster');
  if (!select || !dbData) return;
  // Remove all options except the first 'Semua Klaster' option
  while (select.options.length > 1) select.remove(1);
  dbData.clusters.forEach(c => {
    const opt = document.createElement('option');
    opt.value = String(c.id);
    opt.textContent = `Klaster ${c.id}: ${c.name}`;
    select.appendChild(opt);
  });
}

// 1c. Populate stats panel
function populateStats() {
  if (!dbData) return;
  
  const total = dbData.products.length;
  const halalCount = dbData.products.filter(p => p.o === 'Halal').length;
  const mushboohCount = dbData.products.filter(p => p.o === 'Mushbooh').length;
  const haraamCount = dbData.products.filter(p => p.o === 'Haraam').length;
  
  // Set counts dynamically
  document.getElementById('total-products-count').textContent = total.toLocaleString('id-ID');
  document.getElementById('total-products-desc').textContent = `Seluruh ${total.toLocaleString('id-ID')} produk ber-bahan baku dari RDF`;
  
  document.getElementById('overall-halal-rate').textContent = formatPercent((halalCount / total) * 100);
  document.getElementById('overall-mushbooh-rate').textContent = formatPercent((mushboohCount / total) * 100);
  document.getElementById('overall-haraam-rate').textContent = formatPercent((haraamCount / total) * 100);
}

// 2. Render 8 cluster cards
function renderClusterCards() {
  const container = document.getElementById('clusters-container');
  if (!container || !dbData) return;
  
  container.innerHTML = '';
  
  dbData.clusters.forEach(c => {
    const card = document.createElement('div');
    card.className = 'cluster-card';
    card.onclick = () => {
      // Jump to UMAP view and highlight this cluster
      switchTab('umap');
      // Highlight logic in chart can be triggered here
    };
    
    // Create lists of top 5 ingredients tags
    const tagsHTML = c.top_ingredients.map(ing => 
      `<span class="ing-tag">${ing.name} (${ing.pct.toFixed(0)}%)</span>`
    ).join('');
    
    card.innerHTML = `
      <div class="cluster-header">
        <span class="cluster-id-badge" style="background: ${clusterColors[c.id-1]}22; color: ${clusterColors[c.id-1]};">Klaster ${c.id}</span>
        <span class="cluster-size-badge">N = ${c.size} produk</span>
      </div>
      <h3 class="cluster-name">${c.name}</h3>
      
      <div class="halal-rates-container">
        <div class="rate-row">
          <div class="rate-label-row">
            <span class="rate-label halal">Halal</span>
            <span class="rate-value">${formatPercent(c.halal_pct)}</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar halal" style="width: ${c.halal_pct}%;"></div>
          </div>
        </div>
        <div class="rate-row">
          <div class="rate-label-row">
            <span class="rate-label mushbooh">Mushbooh</span>
            <span class="rate-value">${formatPercent(c.mushbooh_pct)}</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar mushbooh" style="width: ${c.mushbooh_pct}%;"></div>
          </div>
        </div>
        <div class="rate-row">
          <div class="rate-label-row">
            <span class="rate-label haraam">Haraam</span>
            <span class="rate-value">${formatPercent(c.haraam_pct)}</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar haraam" style="width: ${c.haraam_pct}%;"></div>
          </div>
        </div>
      </div>
      
      <h4 class="top-ingredients-title">Top Komposisi Paling Sering</h4>
      <div class="top-ingredients-tags">
        ${tagsHTML}
      </div>
    `;
    
    container.appendChild(card);
  });
}

// 3. Initialize Interactive UMAP Chart
function initUMAPChart() {
  const ctx = document.getElementById('umapChart');
  if (!ctx || !dbData) return;
  
  const isDark = document.body.classList.contains('dark-theme');
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
  const tickColor = isDark ? '#94a3b8' : '#475569';
  
  // Format datasets (1 series per cluster)
  const datasets = Array.from({ length: dbData.clusters.length }, (_, idx) => {
    const clusterIdx = idx + 1;
    const clusterProducts = dbData.products.filter(p => p.c === clusterIdx);
    return {
      label: `Klaster ${clusterIdx}: ${dbData.clusters[idx].name}`,
      data: clusterProducts.map(p => ({
        x: p.u1,
        y: p.u2,
        product: p
      })),
      backgroundColor: clusterColors[idx],
      borderColor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
      borderWidth: 0.5,
      pointRadius: 1.5,
      pointHoverRadius: 5,
      showLine: false
    };
  });
  
  umapChartInstance = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false // We render a custom floating legend panel to matches dark mode styling
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const p = context.raw.product;
              return `${p.l} (${p.m}) [${p.o}]`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: tickColor }
        },
        y: {
          grid: { color: gridColor },
          ticks: { color: tickColor }
        }
      },
      onClick: (event, activeElements) => {
        if (activeElements.length > 0) {
          const element = activeElements[0];
          const rawPoint = umapChartInstance.data.datasets[element.datasetIndex].data[element.index];
          if (rawPoint && rawPoint.product) {
            showProductDetail(rawPoint.product);
          }
        }
      }
    }
  });
  
  // Render custom HTML legend
  const legendContainer = document.getElementById('umap-legend');
  legendContainer.innerHTML = '';
  dbData.clusters.forEach((c, idx) => {
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.style.cursor = 'pointer';
    item.innerHTML = `
      <span class="legend-dot" style="background: ${clusterColors[idx]};"></span>
      <span>K${c.id}: ${c.name}</span>
    `;
    item.onclick = () => {
      // Toggle visibility in Chart.js
      const isVisible = umapChartInstance.isDatasetVisible(idx);
      if (isVisible) {
        umapChartInstance.hide(idx);
        item.style.opacity = '0.35';
      } else {
        umapChartInstance.show(idx);
        item.style.opacity = '1.0';
      }
    };
    legendContainer.appendChild(item);
  });
}

// Parenthesis-Aware Comma Splitter Function
function splitIngredients(text) {
  if (!text) return [];
  const parts = [];
  let current = [];
  let depth = 0;
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char === '(') {
      depth++;
    } else if (char === ')') {
      depth = Math.max(0, depth - 1);
    }
    
    if (char === ',' && depth === 0) {
      parts.push(current.join('').trim());
      current = [];
    } else {
      current.push(char);
    }
  }
  if (current.length > 0) {
    parts.push(current.join('').trim());
  }
  return parts.filter(p => p.length > 0);
}

// Comprehensive Halal Audit Rule Matcher (Fikih & Sains)
function getIngredientStatus(ing) {
  const clean = ing.toLowerCase().trim();
  
  // 1. Direct match in the database status rules
  for (let rule in dbData.status_rules) {
    if (rule === clean || clean === rule.replace(/_/g, ' ')) {
      return { status: dbData.status_rules[rule], matchedRule: rule.replace(/_/g, ' ').toUpperCase() };
    }
  }
  
  // 2. Specific override rules for high-risk halal targets
  if (clean.includes('pork') || clean.includes('pig') || clean.includes('lard') || clean.includes('bacon') || clean.includes('ham') || clean.includes('e120') || clean.includes('carmine') || clean.includes('cochineal') || clean.includes('karmin')) {
    if (clean.includes('e120') || clean.includes('carmine') || clean.includes('cochineal') || clean.includes('karmin')) {
      return { status: 'Haraam', matchedRule: 'Pewarna Karmin (E120) - Berasal dari serangga kutu daun Cochineal (Dilarang/Syubhat)' };
    }
    return { status: 'Haraam', matchedRule: 'BABI / PORK / LARD (Dilarang keras secara syariat)' };
  }
  
  if (clean.includes('beef') || clean.includes('meat') || clean.includes('chicken') || clean.includes('poultry') || clean.includes('animal') || clean.includes('gelatin') || /\bwhey\b/.test(clean) || clean.includes('cheese') || clean.includes('rennet')) {
    return { status: 'Mushbooh', matchedRule: 'Bahan kritis hewani (Butuh verifikasi sertifikat penyembelihan/asal hewan)' };
  }
  
  if (clean.includes('flavour') || clean.includes('flavor') || clean.includes('perisa') || clean === 'vanilla extract' || clean.includes('vanilla essence')) {
    return { status: 'Mushbooh', matchedRule: 'Perisa / Flavourings (Kritis karena pelarut alkohol/etanol industri)' };
  }

  if (clean.includes('emulsifier') || clean.includes('pengemulsi') || clean.includes('e471') || clean.includes('mono and diglycerides') || clean.includes('lecithin') || clean.includes('lesitin')) {
    return { status: 'Mushbooh', matchedRule: 'Pengemulsi / Emulsifier (Potensi lemak hewani)' };
  }
  
  // 3. Scan for any sub-tokens inside parentheses (recursive evaluation)
  const parenMatch = clean.match(/\(([^)]+)\)/);
  if (parenMatch) {
    const subText = parenMatch[1];
    const subIngs = splitIngredients(subText);
    let worst = { status: 'Halal', matchedRule: null };
    for (let sub of subIngs) {
      const subRes = getIngredientStatus(sub);
      if (subRes.status === 'Haraam') {
        return { status: 'Haraam', matchedRule: `${subRes.matchedRule} (Terdeteksi di dalam tanda kurung)` };
      } else if (subRes.status === 'Mushbooh') {
        worst = { status: 'Mushbooh', matchedRule: `${subRes.matchedRule} (Terdeteksi di dalam tanda kurung)` };
      }
    }
    if (worst.status !== 'Halal') return worst;
  }
  
  // 4. Default to Halal for typical botanical/mineral items
  return { status: 'Halal', matchedRule: 'Bahan nabati, mineral, atau sintetis umum yang halal' };
}

// Display product detail inside right card
function showProductDetail(p) {
  document.getElementById('det-title').textContent = p.l;
  document.getElementById('det-manufacturer').textContent = `Pabrikan: ${p.m}`;
  
  // Render Cert status badge (Issue #3: NOCERTIFICAT → 'nocert', not 'mushbooh')
  const certEl = document.getElementById('det-cert');
  const certClass = (p.s === 'New' || p.s === 'Renew') ? 'halal'
                  : (p.s === 'NOCERTIFICAT' || p.s === 'NoCertificate') ? 'nocert'
                  : 'mushbooh';
  certEl.innerHTML = `<span class="badge ${certClass}">${p.s}</span>`;
  
  // Render Halal status badge
  const halalEl = document.getElementById('det-halal');
  const hClass = p.o.toLowerCase();
  halalEl.innerHTML = `<span class="badge ${hClass}">${p.o}</span>`;
  
  // Render Cluster info
  const clusterInfo = dbData.clusters.find(c => c.id === p.c);
  const clusterName = clusterInfo ? clusterInfo.name : 'Tidak diketahui';
  document.getElementById('det-cluster').textContent = `Klaster ${p.c}: ${clusterName}`;
  
  // Render Ingredients with parenthetical parser
  const ings = splitIngredients(p.i);
  const ingListHTML = ings.map(ing => {
    const result = getIngredientStatus(ing);
    const statusClass = result.status.toLowerCase();
    return `<span class="ing-tag ${statusClass}" style="border-left: 2px solid var(--color-${statusClass});" title="Pemicu: ${result.matchedRule}">${ing}</span>`;
  }).join(' ');
  
  document.getElementById('det-ingredients').innerHTML = ingListHTML || '<span style="color: var(--text-muted);">Tidak terdaftar</span>';
}

// 4. Live Halal Scanner Logic
function runLiveAudit() {
  const inputText = document.getElementById('scanner-input-text').value;
  if (!inputText.trim()) {
    alert('Silakan masukkan bahan pangan terlebih dahulu.');
    return;
  }
  
  // Use our Parenthesis-Aware Splitter
  const ings = splitIngredients(inputText);
  const resultsContainer = document.getElementById('scan-results-list');
  resultsContainer.innerHTML = '';
  
  let finalStatus = 'Halal';
  let hasMushbooh = false;
  
  document.getElementById('scan-list-title').style.display = 'block';
  
  ings.forEach(ing => {
    const result = getIngredientStatus(ing);
    const status = result.status;
    const rule = result.matchedRule;
    
    if (status === 'Haraam') {
      finalStatus = 'Haraam';
    } else if (status === 'Mushbooh') {
      hasMushbooh = true;
    }
    
    const row = document.createElement('div');
    row.className = 'audited-ing-item';
    row.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 0.25rem;">
        <span class="audited-ing-name" style="font-weight: 500;">${ing}</span>
        <span style="font-size: 0.72rem; color: var(--text-muted);">${rule}</span>
      </div>
      <span class="badge ${status.toLowerCase()}">${status}</span>
    `;
    resultsContainer.appendChild(row);
  });
  
  if (finalStatus !== 'Haraam' && hasMushbooh) {
    finalStatus = 'Mushbooh';
  }
  
  // Render Banner Status
  const banner = document.getElementById('scanner-banner');
  banner.className = `scanner-status-banner ${finalStatus.toLowerCase()}`;
  banner.style.display = 'block';
  
  const title = document.getElementById('scanner-status-title');
  const desc = document.getElementById('scanner-status-desc');
  
  if (finalStatus === 'Halal') {
    title.textContent = 'Terdeteksi Halal Objektif';
    desc.textContent = 'Seluruh komposisi bahan dianalisis aman (berasal dari nabati, mineral, atau kimia sintetis halal).';
  } else if (finalStatus === 'Mushbooh') {
    title.textContent = 'Terdeteksi Mushbooh (Ragu / Syubhat)';
    desc.textContent = 'Ditemukan Titik Kritis Kehalalan (seperti potensi lemak hewani, susu berpembantu rennet, atau perisa dengan pelarut etanol). Memerlukan verifikasi logistik.';
  } else if (finalStatus === 'Haraam') {
    title.textContent = 'Terdeteksi Haraam (Dilarang)';
    desc.textContent = 'Ditemukan bahan yang mutlak dilarang dalam syariat Islam (seperti babi atau zat pewarna serangga Karmin E120).';
  }
}

// 5. Product Database Table Explorer
function populateDatabaseTable() {
  const body = document.getElementById('db-table-body');
  if (!body || !dbData) return;
  
  // Fetch search values and filter
  const query = document.getElementById('db-search').value.toLowerCase();
  const cleanQuery = query.replace(/[\s\-_]+/g, '');
  const filterCluster = document.getElementById('db-filter-cluster').value;
  const filterStatus = document.getElementById('db-filter-status').value;
  
  body.innerHTML = '';
  
  // Apply filtering rules
  let filtered = dbData.products.filter(p => {
    const labelClean = p.l.toLowerCase().replace(/[\s\-_]+/g, '');
    const manufacturerClean = p.m.toLowerCase().replace(/[\s\-_]+/g, '');
    
    const matchSearch = labelClean.includes(cleanQuery) || manufacturerClean.includes(cleanQuery);
    const matchCluster = filterCluster === '' || p.c === parseInt(filterCluster);
    const matchStatus = filterStatus === '' || p.o === filterStatus;
    return matchSearch && matchCluster && matchStatus;
  });
  
  // Limit to first 100 rows for scrolling speed
  const displayLimit = Math.min(100, filtered.length);

  // Issue #5: Show pagination info
  const infoEl = document.getElementById('db-result-info');
  if (infoEl) {
    if (filtered.length === 0) {
      infoEl.textContent = '';
      infoEl.style.display = 'none';
    } else if (filtered.length > 100) {
      infoEl.textContent = `Menampilkan 100 dari ${filtered.length.toLocaleString('id-ID')} hasil. Perjelas pencarian untuk hasil lebih spesifik.`;
      infoEl.style.display = 'block';
    } else {
      infoEl.textContent = `Menampilkan ${filtered.length.toLocaleString('id-ID')} hasil.`;
      infoEl.style.display = 'block';
    }
  }

  if (displayLimit === 0) {
    body.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 3rem; font-weight: 500;">Not found in database.<br><span style="font-size: 0.85rem; font-weight: normal; margin-top: 0.5rem; display: inline-block;">(Tidak ada produk yang cocok dengan parameter pencarian Anda di dalam database)</span></td></tr>`;
    return;
  }
  
  for (let i = 0; i < displayLimit; i++) {
    const p = filtered[i];
    const row = document.createElement('tr');
    
    const clusterInfo = dbData.clusters.find(c => c.id === p.c);
    
    // Shorten ingredients list for table preview
    let shortIngredients = p.i;
    if (p.i.length > 50) {
      shortIngredients = p.i.substring(0, 47) + '...';
    }
    
    // Issue #11: Conditional ellipsis (only append ... if name is actually truncated)
    const clusterShortName = clusterInfo.name.length > 25
      ? clusterInfo.name.substring(0, 25) + '...'
      : clusterInfo.name;

    // Issue #3: NOCERTIFICAT badge in table should use 'nocert' class
    const rowCertClass = (p.s === 'New' || p.s === 'Renew') ? 'halal'
                       : (p.s === 'NOCERTIFICAT' || p.s === 'NoCertificate') ? 'nocert'
                       : 'mushbooh';

    row.innerHTML = `
      <td style="font-weight: 500;">${p.l}</td>
      <td style="color: var(--text-secondary);">${p.m}</td>
      <td>
        <span style="font-size: 0.82rem; border-left: 2px solid ${clusterColors[p.c-1]}; padding-left: 6px;">
          K${p.c}: ${clusterShortName}
        </span>
      </td>
      <td><span class="badge ${rowCertClass}" style="font-size: 0.7rem;">${p.s}</span></td>
      <td><span class="badge ${p.o.toLowerCase()}" style="font-size: 0.7rem;">${p.o}</span></td>
      <td style="font-size: 0.8rem; color: var(--text-secondary);" title="${p.i}">${shortIngredients}</td>
    `;
    
    // Attach click to show detail inside UMAP tab
    row.style.cursor = 'pointer';
    row.onclick = () => {
      switchTab('umap');
      showProductDetail(p);
      
      // Zoom or highlight point in chart
      if (umapChartInstance) {
        // Find indices
        const datasetIdx = p.c - 1;
        const dataset = umapChartInstance.data.datasets[datasetIdx];
        const pointIdx = dataset.data.findIndex(pt => pt.product.id === p.id);
        
        if (pointIdx !== -1) {
          // Highlight point
          umapChartInstance.setActiveElements([{
            datasetIndex: datasetIdx,
            index: pointIdx
          }]);
          umapChartInstance.update();
        }
      }
    };
    
    body.appendChild(row);
  }
}

// Wrapper function to search/filter database
function filterDatabase() {
  populateDatabaseTable();
}

// Theme toggle logic
function toggleTheme() {
  const isDark = document.body.classList.toggle('dark-theme');
  safeStorage('theme', isDark ? 'dark' : 'light'); // Issue #4: use safeStorage
  updateThemeUI();
  
  // Dynamically update Chart.js colors
  if (umapChartInstance) {
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
    const tickColor = isDark ? '#94a3b8' : '#475569';
    
    umapChartInstance.options.scales.x.grid.color = gridColor;
    umapChartInstance.options.scales.x.ticks.color = tickColor;
    umapChartInstance.options.scales.y.grid.color = gridColor;
    umapChartInstance.options.scales.y.ticks.color = tickColor;
    
    umapChartInstance.update();
  }
}

function updateThemeUI() {
  const isDark = document.body.classList.contains('dark-theme');
  
  // Update desktop toggle
  const desktopBtn = document.querySelector('.theme-toggle-btn');
  if (desktopBtn) {
    const sunIcon = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`;
    const moonIcon = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
    
    desktopBtn.innerHTML = isDark ? 
      `${sunIcon}<span class="theme-btn-text">Switch to Light Theme</span>` : 
      `${moonIcon}<span class="theme-btn-text">Switch to Dark Theme</span>`;
  }
  
  // Update mobile toggle
  const mobileBtn = document.querySelector('.mobile-theme-toggle-btn');
  if (mobileBtn) {
    mobileBtn.innerHTML = isDark ? 
      `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>` : 
      `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
  }
}

// Mobile sidebar toggle
function toggleSidebar() {
  const sidebar = document.querySelector('aside');
  if (sidebar) {
    sidebar.classList.toggle('active');
  }
}
