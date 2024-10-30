import { ControlsWidget } from "./ControlsWidget.js";
import { LiveFeed } from "./LiveFeed.js";
import { LogTray } from "./LogTray.js";
import { PaneCollection } from "./PaneCollection.js";
import { Panel, ResizeablePanels } from "./ResizeablePanels.js";
import { TopControls } from "./TopControls.js";

export class Controller {
    constructor() {
        this.ui = {};

        this.renderQueue = [];

        this.setupUI();
    }

    setupUI() {
        this.logTray = new LogTray();
        const oldConsoleError = console.error;
        console.error = (...args) => {
            oldConsoleError(...args);
            this.logTray.error(...args);
        };

        const oldConsoleLog = console.log;
        console.log = (...args) => {
            oldConsoleLog(...args);
            this.logTray.log(...args);
        };

        const oldConsoleWarn = console.warn;
        console.warn = (...args) => {
            oldConsoleWarn(...args);
            this.logTray.warn(...args);
        };

        window.onerror = (message, source, lineno, colno, error) => {
            this.logTray.error(message, source, lineno, colno, error);
        }

        this.ui.container = document.createElement('div');
        this.ui.container.classList.add('web-pictest');

        this.topControls = new TopControls(this);
        this.ui.container.appendChild(this.topControls.getElement());

        this.ui.contentContainer = document.createElement('div');
        this.ui.contentContainer.classList.add('content-container');
        this.ui.container.appendChild(this.ui.contentContainer);

        this.controlsWidget = new ControlsWidget();
        this.ui.controlsWidgetPanel = new Panel();
        this.ui.controlsWidgetPanel.getElement().appendChild(this.controlsWidget.getElement());
       
        this.ui.logPanel = new Panel();
        this.ui.logPanel.getElement().appendChild(this.logTray.getElement());

        this.liveFeed = new LiveFeed();
        this.ui.liveFeedPanel = new Panel();
        this.ui.liveFeedPanel.getElement().appendChild(this.liveFeed.getElement());

        this.ui.controlsWidgetPanel.setBounds(0.5, 0, 1, 0.8);
        this.ui.liveFeedPanel.setBounds(0, 0, 0.5, 0.8);
        this.ui.logPanel.setBounds(0, 0.8, 1, 1);

        this.resizeablePanels = new ResizeablePanels();
        this.resizeablePanels.setPanels([
            this.ui.controlsWidgetPanel,
            this.ui.liveFeedPanel,
            this.ui.logPanel
        ]);

        this.ui.contentContainer.appendChild(this.resizeablePanels.getElement());
    }

    getElement() {
        return this.ui.container;
    }

    
}