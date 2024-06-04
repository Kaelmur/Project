const pieLabels = ['0-5', '5-20', '20-40', '5-40', '40-70', 'Бутовый камень']

const pieConfig = {
  type: 'doughnut',
  data: {
    datasets: [
      {
        backgroundColor: ['#0694a2', '#1c64f2', '#7e3af2', '#fbbf24', '#f43f5e', '#64748b'],
        label: 'Dataset 1',
      },
    ],
    labels: pieLabels,
  },
  options: {
    responsive: true,
    cutoutPercentage: 80,
    legend: {
      display: false,
    },
  },
}

const fractionNameToIndex = {};
pieLabels.forEach((name, index) => {
  fractionNameToIndex[name] = index;
});

function countOrdersPerFraction(data) {

    const fractionCounts = Array(pieLabels.length).fill(0);

    data.forEach(item => {
        const fractionName = item.fraction;
        const fractionIndex = fractionNameToIndex[fractionName];

        fractionCounts[fractionIndex]++;
    });

    return fractionCounts;
}

pieConfig.data.datasets[0].data = countOrdersPerFraction(ordersData);

const pieCtx = document.getElementById('pie')
window.myPie = new Chart(pieCtx, pieConfig)
