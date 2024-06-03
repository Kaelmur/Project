const fractionCounts = {};

ordersData.forEach(order => {
    const fraction = order.fraction;
    fractionCounts[fraction] = (fractionCounts[fraction] || 0) + 1;
});

const uniqueFractions = Object.keys(fractionCounts).sort();

const counts = uniqueFractions.map(fraction => fractionCounts[fraction]);

console.log(counts)

const pieConfig = {
  type: 'doughnut',
  data: {
    datasets: [
      {
        backgroundColor: ['#0694a2', '#1c64f2', '#7e3af2', '#fbbf24', '#f43f5e', '#64748b'],
        label: 'Dataset 1',
      },
    ],
    labels: ['0-5', '5-20', '20-40', '5-40', '40-70', 'Rubble_stone'],
  },
  options: {
    responsive: true,
    cutoutPercentage: 80,
    legend: {
      display: false,
    },
  },
}

pieConfig.data.datasets[0].data = counts;


const pieCtx = document.getElementById('pie')
window.myPie = new Chart(pieCtx, pieConfig)
