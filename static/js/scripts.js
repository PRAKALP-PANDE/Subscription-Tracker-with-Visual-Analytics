// Fetch and render analysis results
document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const response = await fetch('/analyze');
    if (response.ok) {
      const data = await response.json();
  
      // Show the results container
      document.getElementById('analysisResults').classList.remove('hidden');
  
      // Render Peak Sales Chart
      const peakSalesCtx = document.getElementById('peakSalesChart').getContext('2d');
      new Chart(peakSalesCtx, {
        type: 'bar',
        data: {
          labels: data.peak_sales_periods.dates,
          datasets: [{
            label: 'Total Sales (₹)',
            data: data.peak_sales_periods.amounts,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            title: { display: true, text: 'Peak Sales Periods' }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
  
      // Render User Onboarding Trends Chart
      const onboardingTrendsCtx = document.getElementById('onboardingTrendsChart').getContext('2d');
      new Chart(onboardingTrendsCtx, {
        type: 'line',
        data: {
          labels: data.user_onboarding_trends.months,
          datasets: [{
            label: 'User Count',
            data: data.user_onboarding_trends.counts,
            backgroundColor: 'rgba(255, 99, 132, 0.6)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1,
            fill: true
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            title: { display: true, text: 'User Onboarding Trends' }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
    } else {
      alert('Failed to analyze data. Please try again later.');
    }
  });
  