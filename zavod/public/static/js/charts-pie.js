const fractionCounts = {};

ordersData.forEach(order => {
    const fraction = order.fraction;
    fractionCounts[fraction] = (fractionCounts[fraction] || 0) + 1;
});

const uniqueFractions = Object.keys(fractionCounts).sort();

const counts = uniqueFractions.map(fraction => fractionCounts[fraction]);

const pieConfig = {
  type: 'doughnut',
  data: {
    datasets: [
      {
        /**
         * These colors come from Tailwind CSS palette
         * https://tailwindcss.com/docs/customizing-colors/#default-color-palette
         */
        backgroundColor: ['#0694a2', '#1c64f2', '#7e3af2', '#fbbf24', '#f43f5e', '#64748b'],
        label: 'Dataset 1',
      },
    ],
    labels: ['0-5', '5-20', '20-40', '5-40', '40-70', 'Бутовый камень'],
  },
  options: {
    responsive: true,
    cutoutPercentage: 80,
    /**
     * Default legends are ugly and impossible to style.
     * See examples in charts.html to add your own legends
     *  */
    legend: {
      display: false,
    },
  },
}

pieConfig.data.datasets[0].data = counts;

// change this to the id of your chart element in HMTL
const pieCtx = document.getElementById('pie')
window.myPie = new Chart(pieCtx, pieConfig)
