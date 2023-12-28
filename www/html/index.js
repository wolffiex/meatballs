import { connect } from './lib.js';

const { summary, two_days } = connect("summary", "two_days")
console.log('foo', summary)
console.log('td', two_days)
summary.then(ooo => console.log('summary', ooo))
two_days.then(dd => {
  const pressureData = dd.map(item => ({ x: item.time_bucket, y: item.pressure }))
  const temperatureData = dd.map(item => ({ x: item.time_bucket, y: item.outdoor_temp }))
  console.log(pressureData[0])
  console.log(temperatureData[0])
  new window.Chart(ctx, getTwoDayChart(pressureData, temperatureData))
})

const ctx = document.getElementById('myChart');

function getTwoDayChart(pressureData, temperatureData) {
  return {
    type: 'line',
    data: {
      datasets: [
        {
          label: 'Pressure',
          data: pressureData,
          fill: false,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1,
          yAxisID: 'pressure'
        },
        {
          label: 'Temperature',
          data: temperatureData,
          fill: false,
          borderColor: 'rgb(255, 99, 132)',
          tension: 0.1,
          yAxisID: 'temperature'
        }
      ]
    },
    options: {
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'minute',
            stepSize: 60,
          },
          title: {
            display: true,
            text: 'Time'
          }
        },
        temperature: {
          type: 'linear',
          position: 'left', // Temperature on the left
          beginAtZero: false,
          title: {
            display: true,
            text: 'Temperature (°C)'
          },
          grid: {
            drawOnChartArea: true // Temperature has grid lines
          }
        },
        pressure: {
          type: 'linear',
          position: 'right', // Pressure on the right
          beginAtZero: false,
          title: {
            display: true,
            text: 'Pressure (hPa)'
          },
          grid: {
            drawOnChartArea: false // Pressure does not have grid lines
          }
        }
      }
    }
  }
}
