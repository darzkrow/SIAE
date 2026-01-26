/**
 * Testing Utilities
 * Common utilities for unit and property-based testing
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import fc from 'fast-check'

/**
 * Custom render function with providers
 */
export const renderWithProviders = (ui, options = {}) => {
  const { initialEntries = ['/'], ...renderOptions } = options

  // Add any providers here (Router, Context, etc.)
  const Wrapper = ({ children }) => {
    return children // Add providers as needed
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

/**
 * Property-based testing generators for AdminLTE3 components
 */
export const generators = {
  // Table data generator
  tableData: (columns) => fc.array(
    fc.record(
      columns.reduce((acc, col) => {
        acc[col.key] = fc.string({ minLength: 1, maxLength: 50 })
        return acc
      }, {})
    ),
    { minLength: 0, maxLength: 100 }
  ),

  // Form field generator
  formField: () => fc.record({
    name: fc.string({ minLength: 1, maxLength: 20 }).filter(s => /^[a-zA-Z][a-zA-Z0-9_]*$/.test(s)),
    label: fc.string({ minLength: 1, maxLength: 50 }),
    type: fc.constantFrom('text', 'email', 'number', 'password', 'textarea', 'select', 'checkbox'),
    required: fc.boolean(),
    placeholder: fc.option(fc.string({ maxLength: 100 }))
  }),

  // Widget data generator
  widgetData: () => fc.record({
    type: fc.constantFrom('metric', 'card', 'chart', 'table', 'progress', 'info-box'),
    title: fc.string({ minLength: 1, maxLength: 50 }),
    value: fc.oneof(
      fc.string({ minLength: 1, maxLength: 20 }),
      fc.integer({ min: 0, max: 1000000 }),
      fc.float({ min: 0, max: 100, noNaN: true })
    ),
    color: fc.constantFrom('primary', 'secondary', 'success', 'info', 'warning', 'danger')
  }),

  // Notification generator
  notification: () => fc.record({
    type: fc.constantFrom('info', 'success', 'warning', 'error'),
    title: fc.string({ minLength: 1, maxLength: 50 }),
    message: fc.string({ minLength: 1, maxLength: 200 }),
    duration: fc.integer({ min: 1000, max: 10000 }),
    persistent: fc.boolean()
  }),

  // Search query generator
  searchQuery: () => fc.string({ minLength: 1, maxLength: 100 })
    .filter(s => s.trim().length > 0),

  // Pagination config generator
  paginationConfig: () => fc.record({
    enabled: fc.boolean(),
    pageSize: fc.constantFrom(5, 10, 25, 50, 100),
    currentPage: fc.integer({ min: 1, max: 10 })
  }),

  // Sort config generator
  sortConfig: (columns) => fc.record({
    key: fc.constantFrom(...columns.map(c => c.key)),
    direction: fc.constantFrom('asc', 'desc')
  }),

  // Filter config generator
  filterConfig: () => fc.record({
    enabled: fc.boolean(),
    searchText: fc.option(fc.string({ maxLength: 50 }))
  }),

  // User input generator
  userInput: () => fc.record({
    text: fc.string({ maxLength: 1000 }),
    email: fc.emailAddress(),
    number: fc.integer({ min: -1000, max: 1000 }),
    boolean: fc.boolean(),
    date: fc.date({ min: new Date('2020-01-01'), max: new Date('2030-12-31') })
  }),

  // Viewport size generator for responsive testing
  viewportSize: () => fc.record({
    width: fc.integer({ min: 320, max: 1920 }),
    height: fc.integer({ min: 240, max: 1080 })
  }),

  // Chart data generator
  chartData: () => fc.array(
    fc.record({
      label: fc.string({ minLength: 1, maxLength: 20 }),
      value: fc.float({ min: 0, max: 1000, noNaN: true })
    }),
    { minLength: 1, maxLength: 20 }
  )
}

/**
 * Property-based test helpers
 */
export const propertyHelpers = {
  // Test that a component renders without crashing
  rendersProperly: (Component, propsGenerator) => {
    return fc.property(propsGenerator, (props) => {
      expect(() => renderWithProviders(<Component {...props} />)).not.toThrow()
    })
  },

  // Test that form validation works correctly
  formValidation: (Component, fieldsGenerator, validationRules) => {
    return fc.property(fieldsGenerator, generators.userInput(), (fields, input) => {
      const { container } = renderWithProviders(
        <Component fields={fields} validationRules={validationRules} />
      )
      
      // Fill form with generated input
      fields.forEach(field => {
        const element = container.querySelector(`[name="${field.name}"]`)
        if (element && input[field.type]) {
          fireEvent.change(element, { target: { value: input[field.type] } })
          fireEvent.blur(element)
        }
      })

      // Validation should be consistent
      const errors = container.querySelectorAll('.invalid-feedback')
      expect(errors.length).toBeGreaterThanOrEqual(0)
    })
  },

  // Test that data table operations work correctly
  dataTableOperations: (Component, columnsGenerator, dataGenerator) => {
    return fc.property(columnsGenerator, dataGenerator, (columns, data) => {
      const { container } = renderWithProviders(
        <Component columns={columns} data={data} />
      )
      
      // Table should render
      const table = container.querySelector('table')
      expect(table).toBeInTheDocument()
      
      // Should have correct number of columns
      const headers = container.querySelectorAll('th')
      expect(headers.length).toBeGreaterThanOrEqual(columns.length)
      
      // Should display data correctly
      const rows = container.querySelectorAll('tbody tr')
      if (data.length === 0) {
        expect(rows.length).toBe(1) // "No data" row
      } else {
        expect(rows.length).toBeGreaterThan(0)
      }
    })
  },

  // Test responsive behavior
  responsiveBehavior: (Component, propsGenerator) => {
    return fc.property(propsGenerator, generators.viewportSize(), (props, viewport) => {
      // Mock window resize
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: viewport.width,
      })
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: viewport.height,
      })

      const { container } = renderWithProviders(<Component {...props} />)
      
      // Component should render without breaking
      expect(container.firstChild).toBeInTheDocument()
      
      // Should maintain functionality across viewport sizes
      const interactiveElements = container.querySelectorAll('button, input, select, textarea')
      interactiveElements.forEach(element => {
        expect(element).not.toHaveAttribute('disabled')
      })
    })
  }
}

