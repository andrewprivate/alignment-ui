export class ControlsWidget {
    constructor() {
        this.ui = {};
        this.setupUI();
    }

    setupUI() {
        this.ui.container = document.createElement('div');
        this.ui.container.classList.add('controls-widget');

        this.plotElement = document.createElement('div');
        this.plotElement.classList.add('plot');
        this.ui.container.appendChild(this.plotElement);

        this.trace = {
            x: [],
            y: [],
            z: [],
            type: 'scatter3d'
        }
        window.Plotly.newPlot(this.plotElement, [this.trace],{
            margin: {
                l: 0,
                r: 0,
                b: 0,
                t: 0
            }
        },{
            responsive: true
        });
    }

    addPoint(x, y, z) {
        window.Plotly.extendTraces(this.plotElement, {
            x: [[x]],
            y: [[y]],
            z: [[z]]
        }, [0])
    }

    getElement() {
        return this.ui.container;
    }
}