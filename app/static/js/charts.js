// Jolly Cabs Operations Management Suite (JOMS) - Brand Integrated Charts

(function() {
    let activeCharts = {};

    document.addEventListener('DOMContentLoaded', () => {
        initCharts();
        
        window.addEventListener('theme-changed', () => {
            initCharts();
        });
    });

    function getChartThemeColors() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        return {
            grid: isDark ? '#1E293B' : '#E5E7EB',
            text: isDark ? '#9CA3AF' : '#6B7280',
            tooltipBg: isDark ? '#0A1628' : '#FFFFFF',
            tooltipText: isDark ? '#FFFFFF' : '#1A1A2E',
            
            // Brand Colors
            primary: '#0A1628',   /* Deep Blue */
            accent: '#F5A623',    /* Accent Gold */
            accentLight: '#FFD166',
            success: '#10B981',
            danger: '#EF4444',
            info: '#3B82F6'
        };
    }

    function initCharts() {
        const theme = getChartThemeColors();
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        
        if (window.Chart) {
            Chart.defaults.color = theme.text;
            Chart.defaults.font.family = "'Inter', sans-serif";
            Chart.defaults.plugins.tooltip.backgroundColor = theme.tooltipBg;
            Chart.defaults.plugins.tooltip.titleColor = theme.tooltipText;
            Chart.defaults.plugins.tooltip.bodyColor = theme.tooltipText;
            Chart.defaults.plugins.tooltip.borderColor = theme.grid;
            Chart.defaults.plugins.tooltip.borderWidth = 1;
        } else {
            return;
        }

        Object.keys(activeCharts).forEach(key => {
            if (activeCharts[key]) {
                activeCharts[key].destroy();
            }
        });

        // 1. REVENUE TREND CHART (Using Gold line in Dark mode, Deep Blue line in Light mode)
        const revenueCtx = document.getElementById('revenueTrendChart');
        if (revenueCtx) {
            try {
                const rawData = JSON.parse(revenueCtx.dataset.chartData || '{}');
                const labels = rawData.labels || [];
                const data = rawData.values || [];
                const lineColor = isDark ? theme.accent : theme.primary;
                const areaColor = isDark ? 'rgba(245, 166, 35, 0.05)' : 'rgba(10, 22, 40, 0.04)';
                
                activeCharts.revenue = new Chart(revenueCtx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Revenue (INR)',
                            data: data,
                            borderColor: lineColor,
                            backgroundColor: areaColor,
                            fill: true,
                            tension: 0.3,
                            borderWidth: 2.5,
                            pointBackgroundColor: lineColor,
                            pointHoverRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: {
                                grid: { color: theme.grid },
                                ticks: { font: { size: 11 } }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { size: 11 } }
                            }
                        }
                    }
                });
            } catch (e) {
                console.error("Error drawing Revenue chart: ", e);
            }
        }

        // 2. BOOKINGS TREND CHART
        const bookingsCtx = document.getElementById('bookingsTrendChart');
        if (bookingsCtx) {
            try {
                const rawData = JSON.parse(bookingsCtx.dataset.chartData || '{}');
                const labels = rawData.labels || [];
                const data = rawData.values || [];
                const barColor = isDark ? 'rgba(255, 255, 255, 0.1)' : theme.primary;
                
                activeCharts.bookings = new Chart(bookingsCtx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Trips Placed',
                            data: data,
                            backgroundColor: barColor,
                            hoverBackgroundColor: theme.accent,
                            borderRadius: 4,
                            barPercentage: 0.5
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: {
                                grid: { color: theme.grid },
                                ticks: { stepSize: 1, font: { size: 11 } }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { size: 11 } }
                            }
                        }
                    }
                });
            } catch (e) {
                console.error("Error drawing Bookings chart: ", e);
            }
        }

        // 3. VEHICLE UTILIZATION CHART
        const vehicleCtx = document.getElementById('vehicleUtilizationChart');
        if (vehicleCtx) {
            try {
                const rawData = JSON.parse(vehicleCtx.dataset.chartData || '{}');
                const labels = rawData.labels || [];
                const values = rawData.values || [];
                
                activeCharts.vehicles = new Chart(vehicleCtx, {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: [theme.success, theme.accent, theme.danger],
                            borderWidth: 1.5,
                            borderColor: theme.tooltipBg
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { boxWidth: 10, padding: 12, font: { size: 11 } }
                            }
                        },
                        cutout: '75%'
                    }
                });
            } catch (e) {
                console.error("Error drawing Vehicle Utilization chart: ", e);
            }
        }

        // 4. DRIVER PERFORMANCE CHART
        const driverCtx = document.getElementById('driverPerformanceChart');
        if (driverCtx) {
            try {
                const rawData = JSON.parse(driverCtx.dataset.chartData || '{}');
                const labels = rawData.labels || [];
                const values = rawData.values || [];
                
                activeCharts.drivers = new Chart(driverCtx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Trips Completed',
                            data: values,
                            backgroundColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(10, 22, 40, 0.06)',
                            hoverBackgroundColor: theme.accent,
                            borderRadius: 3,
                            barPercentage: 0.5
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: {
                                grid: { color: theme.grid },
                                ticks: { font: { size: 11 } }
                            },
                            y: {
                                grid: { display: false },
                                ticks: { font: { size: 11 } }
                            }
                        }
                    }
                });
            } catch (e) {
                console.error("Error drawing Driver Performance chart: ", e);
            }
        }
    }
})();
