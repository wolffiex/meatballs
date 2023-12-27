import { ServerEventStream } from './lib.js';


console.log('foo')

const ctx = document.getElementById('myChart');

// new Chart(ctx, {
//   type: 'bar',
//   data: {
//     labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
//     datasets: [{
//       label: '# of Votes',
//       data: [12, 19, 3, 5, 2, 3],
//       borderWidth: 1
//     }]
//   },
//   options: {
//     scales: {
//       y: {
//         beginAtZero: true
//       }
//     }
//   }
// });

const eventStream = new ServerEventStream("/api")
console.log(eventStream)
const terters = eventStream.init("barometer", "fooof")
console.log(terters)
drain(terters.barometer)

async function drain(q) {
  console.log('drain', q)
  const data = []
  for await (const {time, pressure} of q) {
    data.push({x: time * 1000, y: pressure})
  }
  console.log('infiit', data)
  const myChart = new window.Chart(ctx, {
      type: 'line',
      data: {
          datasets: [{
              label: 'Pressure',
              data,
              fill: false,
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1
          }]
      },
      options: {
          scales: {
              x: {
                  type: 'time',
                  time: {
                      unit: 'minute'
                  },
                  title: {
                      display: true,
                      text: 'Time'
                  }
              },
              y: {
                  beginAtZero: false,
                  title: {
                      display: true,
                      text: 'Pressure (hPa)'
                  }
              }
          }
      }
  });
}
