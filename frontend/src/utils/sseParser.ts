/**
 * SSE (Server-Sent Events) Stream Parser
 * Parses text/event-stream format data and extracts task events
 */

export interface SSETaskEvent {
  type: string;
  task_id: string;
  task_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message?: string;
  error?: string;
  timestamp: number;
}

/**
 * Parse SSE stream
 *
 * @param reader - ReadableStream reader
 * @param onEvent - Generic event callback
 * @param onTaskEvent - Task event callback (triggered for TASK_* events)
 */
export function parseSSEStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  onEvent: (event: any) => void,
  onTaskEvent?: (taskEvent: SSETaskEvent) => void
): Promise<void> {
  const decoder = new TextDecoder();
  let buffer = '';

  return new Promise((resolve, reject) => {
    function read() {
      reader.read().then(({ done, value }) => {
        if (done) {
          resolve();
          return;
        }

        // Accumulate to buffer
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line

        // Process each complete line
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.substring(6).trim());

              // Generic event handling
              onEvent(event);

              // Task event handling (identify TASK_* prefixed events)
              if (event.type?.startsWith('TASK_')) {
                onTaskEvent?.(event as SSETaskEvent);
              }
            } catch (e) {
              console.error('Failed to parse SSE:', e, line);
            }
          }
        }

        // Continue reading
        read();
      }).catch(reject);
    }

    read();
  });
}

/**
 * Trigger task event (for external use)
 *
 * @param taskEvent - Task event object
 */
export function dispatchTaskEvent(taskEvent: SSETaskEvent) {
  document.dispatchEvent(new CustomEvent('sse-task-event', {
    detail: taskEvent
  }));
}
