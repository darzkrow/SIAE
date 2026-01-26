import React, { useState, useEffect } from 'react'
import { AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react'

/**
 * AdminLTE3 Form Component
 * Provides form controls with AdminLTE3 styling and validation
 */
const AdminLTEForm = ({
  fields = [],
  initialValues = {},
  validationRules = {},
  onSubmit = () => {},
  onCancel = null,
  submitText = 'Guardar',
  cancelText = 'Cancelar',
  loading = false,
  className = ''
}) => {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})
  const [showPasswords, setShowPasswords] = useState({})

  useEffect(() => {
    setValues(initialValues)
  }, [initialValues])

  const validateField = (name, value) => {
    const rules = validationRules[name]
    if (!rules) return null

    // Required validation
    if (rules.required && (!value || value.toString().trim() === '')) {
      return 'Este campo es requerido'
    }

    // Min length validation
    if (rules.minLength && value && value.toString().length < rules.minLength) {
      return `Debe tener al menos ${rules.minLength} caracteres`
    }

    // Max length validation
    if (rules.maxLength && value && value.toString().length > rules.maxLength) {
      return `No puede tener más de ${rules.maxLength} caracteres`
    }

    // Email validation
    if (rules.email && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(value)) {
        return 'Ingrese un email válido'
      }
    }

    // Number validation
    if (rules.number && value && isNaN(Number(value))) {
      return 'Debe ser un número válido'
    }

    // Min value validation
    if (rules.min !== undefined && value && Number(value) < rules.min) {
      return `El valor mínimo es ${rules.min}`
    }

    // Max value validation
    if (rules.max !== undefined && value && Number(value) > rules.max) {
      return `El valor máximo es ${rules.max}`
    }

    // Pattern validation
    if (rules.pattern && value && !rules.pattern.test(value)) {
      return rules.patternMessage || 'Formato inválido'
    }

    // Custom validation
    if (rules.custom && value) {
      return rules.custom(value, values)
    }

    return null
  }

  const handleChange = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }))
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }))
    }
  }

  const handleBlur = (name) => {
    setTouched(prev => ({ ...prev, [name]: true }))
    const error = validateField(name, values[name])
    setErrors(prev => ({ ...prev, [name]: error }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Validate all fields
    const newErrors = {}
    let hasErrors = false

    fields.forEach(field => {
      const error = validateField(field.name, values[field.name])
      if (error) {
        newErrors[field.name] = error
        hasErrors = true
      }
    })

    setErrors(newErrors)
    setTouched(fields.reduce((acc, field) => ({ ...acc, [field.name]: true }), {}))

    if (!hasErrors) {
      onSubmit(values)
    }
  }

  const togglePasswordVisibility = (fieldName) => {
    setShowPasswords(prev => ({
      ...prev,
      [fieldName]: !prev[fieldName]
    }))
  }

  const renderField = (field) => {
    const value = values[field.name] || ''
    const error = errors[field.name]
    const isTouched = touched[field.name]
    const hasError = error && isTouched
    const isValid = !error && isTouched && value

    const baseClasses = `form-control ${hasError ? 'is-invalid' : ''} ${isValid ? 'is-valid' : ''}`

    switch (field.type) {
      case 'text':
      case 'email':
      case 'number':
        return (
          <div key={field.name} className="form-group">
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {validationRules[field.name]?.required && <span className="text-danger">*</span>}
            </label>
            <input
              type={field.type}
              id={field.name}
              name={field.name}
              className={baseClasses}
              value={value}
              placeholder={field.placeholder}
              disabled={field.disabled || loading}
              onChange={(e) => handleChange(field.name, e.target.value)}
              onBlur={() => handleBlur(field.name)}
            />
            {hasError && (
              <div className="invalid-feedback d-flex align-items-center">
                <AlertCircle size={16} className="mr-1" />
                {error}
              </div>
            )}
            {isValid && (
              <div className="valid-feedback d-flex align-items-center">
                <CheckCircle size={16} className="mr-1" />
                Campo válido
              </div>
            )}
            {field.help && (
              <small className="form-text text-muted">{field.help}</small>
            )}
          </div>
        )

      case 'password':
        return (
          <div key={field.name} className="form-group">
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {validationRules[field.name]?.required && <span className="text-danger">*</span>}
            </label>
            <div className="input-group">
              <input
                type={showPasswords[field.name] ? 'text' : 'password'}
                id={field.name}
                name={field.name}
                className={baseClasses}
                value={value}
                placeholder={field.placeholder}
                disabled={field.disabled || loading}
                onChange={(e) => handleChange(field.name, e.target.value)}
                onBlur={() => handleBlur(field.name)}
              />
              <div className="input-group-append">
                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={() => togglePasswordVisibility(field.name)}
                >
                  {showPasswords[field.name] ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            {hasError && (
              <div className="invalid-feedback d-flex align-items-center">
                <AlertCircle size={16} className="mr-1" />
                {error}
              </div>
            )}
            {field.help && (
              <small className="form-text text-muted">{field.help}</small>
            )}
          </div>
        )

      case 'textarea':
        return (
          <div key={field.name} className="form-group">
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {validationRules[field.name]?.required && <span className="text-danger">*</span>}
            </label>
            <textarea
              id={field.name}
              name={field.name}
              className={baseClasses}
              value={value}
              placeholder={field.placeholder}
              disabled={field.disabled || loading}
              rows={field.rows || 3}
              onChange={(e) => handleChange(field.name, e.target.value)}
              onBlur={() => handleBlur(field.name)}
            />
            {hasError && (
              <div className="invalid-feedback d-flex align-items-center">
                <AlertCircle size={16} className="mr-1" />
                {error}
              </div>
            )}
            {field.help && (
              <small className="form-text text-muted">{field.help}</small>
            )}
          </div>
        )

      case 'select':
        return (
          <div key={field.name} className="form-group">
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {validationRules[field.name]?.required && <span className="text-danger">*</span>}
            </label>
            <select
              id={field.name}
              name={field.name}
              className={baseClasses}
              value={value}
              disabled={field.disabled || loading}
              onChange={(e) => handleChange(field.name, e.target.value)}
              onBlur={() => handleBlur(field.name)}
            >
              <option value="">Seleccionar...</option>
              {field.options?.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {hasError && (
              <div className="invalid-feedback d-flex align-items-center">
                <AlertCircle size={16} className="mr-1" />
                {error}
              </div>
            )}
            {field.help && (
              <small className="form-text text-muted">{field.help}</small>
            )}
          </div>
        )

      case 'checkbox':
        return (
          <div key={field.name} className="form-group">
            <div className="form-check">
              <input
                type="checkbox"
                id={field.name}
                name={field.name}
                className={`form-check-input ${hasError ? 'is-invalid' : ''}`}
                checked={!!value}
                disabled={field.disabled || loading}
                onChange={(e) => handleChange(field.name, e.target.checked)}
                onBlur={() => handleBlur(field.name)}
              />
              <label htmlFor={field.name} className="form-check-label">
                {field.label}
                {validationRules[field.name]?.required && <span className="text-danger">*</span>}
              </label>
              {hasError && (
                <div className="invalid-feedback d-flex align-items-center">
                  <AlertCircle size={16} className="mr-1" />
                  {error}
                </div>
              )}
              {field.help && (
                <small className="form-text text-muted">{field.help}</small>
              )}
            </div>
          </div>
        )

      case 'radio':
        return (
          <div key={field.name} className="form-group">
            <label className="form-label">
              {field.label}
              {validationRules[field.name]?.required && <span className="text-danger">*</span>}
            </label>
            {field.options?.map(option => (
              <div key={option.value} className="form-check">
                <input
                  type="radio"
                  id={`${field.name}_${option.value}`}
                  name={field.name}
                  className={`form-check-input ${hasError ? 'is-invalid' : ''}`}
                  value={option.value}
                  checked={value === option.value}
                  disabled={field.disabled || loading}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  onBlur={() => handleBlur(field.name)}
                />
                <label htmlFor={`${field.name}_${option.value}`} className="form-check-label">
                  {option.label}
                </label>
              </div>
            ))}
            {hasError && (
              <div className="invalid-feedback d-flex align-items-center">
                <AlertCircle size={16} className="mr-1" />
                {error}
              </div>
            )}
            {field.help && (
              <small className="form-text text-muted">{field.help}</small>
            )}
          </div>
        )

      case 'file':
        return (
          <div key={field.name} className="form-group">
            <label htmlFor={field.name} className="form-label">
              {field.label}
              {validationRules[field.name]?.required && <span className="text-danger">*</span>}
            </label>
            <input
              type="file"
              id={field.name}
              name={field.name}
              className={baseClasses}
              disabled={field.disabled || loading}
              accept={field.accept}
              multiple={field.multiple}
              onChange={(e) => handleChange(field.name, field.multiple ? e.target.files : e.target.files[0])}
              onBlur={() => handleBlur(field.name)}
            />
            {hasError && (
              <div className="invalid-feedback d-flex align-items-center">
                <AlertCircle size={16} className="mr-1" />
                {error}
              </div>
            )}
            {field.help && (
              <small className="form-text text-muted">{field.help}</small>
            )}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <form onSubmit={handleSubmit} className={className}>
      {fields.map(renderField)}
      
      <div className="form-group d-flex justify-content-end">
        {onCancel && (
          <button
            type="button"
            className="btn btn-secondary mr-2"
            onClick={onCancel}
            disabled={loading}
          >
            {cancelText}
          </button>
        )}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
        >
          {loading && <div className="loading-spinner mr-2"></div>}
          {submitText}
        </button>
      </div>
    </form>
  )
}

export default AdminLTEForm