import { greet } from './lib.js';

export function showMessage(message) {
    console.log(message);
}

// Initialization code that runs on module load
showMessage('Module is loaded and initialized!');
greet("gus")
