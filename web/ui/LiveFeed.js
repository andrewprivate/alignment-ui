export class LiveFeed {
    constructor() {
        this.ui = {};
        this.setupUI();
    }

    setupUI() {
        this.ui.container = document.createElement('div');
        this.ui.container.classList.add('live-feed');

        this.ui.feed = document.createElement('img');
        this.ui.feed.classList.add('video-feed');
        this.ui.feed.id = 'video-feed';
        this.ui.container.appendChild(this.ui.feed);
    }

    getElement() {
        return this.ui.container;
    }
}