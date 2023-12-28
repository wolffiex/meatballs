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

  // This method makes the instance itself an asynchronous iterable
  [Symbol.asyncIterator]() {
    return this;
  }

  // Async iterator protocol method
  async next() {
    return this.pending
  }
}

export class ServerEventStream {
  constructor(url) {
    this.url = url
  }

  _start() {
    const eventSource = new EventSource(this.url)

    eventSource.onmessage = event => {
      try {
        const data = JSON.parse(event.data)
        if (!data) {
          eventSource.close()
          return
        }
        const [topic, eventData] = data
        if (this.queues.has(topic)) {
          const queue = this.queues.get(topic)
          if (!eventData) {
            queue.finish()
          } else {
            queue.push(eventData)
          }
        }
      } catch (e) {
        console.error(e)
      }
    }

    eventSource.onopen = () => {
      console.log("Connection to server opened.")
    }

    eventSource.onerror = (error) => {
      console.error("EventSource failed:", error)
      eventSource.close()
    }
    this.eventSource = eventSource
  }

  init(...queueKeys) {
    this.queues = new Map(queueKeys.map(key => [key, new AsyncQueue()]))
    this._start()
    return Object.fromEntries(this.queues)
  }
}
