const monthNames = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];
const currentMonth = new Date().getMonth()

const getWrappedMonthIndex = (monthIndex) => {
  if (monthIndex < 0) {
    return 12 + monthIndex; // Wrap around to December if monthIndex is negative
  }
  return monthIndex % 12; // Wrap around to January if monthIndex is greater than 11
};

const boughtDataArray = Object.values(boughtData);



function countOrdersPerMonth(data) {

  const monthCounts = Array(12).fill(0);

  data.forEach(item => {
    const date = new Date(item.date_ordered);
    const month = date.getMonth() - 1;

    monthCounts[month]++;
  });

  return monthCounts;
}

const ordersPerMonth = countOrdersPerMonth(boughtData);


const lineConfig = {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Paid',
        fill: false,
        /**
         * These colors come from Tailwind CSS palette
         * https://tailwindcss.com/docs/customizing-colors/#default-color-palette
         */
        backgroundColor: '#7e3af2',
        borderColor: '#7e3af2',
        data: [],
      },
    ],
  },
  options: {
    responsive: true,
    /**
     * Default legends are ugly and impossible to style.
     * See examples in charts.html to add your own legends
     *  */
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

function addDataToLineChart(newData) {

  lineConfig.data.datasets[0].data.push(newData);

  window.myLine.update();
}
lineConfig.data.datasets[0].data = ordersPerMonth;
const lineCtx = document.getElementById('line')
window.myLine = new Chart(lineCtx, lineConfig)