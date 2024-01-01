import { connect } from './lib.js'

dayjs.extend(dayjs_plugin_relativeTime)
const { summary, two_days } = connect("summary", "two_days")
document.addEventListener('alpine:init', () => {
  Alpine.store('summary', {})
  processSummary(Alpine.store('summary')).catch(console.error)
  processTwoDayData().catch(console.error)
})

const SUMMARIZE = {
  'time': value => dayjs(new Date(value)).fromNow(),
  'outdoor_temp': value => `${value}° F`,
}
async function processSummary(store) {
  for await (const data of summary) {
    for (const [key, value] of Object.entries(data)) {
      if (key in SUMMARIZE) {
        store[key] = SUMMARIZE[key](value)
      }
    }
  }
}

async function processTwoDayData() {
  let pressureData = []
  let temperatureData = []
  for await (const data of two_days) {
    pressureData.push({ x: data.time_bucket, y: data.pressure })
    temperatureData.push({ x: data.time_bucket, y: data.outdoor_temp })
  }
  new window.Chart(ctx, getTwoDayChart(pressureData, temperatureData))
}

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
