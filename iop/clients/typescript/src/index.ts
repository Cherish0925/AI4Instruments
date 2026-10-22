export type Step = { id: string; device: string; operation: string; arguments?: Record<string, unknown>; after?: string[]; resources?: string[]; requirements?: Record<string, number>; bindings?: Record<string, { step: string; path?: (string | number)[] }> };
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
export type Submission = { name?: string; project?: string; experiment?: string; platform?: string; resources?: string[]; requirements?: Record<string, number>; parameters?: Record<string, unknown>; request_id?: string };
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
  async request<T>(path: string, body?: unknown, signal?: AbortSignal): Promise<T> {
    const response = await fetch(this.endpoint + path, { method: body === undefined ? 'GET' : 'POST',
      headers: { 'Authorization': 'Bearer ' + this.token, 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body), signal: signal ?? AbortSignal.timeout(this.timeout) });
    const value = await response.json();
    if (!response.ok) throw new IOPError(value.error ?? response.statusText, response.status);
    return value as T;
  }
  devices() { return this.request<Record<string, unknown>[]>('/v1/devices'); }
  discover() { return this.request<Record<string, unknown>>('/v1/discovery'); }
  register(record: Record<string, unknown>) { return this.request('/v1/devices', record); }
  adapters() { return this.request<Record<string, unknown>[]>('/v1/adapters'); }
  resources() { return this.request('/v1/resources'); }
  configureResources(capacities: Record<string, number>) { return this.request('/v1/resources', { capacities }); }
  reconnect(device: string) { return this.request('/v1/devices/' + encodeURIComponent(device) + '/reconnect', {}); }
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
  async submitPackage(archive: Uint8Array, options: Submission = {}): Promise<Run> {
    let text = '';
    for (let offset = 0; offset < archive.length; offset += 8192) text += String.fromCharCode(...archive.subarray(offset, offset + 8192));
    const record = await this.request<RunRecord>('/v1/packages', { ...options, archive: btoa(text), request_id: options.request_id ?? crypto.randomUUID() });
    return this.run(record.id);
  }
  run(id: string) { return new Run(this, id); }
  events(after = 0, runId?: string, wait = 0, signal?: AbortSignal) {
    const params = new URLSearchParams({ after: String(after), wait: String(wait) });
    if (runId) params.set('run_id', runId);
    return this.request<{ events: Event[]; cursor: number }>('/v1/events?' + params, undefined, signal);
  }
  async invoke(device: string, operation: string, args: Record<string, unknown> = {}, platform?: string) {
    const run = await this.submit([{ id: 'call', device, operation, arguments: args }], { platform });
    return ((await run.result()) as Record<string, unknown>).call;
  }
}
export class Run {
  constructor(readonly client: IOP, readonly id: string) {}
  info(details = true) { return this.client.request<RunRecord>('/v1/runs/' + encodeURIComponent(this.id) + (details ? '' : '?details=false')); }
  cancel() { return this.client.request<RunRecord>(`/v1/runs/${encodeURIComponent(this.id)}/cancel`, {}); }
  async wait(options: { signal?: AbortSignal; interval?: number } = {}): Promise<RunRecord> {
    let cursor = 0;
    for (;;) {
      options.signal?.throwIfAborted();
      const record = await this.info(false);
      if (terminal.has(record.state)) return this.info();
      const page = await this.client.events(cursor, this.id, Math.min(25, Math.max(0, this.client.timeout / 1000 - 1)), options.signal);
      cursor = page.cursor;
    }
  }
  async result(options: { signal?: AbortSignal; interval?: number } = {}): Promise<unknown> {
    const record = await this.wait(options);
    if (record.state !== 'completed') throw new IOPError(`${record.state}: ${record.error ?? this.id}`, 0);
    return record.result;
  }
  files() { return this.client.request<{ id: string; name: string; size: number; media_type: string }[]>(`/v1/runs/${encodeURIComponent(this.id)}/artifacts`); }
  operations(after = 0, limit = 200) { return this.client.request<{ operations: RunRecord[]; cursor: number }>(`/v1/runs/${encodeURIComponent(this.id)}/operations?` + new URLSearchParams({after:String(after),limit:String(limit)})); }
  saveResult(result: unknown) { return this.client.request(`/v1/runs/${encodeURIComponent(this.id)}/result`, { result }); }
  async invoke(device: string, operation: string, args: Record<string, unknown> = {}, options: { requestId?: string; signal?: AbortSignal } = {}) {
    let record = await this.client.request<RunRecord>(`/v1/runs/${encodeURIComponent(this.id)}/operations`, {
      device, operation, arguments: args, request_id: options.requestId ?? crypto.randomUUID()
    }, options.signal);
    let cursor = 0;
    while (!terminal.has(record.state)) {
      const page = await this.client.events(cursor, this.id, Math.min(25, Math.max(0, this.client.timeout / 1000 - 1)), options.signal);
      cursor = page.cursor;
      record = await this.client.request<RunRecord>('/v1/operations/' + encodeURIComponent(record.id), undefined, options.signal);
    }
    if (record.state !== 'completed') throw new IOPError(record.error ?? record.state, 0);
    return record.result;
  }
  async upload(name: string, file: Blob, signal?: AbortSignal) {
    const response = await fetch(this.client.endpoint + `/v1/runs/${encodeURIComponent(this.id)}/files?` + new URLSearchParams({ name }), {
      method: 'POST', headers: { Authorization: 'Bearer ' + this.client.token, 'Content-Type': 'application/octet-stream' },
      body: file, signal: signal ?? AbortSignal.timeout(this.client.timeout)
    });
    const value = await response.json();
    if (!response.ok) throw new IOPError(value.error ?? response.statusText, response.status);
    return value as { id: string; name: string; size: number };
  }
  async download(artifactId: string, signal?: AbortSignal): Promise<Response> {
    const response = await fetch(this.client.endpoint + '/v1/artifacts/' + encodeURIComponent(artifactId), {
      headers: { Authorization: 'Bearer ' + this.client.token }, signal: signal ?? AbortSignal.timeout(this.client.timeout)
    });
    if (!response.ok) throw new IOPError(response.statusText, response.status);
    return response;
  }
  async *watch(after = 0, signal?: AbortSignal): AsyncGenerator<Event> {
    let ended = false;
    for (;;) {
      signal?.throwIfAborted();
      const page = await this.client.events(after, this.id, Math.min(25, Math.max(0, this.client.timeout / 1000 - 1)), signal);
      for (const event of page.events) yield event;
      after = page.cursor;
      if (!page.events.length && terminal.has((await this.info(false)).state)) {
        if (ended) return;
        ended = true;
        continue;
      }
      if (!page.events.length) await delay(200, signal);
    }
  }
}
