document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const insightsContainer = document.getElementById('insightsContainer');
    const noDataMessage = document.getElementById('noDataMessage');
    const previewContainer = document.getElementById('previewContainer');

    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFileUpload);
    }

    if (window.location.pathname === '/insights') {
        const savedData = sessionStorage.getItem('data');
        if (savedData) {
            const parsedData = JSON.parse(savedData);
            displayPreview(parsedData);
            displayInsights(parsedData.insights);
        } else {
            showNoDataMessage();
        }
    }
});

async function handleFileUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        showLoadingIndicator();
        
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        sessionStorage.setItem('data', JSON.stringify(data));
        
        window.location.href = '/insights';
        
    } catch (error) {
        alert('Error processing file: ' + error.message);
    } finally {
        hideLoadingIndicator();
    }
}

function displayPreview(data) {
    const previewContainer = document.getElementById('previewContainer');
    const previewHeader = document.getElementById('previewHeader');
    const previewBody = document.getElementById('previewBody');
    const totalRows = document.getElementById('totalRows');
    const totalColumns = document.getElementById('totalColumns');
    const columnTypes = document.getElementById('columnTypes');

    // Display preview table
    previewHeader.innerHTML = data.columns.map(col => `<th>${col}</th>`).join('');
    previewBody.innerHTML = data.preview.map(row => 
        `<tr>${data.columns.map(col => `<td>${row[col]}</td>`).join('')}</tr>`
    ).join('');

    // Display basic stats
    totalRows.textContent = data.basic_stats.total_rows;
    totalColumns.textContent = data.basic_stats.total_columns;
    columnTypes.innerHTML = Object.entries(data.basic_stats.column_types)
        .map(([col, type]) => `<li>${col}: ${type}</li>`)
        .join('');

    previewContainer.classList.remove('d-none');
}

function displayInsights(data) {
    document.getElementById('insightsContainer').classList.remove('d-none');
    document.getElementById('noDataMessage').classList.add('d-none');

    updateBasicStats(data.basic_stats);

    createChart('genderChart', data.gender_distribution);
    createChart('ageChart', data.age_distribution);
    createChart('salesTrendChart', data.monthly_trend);
    createChart('categoryChart', data.sales_by_category);
    createChart('segmentChart', data.customer_segments);
    createChart('quantityChart', data.quantity_distribution);
    createChart('ageCategoryChart', data.age_category_correlation);

    window.addEventListener('resize', resizeCharts);
}

function updateBasicStats(stats) {
    document.getElementById('totalSales').textContent = formatCurrency(stats.total_sales);
    document.getElementById('avgOrderValue').textContent = formatCurrency(stats.avg_order_value);
    document.getElementById('totalOrders').textContent = formatNumber(stats.total_orders);
    document.getElementById('uniqueCustomers').textContent = formatNumber(stats.unique_customers);
}

function createChart(elementId, chartData) {
    Plotly.newPlot(elementId, chartData.data, chartData.layout, {responsive: true});
}

function resizeCharts() {
    const charts = document.querySelectorAll('[id$="Chart"]');
    charts.forEach(chart => {
        Plotly.Plots.resize(chart);
    });
}

function showLoadingIndicator() {
    document.getElementById('loadingIndicator').classList.remove('d-none');
}

function hideLoadingIndicator() {
    document.getElementById('loadingIndicator').classList.add('d-none');
}

function showNoDataMessage() {
    document.getElementById('insightsContainer').classList.add('d-none');
    document.getElementById('previewContainer').classList.add('d-none');
    document.getElementById('noDataMessage').classList.remove('d-none');
}

function formatCurrency(num) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(num);
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}