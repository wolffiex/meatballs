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
    this.setPending()
  }

  setPending() {
    this.pending = new Promise(resolve => {
      this.nextResolve = resolve
    })
  }

  push(value) {
    this.nextResolve({ value, done: false })
    this.setPending()
  }

  finish() {
    this.nextResolve({ value: undefined, done: true })
  }

  // Instance is async iterable
  [Symbol.asyncIterator]() {
    return this;
  }

  // Async iterator protocol method
  async next() {
    return this.pending
  }
}
