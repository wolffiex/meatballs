export function connect(...eventNames) {
  const eventSource = new EventSource('/api');
  eventSource.addEventListener('stream_stop', () => {
    eventSource.close();
  });
  return Object.fromEntries(eventNames.map(name => {
    const iterable = new AsyncQueue()
    eventSource.addEventListener(name, (event) => {
      const data = JSON.parse(event.data)
      if (data != null) {
        iterable.push(data)
      } else {
        iterable.finish()
      }
    })
    return [name, iterable]
  }))
}

class AsyncQueue {
  constructor() {
    this.queue = []
    this.pendingResolve = null
  }

  checkQ() {
    if (this.pendingResolve && this.queue.length) {
      this.pendingResolve(this.queue.shift())
    }
  }

  push(value) {
    this.queue.push({ value, done: false })
    this.checkQ()
  }

  finish() {
    this.queue.push({ value: undefined, done: true })
    this.checkQ()
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
