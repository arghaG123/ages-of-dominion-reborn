// Port selection for the local preview. This does not stop another listener.

export function selectedPort(argv = [], env = {}) {
  let chosen = null;
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--port') chosen = argv[index + 1];
    else if (arg.startsWith('--port=')) chosen = arg.slice('--port='.length);
  }
  if ((chosen == null || chosen === '') && env.PORT) chosen = env.PORT;
  if (chosen == null || chosen === '') chosen = '4173';
  if (!/^\d+$/.test(String(chosen))) {
    throw new Error(`Selected port "${chosen}" is not a whole number. Use --port or PORT.`);
  }
  const port = Number(chosen);
  if (port < 1 || port > 65535) throw new Error(`Selected port ${port} is outside 1-65535.`);
  return port;
}

export function occupiedPortMessage(port) {
  return `Selected port ${port} on 127.0.0.1 is already in use. No other process was stopped. Pass --port or set PORT to a free port.`;
}

export function listeningMessage(port) {
  return `Reborn local preview: http://127.0.0.1:${port}`;
}
