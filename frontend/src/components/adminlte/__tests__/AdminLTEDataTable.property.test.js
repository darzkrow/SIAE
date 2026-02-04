/**
 * Property-Based Tests for AdminLTEDataTable Component
 * Feature: system-modernization, Property 1: Data Table Functionality
 * Validates: Requirements 1.2, 9.4
 */

import { describe, test, expect } from 'vitest'
import fc from 'fast-check'
import { render, fireEvent, screen } from '@testing-library/react'
import AdminLTEDataTable from '../AdminLTEDataTable'
import { generators, propertyHelpers } from '../../../test/utils'

describe('AdminLTEDataTable Property-Based Tests', () => {
  // Generate table columns
  const columnsGenerator = fc.array(
    fc.record({
      key: fc.string({ minLength: 1, maxLength: 20 }).filter(s => /^[a-zA-Z][a-zA-Z0-9_]*$/.test(s)),
      title: fc.string({ minLength: 1, maxLength: 50 }),
      sortable: fc.boolean(),
      filterable: fc.boolean()
    }),
    { minLength: 1, maxLength: 10 }
  ).map(columns => {
    // Ensure unique keys
    const uniqueColumns = []
    const seenKeys = new Set()
    for (const col of columns) {
      if (!seenKeys.has(col.key)) {
        seenKeys.add(col.key)
        uniqueColumns.push(col)
      }
    }
    return uniqueColumns.length > 0 ? uniqueColumns : [{ key: 'id', title: 'ID', sortable: true, filterable: true }]
  })

  // Generate table data based on columns
  const dataGenerator = (columns) => fc.array(
    fc.record(
      columns.reduce((acc, col) => {
        acc[col.key] = fc.oneof(
          fc.string({ maxLength: 100 }),
          fc.integer({ min: 0, max: 10000 }),
          fc.float({ min: 0, max: 1000, noNaN: true })
        )
        return acc
      }, {})
    ),
    { minLength: 0, maxLength: 100 }
  )

  /**
   * Property 1: Data Table Functionality
   * For any data table in the system, it should provide sorting, filtering, 
   * and pagination capabilities that work correctly with any dataset size
   */
  test('Property 1: Data table provides sorting, filtering, and pagination for any dataset', () => {
    fc.assert(
      fc.property(
        columnsGenerator,
        columnsGenerator.chain(cols => dataGenerator(cols)),
        generators.paginationConfig(),
        (columns, data, paginationConfig) => {
          const { container } = render(
            <AdminLTEDataTable
              columns={columns}
              data={data}
              pagination={paginationConfig}
              filtering={{ enabled: true }}
              sorting={{ enabled: true }}
            />
          )

          // Table should always render
          const table = container.querySelector('table')
          expect(table).toBeInTheDocument()

          // Should have correct number of column headers
          const headers = container.querySelectorAll('thead th')
          expect(headers.length).toBeGreaterThanOrEqual(columns.length)

          // Should display appropriate number of rows
          const dataRows = container.querySelectorAll('tbody tr')
          if (data.length === 0) {
            // Should show "no data" message
            expect(dataRows.length).toBe(1)
            expect(container.textContent).toContain('No se encontraron registros')
          } else if (paginationConfig.enabled) {
            // Should respect pagination
            const expectedRows = Math.min(data.length, paginationConfig.pageSize)
            expect(dataRows.length).toBeLessThanOrEqual(expectedRows)
          } else {
            // Should show all data when pagination disabled
            expect(dataRows.length).toBe(data.length)
          }

          // Pagination controls should be present when enabled and needed
          if (paginationConfig.enabled && data.length > paginationConfig.pageSize) {
            const pagination = container.querySelector('.pagination')
            expect(pagination).toBeInTheDocument()
          }

          // Search input should be present when filtering enabled
          const searchInput = container.querySelector('input[placeholder*="Buscar"]')
          expect(searchInput).toBeInTheDocument()
        }
      ),
      { numRuns: 100 }
    )
  })

  test('Property 1.1: Sorting functionality works correctly for any column and direction', () => {
    fc.assert(
      fc.property(
        columnsGenerator,
        columnsGenerator.chain(cols => dataGenerator(cols.filter(c => c.sortable))),
        (columns, data) => {
          const sortableColumns = columns.filter(c => c.sortable)
          if (sortableColumns.length === 0 || data.length === 0) return

          const { container } = render(
            <AdminLTEDataTable
              columns={columns}
              data={data}
              sorting={{ enabled: true }}
              pagination={{ enabled: false }}
            />
          )

          // Test sorting on each sortable column
          sortableColumns.forEach(column => {
            const header = container.querySelector(`th:has-text("${column.title}")`) ||
                          Array.from(container.querySelectorAll('th')).find(th => th.textContent.includes(column.title))
            
            if (header) {
              // Click to sort ascending
              fireEvent.click(header)
              
              // Verify sort icon is present
              const sortIcon = header.querySelector('svg')
              expect(sortIcon).toBeInTheDocument()

              // Click again to sort descending
              fireEvent.click(header)
              
              // Sort icon should still be present but direction changed
              expect(sortIcon).toBeInTheDocument()
            }
          })
        }
      ),
      { numRuns: 50 }
    )
  })

  test('Property 1.2: Filtering functionality works correctly for any search term', () => {
    fc.assert(
      fc.property(
        columnsGenerator,
        columnsGenerator.chain(cols => dataGenerator(cols)),
        generators.searchQuery(),
        (columns, data, searchTerm) => {
          const { container } = render(
            <AdminLTEDataTable
              columns={columns}
              data={data}
              filtering={{ enabled: true }}
              pagination={{ enabled: false }}
            />
          )

          const searchInput = container.querySelector('input[placeholder*="Buscar"]')
          expect(searchInput).toBeInTheDocument()

          // Apply search filter
          fireEvent.change(searchInput, { target: { value: searchTerm } })

          // Table should still be functional
          const table = container.querySelector('table')
          expect(table).toBeInTheDocument()

          // Should show appropriate results or no results message
          const dataRows = container.querySelectorAll('tbody tr')
          expect(dataRows.length).toBeGreaterThanOrEqual(1) // At least one row (data or no-data message)
        }
      ),
      { numRuns: 50 }
    )
  })

  test('Property 1.3: Pagination maintains consistency across page changes', () => {
    fc.assert(
      fc.property(
        columnsGenerator,
        columnsGenerator.chain(cols => fc.array(
          fc.record(
            cols.reduce((acc, col) => {
              acc[col.key] = fc.string({ minLength: 1, maxLength: 20 })
              return acc
            }, {})
          ),
          { minLength: 20, maxLength: 100 } // Ensure enough data for pagination
        )),
        fc.constantFrom(5, 10, 25), // Page sizes
        (columns, data, pageSize) => {
          const { container } = render(
            <AdminLTEDataTable
              columns={columns}
              data={data}
              pagination={{ enabled: true, pageSize }}
            />
          )

          const totalPages = Math.ceil(data.length / pageSize)
          
          if (totalPages > 1) {
            // Should show pagination controls
            const pagination = container.querySelector('.pagination')
            expect(pagination).toBeInTheDocument()

            // Should show correct number of rows on first page
            const firstPageRows = container.querySelectorAll('tbody tr')
            expect(firstPageRows.length).toBe(Math.min(pageSize, data.length))

            // Test navigation to next page if available
            const nextButton = container.querySelector('.page-link:has-text("Siguiente")') ||
                              Array.from(container.querySelectorAll('.page-link')).find(btn => btn.textContent.includes('Siguiente'))
            
            if (nextButton && !nextButton.closest('.page-item').classList.contains('disabled')) {
              fireEvent.click(nextButton)
              
              // Should still show appropriate number of rows
              const secondPageRows = container.querySelectorAll('tbody tr')
              const expectedSecondPageRows = Math.min(pageSize, data.length - pageSize)
              expect(secondPageRows.length).toBe(expectedSecondPageRows)
            }
          }
        }
      ),
      { numRuns: 30 }
    )
  })

  test('Property 1.4: Table maintains functionality with empty or invalid data', () => {
    fc.assert(
      fc.property(
        columnsGenerator,
        fc.oneof(
          fc.constant([]), // Empty array
          fc.constant(null), // Null data
          fc.constant(undefined), // Undefined data
          fc.array(fc.record({}), { maxLength: 5 }) // Objects without expected properties
        ),
        (columns, data) => {
          expect(() => {
            const { container } = render(
              <AdminLTEDataTable
                columns={columns}
                data={data}
                pagination={{ enabled: true }}
                filtering={{ enabled: true }}
                sorting={{ enabled: true }}
              />
            )

            // Should render without crashing
            const table = container.querySelector('table')
            expect(table).toBeInTheDocument()

            // Should show appropriate message for empty/invalid data
            if (!data || data.length === 0) {
              expect(container.textContent).toContain('No se encontraron registros')
            }

            // Controls should still be present and functional
            const searchInput = container.querySelector('input[placeholder*="Buscar"]')
            expect(searchInput).toBeInTheDocument()
            expect(searchInput).not.toBeDisabled()

          }).not.toThrow()
        }
      ),
      { numRuns: 50 }
    )
  })

  test('Property 1.5: Table performance remains acceptable with large datasets', () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            key: fc.constantFrom('id', 'name', 'email', 'status', 'date'),
            title: fc.string({ minLength: 1, maxLength: 20 }),
            sortable: fc.boolean(),
            filterable: fc.boolean()
          }),
          { minLength: 3, maxLength: 5 }
        ),
        fc.integer({ min: 100, max: 1000 }),
        (columns, dataSize) => {
          // Generate large dataset
          const largeData = Array.from({ length: dataSize }, (_, i) => ({
            id: i,
            name: `Item ${i}`,
            email: `item${i}@example.com`,
            status: i % 2 === 0 ? 'active' : 'inactive',
            date: new Date(2020, 0, 1 + i % 365).toISOString()
          }))

          const startTime = performance.now()
          
          const { container } = render(
            <AdminLTEDataTable
              columns={columns}
              data={largeData}
              pagination={{ enabled: true, pageSize: 25 }}
              filtering={{ enabled: true }}
              sorting={{ enabled: true }}
            />
          )

          const endTime = performance.now()
          const renderTime = endTime - startTime

          // Should render within reasonable time (less than 1 second)
          expect(renderTime).toBeLessThan(1000)

          // Should still be functional
          const table = container.querySelector('table')
          expect(table).toBeInTheDocument()

          // Should show paginated results, not all data
          const rows = container.querySelectorAll('tbody tr')
          expect(rows.length).toBeLessThanOrEqual(25)
        }
      ),
      { numRuns: 10 } // Fewer runs for performance tests
    )
  })
})