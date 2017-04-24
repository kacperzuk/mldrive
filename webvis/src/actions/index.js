export const newDevice = (device_id) => ({
  type: 'NEW_DEVICE',
  device_id
});

export const updateForm = (device_id, field, value) => ({
  type: 'UPDATE_FORM',
  device_id, field, value
});

export const updateTelemetry = (device_id, telemetry, value) => ({
  type: 'UPDATE_TELEMETRY',
  device_id, telemetry, value
});

export const setVisibleDevice = (device_id) => ({
  type: 'SET_VISIBLE_DEVICE',
  device_id
});

export const updateGamepad = (steering, throttle, debug) => ({
  type: 'UPDATE_GAMEPAD',
  steering, throttle, debug
});

export const clearForm = (device_id) => ({
  type: 'CLEAR_FORM',
  device_id
});
