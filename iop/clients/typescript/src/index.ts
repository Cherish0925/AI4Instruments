export type Step = { id: string; device: string; operation: string; arguments?: Record<string, unknown>; after?: string[]; resources?: string[] };
export type Endpoint = { device: string; port: string };
export type Procedure = { steps: Step[]; resources?: string[] };
export type PlatformDefinition = {
  schema_version: 1; id: string; name?: string; description?: string; devices: string[];
  resources?: { id: string; devices: string[]; description?: string; operations?: Record<string, string[]> }[];
  connections?: { from: Endpoint; to: Endpoint; kind: string; description?: string }[];
  procedures?: Record<string, Procedure>;
};
export type Platform = { id: string; revision: number; updated: string; definition: PlatformDefinition; active_runs?: string[]; missing_devices?: string[] };
export type RunRecord = { id: string; state: string; result?: unknown; error?: string; platform?: Platform; [key: string]: unknown };
export type Event = { sequence: number; kind: string; run_id?: string; [key: string]: unknown };
export type Submission = { name?: string; project?: string; experiment?: string; platform?: string; resources?: string[]; parameters?: Record<string, unknown>; request_id?: string };
export class IOPError extends Error {
  constructor(message: string, readonly status: number) { super(message); this.name = 'IOPError'; }
}
const terminal = new Set(['completed', 'failed', 'cancelled', 'interrupted']);
const delay = (ms: number, signal?: AbortSignal): Promise<void> => new Promise((resolve, reject) => {
  if (signal?.aborted) { reject(signal.reason); return; }
  const abort = () => { clearTimeout(timer); reject(signal?.reason); };
  const timer = setTimeout(() => { signal?.removeEventListener('abort', abort); resolve(); }, ms);
  signal?.addEventListener('abort', abort, { once: true });
});
export class IOP {
  readonly endpoint: string;
  constructor(endpoint = 'http://127.0.0.1:8765', readonly token = '', readonly timeout = 30000) {
    this.endpoint = endpoint.replace(/\/$/, '');
  }
  async request<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(this.endpoint + path, { method: body === undefined ? 'GET' : 'POST',
      headers: { 'Authorization': 'Bearer ' + this.token, 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(this.timeout) });
    const value = await response.json();
    if (!response.ok) throw new IOPError(value.error ?? response.statusText, response.status);
    return value as T;
  }
  devices() { return this.request<Record<string, unknown>[]>('/v1/devices'); }
  discover() { return this.request<Record<string, unknown>>('/v1/discovery'); }
  register(record: Record<string, unknown>) { return this.request('/v1/devices', record); }
  platforms() { return this.request<Platform[]>('/v1/platforms'); }
  platform(id: string) { return this.request<Platform>('/v1/platforms/' + encodeURIComponent(id)); }
  configurePlatform(definition: PlatformDefinition, expectedRevision = 0) {
    return this.request<Platform>('/v1/platforms', { definition, expected_revision: expectedRevision });
  }
  async procedure(platform: string, procedure = 'initialize', requestId = crypto.randomUUID()): Promise<Run> {
    const record = await this.request<RunRecord>(`/v1/platforms/${encodeURIComponent(platform)}/procedures/${encodeURIComponent(procedure)}`, { request_id: requestId });
    return this.run(record.id);
  }
  async submit(steps: Step[], options: Submission = {}): Promise<Run> {
    const record = await this.request<RunRecord>('/v1/runs', { ...options, steps, request_id: options.request_id ?? crypto.randomUUID() });
    return this.run(record.id);
  }
  run(id: string) { return new Run(this, id); }
  events(after = 0, runId?: string) {
    const params = new URLSearchParams({ after: String(after) });
    if (runId) params.set('run_id', runId);
    return this.request<{ events: Event[]; cursor: number }>('/v1/events?' + params);
  }
  async invoke(device: string, operation: string, args: Record<string, unknown> = {}, platform?: string) {
    const run = await this.submit([{ id: 'call', device, operation, arguments: args }], { platform });
    return ((await run.result()) as Record<string, unknown>).call;
  }
}
export class Run {
  constructor(readonly client: IOP, readonly id: string) {}
  info() { return this.client.request<RunRecord>('/v1/runs/' + encodeURIComponent(this.id)); }
  cancel() { return this.client.request<RunRecord>(`/v1/runs/${encodeURIComponent(this.id)}/cancel`, {}); }
  async wait(options: { signal?: AbortSignal; interval?: number } = {}): Promise<RunRecord> {
    for (;;) {
      options.signal?.throwIfAborted();
      const record = await this.info();
      if (terminal.has(record.state)) return record;
      await delay(options.interval ?? 100, options.signal);
    }
  }
  async result(options: { signal?: AbortSignal; interval?: number } = {}): Promise<unknown> {
    const record = await this.wait(options);
    if (record.state !== 'completed') throw new IOPError(`${record.state}: ${record.error ?? this.id}`, 0);
    return record.result;
  }
  async *watch(after = 0, signal?: AbortSignal): AsyncGenerator<Event> {
    let ended = false;
    for (;;) {
      signal?.throwIfAborted();
      const page = await this.client.events(after, this.id);
      for (const event of page.events) yield event;
      after = page.cursor;
      if (!page.events.length && terminal.has((await this.info()).state)) {
        if (ended) return;
        ended = true;
        continue;
      }
      if (!page.events.length) await delay(200, signal);
    }
  }
}
