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
    this._check()
  }

  _check() {
    if (this.pendingResolve && this.queue.length) {
      const pendingResolve = this.pendingResolve
      this.pendingResolve = null
      this.pendingReject = null
      pendingResolve(this.queue.shift())
    }
  }

  // Instance is async iterable
  [Symbol.asyncIterator]() {
    return this;
  }

  // Async iterator protocol method
  async next() {
    return new Promise((resolve, reject) => {
      if (this.pendingResolve != null) {
        this.pendingReject("Failed to await items in order")
      }
      this.pendingResolve = resolve;
      this.pendingRejext = reject
      this._check()
    });
  }
}
