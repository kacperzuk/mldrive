export const newDevice = (device_id) => ({
  type: 'NEW_DEVICE',
  device_id
});

export const updateTelemetry = (device_id, telemetry, value) => ({
  type: 'UPDATE_TELEMETRY',
  device_id, telemetry, value
});
