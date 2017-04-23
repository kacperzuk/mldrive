import { updateGamepad } from './actions';
import connector from './connector';

class Controller {
  init(store) {
    this.store = store;
    this.last_ts = 0;
    this.tick();
  }
  tick() {
    requestAnimationFrame(this.tick.bind(this));

    const gamepad = navigator.getGamepads()[0];
    if(!gamepad) return;
    if(gamepad.timestamp === this.last_ts) return;


    let device_id = this.store.getState().uistate.visible_device;
    let steering = Math.round(90 + gamepad.axes[0]*20);
    let throttle = Math.round(80 - gamepad.axes[2]*20);
    this.last_ts = gamepad.timestamp;
    this.store.dispatch(updateGamepad(steering, throttle, gamepad));
    connector.sendOnce(`${device_id}/set/steering`, steering);
    connector.sendOnce(`${device_id}/set/throttle`, throttle);
  }
}

const controller = new Controller();

export default controller;
