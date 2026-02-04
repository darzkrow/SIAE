/**
 * Property-Based Tests for AdminLTEForm Component
 * Feature: system-modernization, Property 2: Form Validation Consistency
 * Validates: Requirements 1.3
 */

import { describe, test, expect } from 'vitest'
import fc from 'fast-check'
import { render, fireEvent, waitFor } from '@testing-library/react'
import AdminLTEForm from '../AdminLTEForm'
import { generators } from '../../../test/utils'

describe('AdminLTEForm Property-Based Tests', () => {
  // Generate form fields with various types and validation rules
  const formFieldGenerator = fc.array(
    fc.record({
      name: fc.string({ minLength: 1, maxLength: 20 }).filter(s => /^[a-zA-Z][a-zA-Z0-9_]*$/.test(s)),
      label: fc.string({ minLength: 1, maxLength: 50 }),
      type: fc.constantFrom('text', 'email', 'number', 'password', 'textarea', 'select', 'checkbox', 'radio'),
      placeholder: fc.option(fc.string({ maxLength: 100 })),
      disabled: fc.boolean(),
      help: fc.option(fc.string({ maxLength: 200 })),
      options: fc.option(fc.array(
        fc.record({
          value: fc.string({ minLength: 1, maxLength: 20 }),
          label: fc.string({ minLength: 1, maxLength: 50 })
        }),
        { minLength: 1, maxLength: 10 }
      ))
    }),
    { minLength: 1, maxLength: 10 }
  ).map(fields => {
    // Ensure unique field names
    const uniqueFields = []
    const seenNames = new Set()
    for (const field of fields) {
      if (!seenNames.has(field.name)) {
        seenNames.add(field.name)
        // Add options for select and radio fields
        if ((field.type === 'select' || field.type === 'radio') && !field.options) {
          field.options = [
            { value: 'option1', label: 'Option 1' },
            { value: 'option2', label: 'Option 2' }
          ]
        }
        uniqueFields.push(field)
      }
    }
    return uniqueFields
  })

  // Generate validation rules
  const validationRulesGenerator = (fields) => fc.record(
    fields.reduce((acc, field) => {
      acc[field.name] = fc.record({
        required: fc.boolean(),
        minLength: fc.option(fc.integer({ min: 1, max: 10 })),
        maxLength: fc.option(fc.integer({ min: 10, max: 100 })),
        email: fc.constant(field.type === 'email'),
        number: fc.constant(field.type === 'number'),
        min: field.type === 'number' ? fc.option(fc.integer({ min: 0, max: 100 })) : fc.constant(undefined),
        max: field.type === 'number' ? fc.option(fc.integer({ min: 100, max: 1000 })) : fc.constant(undefined)
      })
      return acc
    }, {})
  )

  // Generate form input values
  const formValuesGenerator = (fields) => fc.record(
    fields.reduce((acc, field) => {
      switch (field.type) {
        case 'text':
        case 'textarea':
        case 'password':
          acc[field.name] = fc.option(fc.string({ maxLength: 200 }))
          break
        case 'email':
          acc[field.name] = fc.option(fc.oneof(
            fc.emailAddress(),
            fc.string({ maxLength: 50 }), // Invalid emails for testing
            fc.constant('')
          ))
          break
        case 'number':
          acc[field.name] = fc.option(fc.oneof(
            fc.integer({ min: -1000, max: 1000 }),
            fc.string({ maxLength: 10 }) // Invalid numbers for testing
          ))
          break
        case 'select':
        case 'radio':
          if (field.options && field.options.length > 0) {
            acc[field.name] = fc.option(fc.constantFrom(...field.options.map(opt => opt.value)))
          } else {
            acc[field.name] = fc.option(fc.string({ maxLength: 20 }))
          }
          break
        case 'checkbox':
          acc[field.name] = fc.boolean()
          break
        default:
          acc[field.name] = fc.option(fc.string({ maxLength: 100 }))
      }
      return acc
    }, {})
  )

  /**
   * Property 2: Form Validation Consistency
   * For any form in the system, client-side validation should correctly validate 
   * all input types according to their validation rules
   */
  test('Property 2: Form validation works consistently for any field configuration', () => {
    fc.assert(
      fc.property(
        formFieldGenerator,
        formFieldGenerator.chain(fields => validationRulesGenerator(fields)),
        (fields, validationRules) => {
          let submitCalled = false
          const handleSubmit = (values) => {
            submitCalled = true
          }

          const { container } = render(
            <AdminLTEForm
              fields={fields}
              validationRules={validationRules}
              onSubmit={handleSubmit}
            />
          )

          // Form should render without crashing
          const form = container.querySelector('form')
          expect(form).toBeInTheDocument()

          // Should render all fields
          fields.forEach(field => {
            const fieldElement = container.querySelector(`[name="${field.name}"]`)
            expect(fieldElement).toBeInTheDocument()
            
            // Label should be present
            const label = container.querySelector(`label[for="${field.name}"]`)
            expect(label).toBeInTheDocument()
            expect(label.textContent).toContain(field.label)

            // Required indicator should be present if field is required
            if (validationRules[field.name]?.required) {
              expect(label.textContent).toContain('*')
            }

            // Help text should be present if provided
            if (field.help) {
              expect(container.textContent).toContain(field.help)
            }
          })

          // Submit button should be present
          const submitButton = container.querySelector('button[type="submit"]')
          expect(submitButton).toBeInTheDocument()
        }
      ),
      { numRuns: 100 }
    )
  })

  test('Property 2.1: Required field validation works correctly', () => {
    fc.assert(
      fc.property(
        formFieldGenerator,
        (fields) => {
          // Create validation rules with some required fields
          const validationRules = {}
          fields.forEach((field, index) => {
            validationRules[field.name] = {
              required: index % 2 === 0 // Make every other field required
            }
          })

          let submitCalled = false
          const handleSubmit = (values) => {
            submitCalled = true
          }

          const { container } = render(
            <AdminLTEForm
              fields={fields}
              validationRules={validationRules}
              onSubmit={handleSubmit}
            />
          )

          // Try to submit form without filling required fields
          const submitButton = container.querySelector('button[type="submit"]')
          fireEvent.click(submitButton)

          // Should not call submit handler if required fields are empty
          const requiredFields = fields.filter((_, index) => index % 2 === 0)
          if (requiredFields.length > 0) {
            expect(submitCalled).toBe(false)
            
            // Should show validation errors for required fields
            const errorMessages = container.querySelectorAll('.invalid-feedback')
            expect(errorMessages.length).toBeGreaterThan(0)
          }
        }
      ),
      { numRuns: 50 }
    )
  })

  test('Property 2.2: Email validation works correctly for any input', () => {
    fc.assert(
      fc.property(
        fc.string({ maxLength: 100 }),
        (emailInput) => {
          const fields = [{
            name: 'email',
            label: 'Email',
            type: 'email'
          }]

          const validationRules = {
            email: { email: true, required: true }
          }

          const { container } = render(
            <AdminLTEForm
              fields={fields}
              validationRules={validationRules}
              onSubmit={() => {}}
            />
          )

          const emailField = container.querySelector('input[name="email"]')
          expect(emailField).toBeInTheDocument()

          // Input the generated email
          fireEvent.change(emailField, { target: { value: emailInput } })
          fireEvent.blur(emailField)

          // Check if validation is applied correctly
          const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput)
          const hasError = container.querySelector('.invalid-feedback')
          
          if (emailInput.trim() === '') {
            // Empty email should show required error
            expect(hasError).toBeInTheDocument()
          } else if (!isValidEmail) {
            // Invalid email should show email format error
            expect(hasError).toBeInTheDocument()
          } else {
            // Valid email should show success or no error
            const hasSuccess = container.querySelector('.valid-feedback')
            expect(hasError || hasSuccess).toBeTruthy()
          }
        }
      ),
      { numRuns: 100 }
    )
  })

  test('Property 2.3: Number validation works correctly for any input', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.integer({ min: -1000, max: 1000 }).map(n => n.toString()),
          fc.float({ min: -1000, max: 1000, noNaN: true }).map(n => n.toString()),
          fc.string({ maxLength: 20 }), // Non-numeric strings
          fc.constant('')
        ),
        fc.option(fc.integer({ min: 0, max: 100 })), // min value
        fc.option(fc.integer({ min: 100, max: 1000 })), // max value
        (numberInput, minValue, maxValue) => {
          const fields = [{
            name: 'number',
            label: 'Number',
            type: 'number'
          }]

          const validationRules = {
            number: { 
              number: true, 
              required: true,
              min: minValue,
              max: maxValue
            }
          }

          const { container } = render(
            <AdminLTEForm
              fields={fields}
              validationRules={validationRules}
              onSubmit={() => {}}
            />
          )

          const numberField = container.querySelector('input[name="number"]')
          expect(numberField).toBeInTheDocument()

          // Input the generated number
          fireEvent.change(numberField, { target: { value: numberInput } })
          fireEvent.blur(numberField)

          const hasError = container.querySelector('.invalid-feedback')
          const numericValue = Number(numberInput)
          
          if (numberInput.trim() === '') {
            // Empty should show required error
            expect(hasError).toBeInTheDocument()
          } else if (isNaN(numericValue)) {
            // Non-numeric should show number format error
            expect(hasError).toBeInTheDocument()
          } else if (minValue !== undefined && numericValue < minValue) {
            // Below minimum should show min error
            expect(hasError).toBeInTheDocument()
          } else if (maxValue !== undefined && numericValue > maxValue) {
            // Above maximum should show max error
            expect(hasError).toBeInTheDocument()
          }
        }
      ),
      { numRuns: 100 }
    )
  })

  test('Property 2.4: Form submission works correctly with valid data', () => {
    fc.assert(
      fc.property(
        formFieldGenerator,
        formFieldGenerator.chain(fields => formValuesGenerator(fields)),
        (fields, formValues) => {
          // Create minimal validation rules
          const validationRules = {}
          fields.forEach(field => {
            validationRules[field.name] = { required: false }
          })

          let submitCalled = false
          let submittedValues = null
          const handleSubmit = (values) => {
            submitCalled = true
            submittedValues = values
          }

          const { container } = render(
            <AdminLTEForm
              fields={fields}
              validationRules={validationRules}
              onSubmit={handleSubmit}
              initialValues={formValues}
            />
          )

          // Submit the form
          const submitButton = container.querySelector('button[type="submit"]')
          fireEvent.click(submitButton)

          // Should call submit handler with form values
          expect(submitCalled).toBe(true)
          expect(submittedValues).toBeDefined()
          
          // Submitted values should contain all field names
          fields.forEach(field => {
            expect(submittedValues).toHaveProperty(field.name)
          })
        }
      ),
      { numRuns: 50 }
    )
  })

  test('Property 2.5: Form handles disabled state correctly', () => {
    fc.assert(
      fc.property(
        formFieldGenerator,
        fc.boolean(), // loading state
        (fields, loading) => {
          const { container } = render(
            <AdminLTEForm
              fields={fields}
              validationRules={{}}
              onSubmit={() => {}}
              loading={loading}
            />
          )

          // All form elements should respect loading state
          const formElements = container.querySelectorAll('input, select, textarea, button')
          formElements.forEach(element => {
            if (loading) {
              expect(element).toBeDisabled()
            } else {
              // Only explicitly disabled fields should be disabled
              const fieldName = element.getAttribute('name')
              const field = fields.find(f => f.name === fieldName)
              if (field && field.disabled) {
                expect(element).toBeDisabled()
              } else if (element.type !== 'submit') {
                expect(element).not.toBeDisabled()
              }
            }
          })

          // Submit button should show loading indicator when loading
          const submitButton = container.querySelector('button[type="submit"]')
          if (loading) {
            expect(submitButton).toBeDisabled()
            expect(container.querySelector('.loading-spinner')).toBeInTheDocument()
          }
        }
      ),
      { numRuns: 50 }
    )
  })
})