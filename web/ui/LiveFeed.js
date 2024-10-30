export class LiveFeed {
    constructor() {
        this.ui = {};
        this.setupUI();
    }

    setupUI() {
        this.ui.container = document.createElement('div');
        this.ui.container.classList.add('live-feed');
    }

    getElement() {
        return this.ui.container;
    }
}