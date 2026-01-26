import '@testing-library/jest-dom'

// Mock AdminLTE3 global objects
global.$ = global.jQuery = {
    fn: {
        DataTable: () => ({
            destroy: () => {},
            draw: () => {},
            clear: () => {},
            rows: {
                add: () => ({ draw: () => {} })
            }
        })
    }
}

// Mock Bootstrap components
global.bootstrap = {
    Modal: class {
        constructor() {}
        show() {}
        hide() {}
    },
    Toast: class {
        constructor() {}
        show() {}
        hide() {}
    },
    Tooltip: class {
        constructor() {}
        show() {}
        hide() {}
    }
}

// Mock Chart.js
global.Chart = {
    register: () => {},
    defaults: {
        global: {
            defaultFontFamily: 'Arial'
        }
    }
}

// Setup for property-based testing with fast-check
global.fc = require('fast-check')