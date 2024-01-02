export function connect(...eventNames) {
  const eventSource = new EventSource('/api');
  eventSource.addEventListener('stream_stop', () => {
    eventSource.close();
  });
  return Object.fromEntries(eventNames.map(name => {
    const iterable = new AsyncQueue()
    eventSource.addEventListener(name, (event) => {
      const data = JSON.parse(event.data)
      iterable.push(data)
    })
    return [name, iterable]
  }))
}

class AsyncQueue {
  constructor() {
    this.queue = []
    this.pendingResolve = null
  }

  push(value) {
    const nextResult = value == null ? { undefined, done: true } : { value, done: false }
    this.queue.push(nextResult)
    if (this.pendingResolve) {
      this.pendingResolve(this.queue.shift())
    }
  }

  finish() {
    this.queue.push({ value: undefined, done: true })
  }

  // Instance is async iterable
  [Symbol.asyncIterator]() {
    return this;
  }

  // Async iterator protocol method
  async next() {
    return new Promise((resolve, reject) => {
      this.pendingResolve = resolve;
    });
  }
}
