import { ServerEventStream } from './lib.js';
console.log('foo')

const ctx = document.getElementById('myChart');

new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
    datasets: [{
      label: '# of Votes',
      data: [12, 19, 3, 5, 2, 3],
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

console.log('jjj')
const eventStream = new ServerEventStream("/api")
console.log(eventStream)
const terters = eventStream.init("barometer", "fooof")
console.log(terters)
drain(terters.barometer)

async function drain(q) {
  console.log('drain', q)
  for await (const value of q) {
    console.log('inside', value)
  }
}
