export function connect(...eventNames) {
  const eventSource = new EventSource('/api');
  eventSource.addEventListener('stream_stop', () => {
    eventSource.close();
  });
  const iterableMap = Object.fromEntries(eventNames.map(name => [name, new AsyncQueue()]));
  eventSource.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    eventNames.forEach(name => {
      if (data.eventType === name) {
        iterableMap[name].push(data.payload);
      }
    });
  });

  return iterableMap
}

class AsyncQueue {
  constructor() {
    this.queue = []
    this.pending = null
  }

  push(value) {
    const nextResult = value == null
      ? { value: undefined, done: true }
      : { value, done: false }
    this.queue.push(nextResult)
    this._check()
  }

  _check() {
    if (this.pending && this.queue.length) {
      const { resolve } = this.pending
      this.pending = null
      resolve(this.queue.shift())
    }
  }

  // Instance is async iterable
  [Symbol.asyncIterator]() {
    return this;
  }

  // Async iterator protocol method
  async next() {
    return new Promise((resolve, reject) => {
      if (this.pending) {
        const { reject: pendingReject } = this.pending
        this.pending = null
        pendingReject(new Error("Failed to await items in order"))
      }
      this.pending = { resolve, reject }
      this._check()
    });
  }
}
