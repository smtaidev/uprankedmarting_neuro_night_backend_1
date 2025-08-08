// frontend/scripts/utils/eventManager.js

export class EventManager {
    constructor() {
        this.events = {};
    }

    // Subscribe to an event
    on(eventName, callback) {
        if (!this.events[eventName]) {
            this.events[eventName] = [];
        }
        this.events[eventName].push(callback);
    }

    // Unsubscribe from an event
    off(eventName, callback) {
        if (this.events[eventName]) {
            this.events[eventName] = this.events[eventName].filter(cb => cb !== callback);
        }
    }

    // Emit an event
    emit(eventName, data = null) {
        if (this.events[eventName]) {
            this.events[eventName].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event callback for ${eventName}:`, error);
                }
            });
        }
    }

    // Subscribe to an event only once
    once(eventName, callback) {
        const onceCallback = (data) => {
            callback(data);
            this.off(eventName, onceCallback);
        };
        this.on(eventName, onceCallback);
    }

    // Remove all listeners for an event
    removeAllListeners(eventName) {
        if (eventName) {
            delete this.events[eventName];
        } else {
            this.events = {};
        }
    }

    // Get all event names
    getEventNames() {
        return Object.keys(this.events);
    }

    // Get listener count for an event
    getListenerCount(eventName) {
        return this.events[eventName] ? this.events[eventName].length : 0;
    }
}


