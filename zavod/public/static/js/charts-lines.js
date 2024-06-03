const monthNames = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];
const currentMonth = new Date().getMonth()

const getWrappedMonthIndex = (monthIndex) => {
  if (monthIndex < 0) {
    return 12 + monthIndex;
  }
  return monthIndex % 12;
};

const boughtDataArray = Object.values(boughtData);

const lineConfig = {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Paid',
        fill: false,
        backgroundColor: '#7e3af2',
        borderColor: '#7e3af2',
        data: [],
      },
    ],
  },
  options: {
    responsive: true,
    legend: {
      display: false,
    },
    tooltips: {
      mode: 'index',
      intersect: false,
    },
    hover: {
      mode: 'nearest',
      intersect: true,
    },
    scales: {
      x: {
        display: true,
        scaleLabel: {
          display: true,
          labelString: 'Month',
        },
      },
      y: {
        display: true,
        scaleLabel: {
          display: true,
          labelString: 'Value',
        },
      },
    },
  },
}

for (let i = -3; i <= 3; i++) {
  const monthIndex = getWrappedMonthIndex(currentMonth + i);
  lineConfig.data.labels.push(monthNames[monthIndex]);
}

const monthNameToIndex = {};
lineConfig.data.labels.forEach((name, index) => {
  monthNameToIndex[name] = index;
});

function countOrdersPerMonth(data) {

  const monthCounts = Array(12).fill(0);

  data.forEach(item => {
    const date = new Date(item.date_ordered);
    const month = date.getMonth();
    const monthName = monthNames[month];
    const monthIndex = monthNameToIndex[monthName];

    monthCounts[monthIndex]++;
  });

  return monthCounts;
}

const ordersPerMonth = countOrdersPerMonth(boughtData);


function addDataToLineChart(newData) {

  lineConfig.data.datasets[0].data.push(newData);

  window.myLine.update();
}
lineConfig.data.datasets[0].data = ordersPerMonth;
const lineCtx = document.getElementById('line')
window.myLine = new Chart(lineCtx, lineConfig)