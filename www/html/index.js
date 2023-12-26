import { greet } from './lib.js';

greet("gus")
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

const sseUrl = "/api"
const eventSource = new EventSource(sseUrl)

eventSource.onmessage = function(event) {
  console.log("New event:", event.data)
  if (event.data == "STOP") {
    console.log('JJJ')
    eventSource.close()
    console.log('OJJ')
  }
};

eventSource.onopen = function() {
    console.log("Connection to server opened.")
};

eventSource.onerror = function(error) {
    console.error("EventSource failed:", error)
    eventSource.close()
};