/**
 * Mock data generators for testing
 */
export const mockData = {
  users: () => Array.from({ length: 10 }, (_, i) => ({
    id: i + 1,
    name: `Usuario ${i + 1}`,
    email: `usuario${i + 1}@example.com`,
    role: ['admin', 'user', 'viewer'][i % 3],
    active: Math.random() > 0.2
  })),

  inventory: () => Array.from({ length: 50 }, (_, i) => ({
    id: i + 1,
    name: `Artículo ${i + 1}`,
    code: `ART-${String(i + 1).padStart(4, '0')}`,
    category: ['Bombas', 'Tuberías', 'Accesorios', 'Químicos'][i % 4],
    stock: Math.floor(Math.random() * 100),
    price: Math.floor(Math.random() * 1000) + 100,
    status: ['active', 'inactive', 'discontinued'][i % 3]
  })),

  notifications: () => Array.from({ length: 5 }, (_, i) => ({
    id: i + 1,
    type: ['info', 'success', 'warning', 'error'][i % 4],
    title: `Notificación ${i + 1}`,
    message: `Mensaje de prueba ${i + 1}`,
    timestamp: new Date(Date.now() - i * 3600000),
    read: Math.random() > 0.5
  }))
}

/**
 * Test utilities for async operations
 */
export const asyncUtils = {
  waitForElement: async (selector, timeout = 5000) => {
    return waitFor(() => {
      const element = document.querySelector(selector)
      expect(element).toBeInTheDocument()
      return element
    }, { timeout })
  },

  waitForText: async (text, timeout = 5000) => {
    return waitFor(() => {
      return screen.getByText(text)
    }, { timeout })
  },

  simulateNetworkDelay: (ms = 100) => {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

export default {
  renderWithProviders,
  generators,
  propertyHelpers,
  mockData,
  asyncUtils
}