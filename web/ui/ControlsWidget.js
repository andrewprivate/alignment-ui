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
            type: 'scatter3d',
            marker: {
                color: 'rgb(17, 157, 255)',
                size: 4,
                line: {
                  color: 'rgb(231, 99, 250)',
                  width: 2
                }
            },
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

        this.controlsContainer = document.createElement('div');
        this.controlsContainer.classList.add('controls-container');

        this.movementContainer = document.createElement('div');
        this.movementContainer.classList.add('movement-container');

        // fiber selection container
        this.fiberSelectionContainer = document.createElement('div');
        this.fiberSelectionContainer.classList.add('fiber-selection-container');

        // fiber 1 button
        this.fiber1Button = document.createElement('button');
        this.fiber1Button.textContent = 'Fiber 1';
        this.fiber1Button.classList.add('fiber-button');
        this.fiberSelectionContainer.appendChild(this.fiber1Button);

        // fiber 2 button
        this.fiber2Button = document.createElement('button');
        this.fiber2Button.textContent = 'Fiber 2';
        this.fiber2Button.classList.add('fiber-button');
        this.fiberSelectionContainer.appendChild(this.fiber2Button);

        // align button
        this.alignButton = document.createElement('button');
        this.alignButton.textContent = 'Align';
        this.alignButton.classList.add('fiber-button');
        this.fiberSelectionContainer.appendChild(this.alignButton);

        this.alignButton.addEventListener('click', () => {
            window.eel.send_command('align');
        });

        this.movementContainer.appendChild(this.fiberSelectionContainer);

        // axis selection container
        this.axisSelectionContainer = document.createElement('div');
        this.axisSelectionContainer.classList.add('axis-selection-container');

        // select x 
        this.selectX = document.createElement('button');
        this.selectX.textContent = 'X Axis';
        this.selectX.classList.add('axis-button');
        this.axisSelectionContainer.appendChild(this.selectX);

        // select y
        this.selectY = document.createElement('button');
        this.selectY.textContent = 'Y Axis';
        this.selectY.classList.add('axis-button');
        this.axisSelectionContainer.appendChild(this.selectY);

        // select z
        this.selectZ = document.createElement('button');
        this.selectZ.textContent = 'Z Axis';
        this.selectZ.classList.add('axis-button');
        this.axisSelectionContainer.appendChild(this.selectZ);

        this.movementContainer.appendChild(this.axisSelectionContainer);

        // stage movement container
        this.stageMovementContainer = document.createElement('div');
        this.stageMovementContainer.classList.add('stage-movement-container');

        // move x
        this.moveXLeft = document.createElement('button');
        this.moveXLeft.textContent = '←';
        this.moveXLeft.classList.add('stage-movement-button');
        this.stageMovementContainer.appendChild(this.moveXLeft);
        this.moveXRight = document.createElement('button');
        this.moveXRight.textContent = '→';
        this.moveXRight.classList.add('stage-movement-button');
        this.stageMovementContainer.appendChild(this.moveXRight);

        // move y
        this.moveYUp = document.createElement('button');
        this.moveYUp.textContent = '↑';
        this.moveYUp.classList.add('stage-movement-button');
        this.stageMovementContainer.appendChild(this.moveYUp);
        this.moveYDown = document.createElement('button');
        this.moveYDown.textContent = '↓';
        this.moveYDown.classList.add('stage-movement-button');
        this.stageMovementContainer.appendChild(this.moveYDown);

        // move z
        this.moveZUp = document.createElement('button');
        this.moveZUp.textContent = '↑';
        this.moveZUp.classList.add('stage-movement-button');
        this.stageMovementContainer.appendChild(this.moveZUp);
        this.moveZDown = document.createElement('button');
        this.moveZDown.textContent = '↓';
        this.moveZDown.classList.add('stage-movement-button');
        this.stageMovementContainer.appendChild(this.moveZDown);

        this.movementContainer.appendChild(this.stageMovementContainer);

        // variable to store the selected fiber
        this.selectedFiber = null;

        // variable to store the selected axis
        this.selectedAxis = null;

        this.fiber1Button.addEventListener('click', () => {
            this.selectedFiber = 2;
            this.updateActiveButton(this.fiber1Button, 'fiber-button');
            console.log('Fiber 1 selected');
        });

        this.fiber2Button.addEventListener('click', () => {
            this.selectedFiber = 1;
            this.updateActiveButton(this.fiber2Button, 'fiber-button');
            console.log('Fiber 2 selected');
        });

        this.selectX.addEventListener('click', () => {
            this.selectedAxis = 'x';
            this.showAxisButtons();
            this.updateActiveButton(this.selectX, 'axis-button');
            console.log('X axis selected');
        });

        this.selectY.addEventListener('click', () => {
            this.selectedAxis = 'y';
            this.showAxisButtons();
            this.updateActiveButton(this.selectY, 'axis-button');
            console.log('Y axis selected');
        });

        this.selectZ.addEventListener('click', () => {
            this.selectedAxis = 'z';
            this.showAxisButtons();
            this.updateActiveButton(this.selectZ, 'axis-button');
            console.log('Z axis selected');
        });

        this.moveXLeft.addEventListener('click', () => {
            window.eel.move_stage(this.selectedFiber, this.selectedAxis, -100);
        });

        this.moveXRight.addEventListener('click', () => {
            window.eel.move_stage(this.selectedFiber, this.selectedAxis, 100);
        });

        this.moveYUp.addEventListener('click', () => {
            window.eel.move_stage(this.selectedFiber, this.selectedAxis, 100);
        });

        this.moveYDown.addEventListener('click', () => {
            window.eel.move_stage(this.selectedFiber, this.selectedAxis, -100);
        });

        this.moveZUp.addEventListener('click', () => {
            window.eel.move_stage(this.selectedFiber, this.selectedAxis, 100);
        });

        this.moveZDown.addEventListener('click', () => {
            window.eel.move_stage(this.selectedFiber, this.selectedAxis, -100);
        });

        // keyboard events
        document.addEventListener('keydown', (event) => {
            if (this.selectedFiber && this.selectedAxis) {
                if (event.key === 'ArrowLeft' && this.selectedAxis === 'x') {
                    window.eel.move_stage(this.selectedFiber, this.selectedAxis, -100);
                } else if (event.key === 'ArrowRight' && this.selectedAxis === 'x') {
                    window.eel.move_stage(this.selectedFiber, this.selectedAxis, 100);
                } else if (event.key === 'ArrowUp' && this.selectedAxis !== 'x') {
                    window.eel.move_stage(this.selectedFiber, this.selectedAxis, 100);
                } else if (event.key === 'ArrowDown' && this.selectedAxis !== 'x') {
                    window.eel.move_stage(this.selectedFiber, this.selectedAxis, -100);
                }
            }
        });

        this.powerMeterContainer = document.createElement('div');
        this.powerMeterContainer.classList.add('power-meter-container');

        this.powerReading = document.createElement('input');
        this.powerReading.type = 'text';
        this.powerReading.readOnly = true;
        this.powerReading.placeholder = 'Power Reading';
        this.powerReading.classList.add('power-meter-reading');
        this.powerMeterContainer.appendChild(this.powerReading);

        this.startButton = document.createElement('button');
        this.startButton.textContent = 'Start PM';
        this.startButton.classList.add('power-meter-button');
        this.powerMeterContainer.appendChild(this.startButton);

        this.stopButton = document.createElement('button');
        this.stopButton.textContent = 'Stop PM';
        this.stopButton.classList.add('power-meter-button');
        this.powerMeterContainer.appendChild(this.stopButton);

        this.startButton.addEventListener('click', () => {
            this.updateActiveButton(this.startButton, 'power-meter-button');
            window.eel.start_power_meter();
        });

        this.stopButton.addEventListener('click', () => {
            this.updateActiveButton(this.stopButton, 'power-meter-button');
            window.eel.stop_power_meter();
        });

        this.controlsContainer.appendChild(this.movementContainer);

        // vertical divider
        this.verticalDivider = document.createElement('div');
        this.verticalDivider.classList.add('vertical-divider');
        this.controlsContainer.appendChild(this.verticalDivider);

        this.controlsContainer.appendChild(this.powerMeterContainer);
        this.ui.container.appendChild(this.controlsContainer);

        this.hideAllAxisButtons();
    }

    updatePowerReading(reading) {
        this.powerReading.value = reading;
    }

    addPoint(x, y, z) {
        window.Plotly.extendTraces(this.plotElement, {
            x: [[x]],
            y: [[y]],
            z: [[z]]
        }, [0])
    }

    showAxisButtons() {
        this.hideAllAxisButtons();
        if(this.selectedAxis === 'x') {
            this.moveXLeft.style.display = 'inline-block';
            this.moveXRight.style.display = 'inline-block';
        } else if(this.selectedAxis === 'y') {
            this.moveYUp.style.display = 'inline-block';
            this.moveYDown.style.display = 'inline-block';
        } else if(this.selectedAxis === 'z') {    
            this.moveZUp.style.display = 'inline-block';
            this.moveZDown.style.display = 'inline-block';
        }
    }

    hideAllAxisButtons() {
        this.moveXLeft.style.display = 'none';
        this.moveXRight.style.display = 'none';
        this.moveYUp.style.display = 'none';
        this.moveYDown.style.display = 'none';
        this.moveZUp.style.display = 'none';
        this.moveZDown.style.display = 'none';
    }   

    updateActiveButton(button, className) {
        const buttons = document.getElementsByClassName(className);
        for (let i = 0; i < buttons.length; i++) {
            buttons[i].classList.remove('active');
        }
        button.classList.add('active');
    }

    clearActiveButtonsInMovementContainer() {
        const buttons = this.movementContainer.querySelectorAll('button');
        for (let i = 0; i < buttons.length; i++) {
            buttons[i].classList.remove('active');
        }
    }

    getElement() {
        return this.ui.container;
    }
}