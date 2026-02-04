import React, { useState, useEffect, useMemo } from 'react'
import { 
  ChevronUp, 
  ChevronDown, 
  Search, 
  Filter,
  Download,
  RefreshCw,
  MoreVertical,
  Edit,
  Trash2,
  Eye
} from 'lucide-react'

/**
 * AdminLTE3 Data Table Component
 * Provides a feature-rich data table with sorting, filtering, and pagination
 */
const AdminLTEDataTable = ({
  columns = [],
  data = [],
  pagination = { enabled: true, pageSize: 10 },
  filtering = { enabled: true },
  sorting = { enabled: true },
  bulkActions = [],
  onRowClick = null,
  onEdit = null,
  onDelete = null,
  onView = null,
  loading = false,
  className = ''
}) => {
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(pagination.pageSize || 10)
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })
  const [filterText, setFilterText] = useState('')
  const [selectedRows, setSelectedRows] = useState(new Set())
  const [showFilters, setShowFilters] = useState(false)
  const [columnFilters, setColumnFilters] = useState({})

  // Filter data based on search text and column filters
  const filteredData = useMemo(() => {
    let filtered = data

    // Apply global search filter
    if (filterText && filtering.enabled) {
      filtered = filtered.filter(row =>
        columns.some(column => {
          const value = row[column.key]
          return value && value.toString().toLowerCase().includes(filterText.toLowerCase())
        })
      )
    }

    // Apply column-specific filters
    Object.entries(columnFilters).forEach(([columnKey, filterValue]) => {
      if (filterValue) {
        filtered = filtered.filter(row => {
          const value = row[columnKey]
          return value && value.toString().toLowerCase().includes(filterValue.toLowerCase())
        })
      }
    })

    return filtered
  }, [data, filterText, columnFilters, columns, filtering.enabled])

  // Sort filtered data
  const sortedData = useMemo(() => {
    if (!sortConfig.key || !sorting.enabled) return filteredData

    return [...filteredData].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1
      }
      return 0
    })
  }, [filteredData, sortConfig, sorting.enabled])

  // Paginate sorted data
  const paginatedData = useMemo(() => {
    if (!pagination.enabled) return sortedData

    const startIndex = (currentPage - 1) * pageSize
    return sortedData.slice(startIndex, startIndex + pageSize)
  }, [sortedData, currentPage, pageSize, pagination.enabled])

  // Calculate pagination info
  const totalPages = Math.ceil(sortedData.length / pageSize)
  const startRecord = (currentPage - 1) * pageSize + 1
  const endRecord = Math.min(currentPage * pageSize, sortedData.length)

  const handleSort = (columnKey) => {
    if (!sorting.enabled) return

    setSortConfig(prevConfig => ({
      key: columnKey,
      direction: prevConfig.key === columnKey && prevConfig.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedRows(new Set(paginatedData.map((_, index) => index)))
    } else {
      setSelectedRows(new Set())
    }
  }

  const handleSelectRow = (index, checked) => {
    const newSelected = new Set(selectedRows)
    if (checked) {
      newSelected.add(index)
    } else {
      newSelected.delete(index)
    }
    setSelectedRows(newSelected)
  }

  const handleColumnFilter = (columnKey, value) => {
    setColumnFilters(prev => ({
      ...prev,
      [columnKey]: value
    }))
  }

  const renderSortIcon = (columnKey) => {
    if (!sorting.enabled || sortConfig.key !== columnKey) {
      return <ChevronUp className="opacity-30" size={14} />
    }
    return sortConfig.direction === 'asc' 
      ? <ChevronUp size={14} />
      : <ChevronDown size={14} />
  }

  const renderCell = (row, column) => {
    if (column.renderer) {
      return column.renderer(row[column.key], row)
    }
    return row[column.key]
  }

  const renderActions = (row, index) => {
    const hasActions = onView || onEdit || onDelete
    if (!hasActions) return null

    return (
      <div className="dropdown">
        <button 
          className="btn btn-sm btn-outline-secondary dropdown-toggle"
          data-toggle="dropdown"
          aria-expanded="false"
        >
          <MoreVertical size={14} />
        </button>
        <div className="dropdown-menu">
          {onView && (
            <button 
              className="dropdown-item"
              onClick={() => onView(row, index)}
            >
              <Eye size={14} className="mr-2" />
              Ver
            </button>
          )}
          {onEdit && (
            <button 
              className="dropdown-item"
              onClick={() => onEdit(row, index)}
            >
              <Edit size={14} className="mr-2" />
              Editar
            </button>
          )}
          {onDelete && (
            <>
              <div className="dropdown-divider"></div>
              <button 
                className="dropdown-item text-danger"
                onClick={() => onDelete(row, index)}
              >
                <Trash2 size={14} className="mr-2" />
                Eliminar
              </button>
            </>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className={`card ${className}`}>
      <div className="card-header">
        <div className="row align-items-center">
          <div className="col-md-6">
            <h3 className="card-title mb-0">
              {sortedData.length} registros
              {selectedRows.size > 0 && ` (${selectedRows.size} seleccionados)`}
            </h3>
          </div>
          <div className="col-md-6">
            <div className="d-flex justify-content-end">
              {filtering.enabled && (
                <div className="input-group input-group-sm mr-2" style={{ width: '200px' }}>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Buscar..."
                    value={filterText}
                    onChange={(e) => setFilterText(e.target.value)}
                  />
                  <div className="input-group-append">
                    <span className="input-group-text">
                      <Search size={14} />
                    </span>
                  </div>
                </div>
              )}
              <button 
                className="btn btn-sm btn-outline-secondary mr-2"
                onClick={() => setShowFilters(!showFilters)}
                title="Filtros avanzados"
              >
                <Filter size={14} />
              </button>
              <button 
                className="btn btn-sm btn-outline-secondary mr-2"
                onClick={() => window.location.reload()}
                title="Actualizar"
              >
                <RefreshCw size={14} />
              </button>
              <button 
                className="btn btn-sm btn-outline-secondary"
                title="Exportar"
              >
                <Download size={14} />
              </button>
            </div>
          </div>
        </div>

        {showFilters && (
          <div className="row mt-3">
            {columns.filter(col => col.filterable).map(column => (
              <div key={column.key} className="col-md-3 mb-2">
                <input
                  type="text"
                  className="form-control form-control-sm"
                  placeholder={`Filtrar ${column.title}...`}
                  value={columnFilters[column.key] || ''}
                  onChange={(e) => handleColumnFilter(column.key, e.target.value)}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card-body p-0">
        {loading ? (
          <div className="text-center p-4">
            <div className="loading-spinner"></div>
            <p className="mt-2 text-muted">Cargando datos...</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table table-striped table-hover mb-0">
              <thead>
                <tr>
                  {bulkActions.length > 0 && (
                    <th style={{ width: '40px' }}>
                      <input
                        type="checkbox"
                        className="form-check-input"
                        checked={selectedRows.size === paginatedData.length && paginatedData.length > 0}
                        onChange={(e) => handleSelectAll(e.target.checked)}
                      />
                    </th>
                  )}
                  {columns.map(column => (
                    <th 
                      key={column.key}
                      className={sorting.enabled && column.sortable ? 'cursor-pointer user-select-none' : ''}
                      onClick={() => column.sortable && handleSort(column.key)}
                    >
                      <div className="d-flex align-items-center justify-content-between">
                        <span>{column.title}</span>
                        {column.sortable && renderSortIcon(column.key)}
                      </div>
                    </th>
                  ))}
                  {(onView || onEdit || onDelete) && (
                    <th style={{ width: '80px' }}>Acciones</th>
                  )}
                </tr>
              </thead>
              <tbody>
                {paginatedData.length === 0 ? (
                  <tr>
                    <td 
                      colSpan={columns.length + (bulkActions.length > 0 ? 1 : 0) + ((onView || onEdit || onDelete) ? 1 : 0)}
                      className="text-center p-4 text-muted"
                    >
                      No se encontraron registros
                    </td>
                  </tr>
                ) : (
                  paginatedData.map((row, index) => (
                    <tr 
                      key={index}
                      className={onRowClick ? 'cursor-pointer' : ''}
                      onClick={() => onRowClick && onRowClick(row, index)}
                    >
                      {bulkActions.length > 0 && (
                        <td>
                          <input
                            type="checkbox"
                            className="form-check-input"
                            checked={selectedRows.has(index)}
                            onChange={(e) => handleSelectRow(index, e.target.checked)}
                            onClick={(e) => e.stopPropagation()}
                          />
                        </td>
                      )}
                      {columns.map(column => (
                        <td key={column.key}>
                          {renderCell(row, column)}
                        </td>
                      ))}
                      {(onView || onEdit || onDelete) && (
                        <td onClick={(e) => e.stopPropagation()}>
                          {renderActions(row, index)}
                        </td>
                      )}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {pagination.enabled && totalPages > 1 && (
        <div className="card-footer">
          <div className="row align-items-center">
            <div className="col-md-6">
              <div className="d-flex align-items-center">
                <span className="text-muted mr-2">Mostrar</span>
                <select 
                  className="form-control form-control-sm"
                  style={{ width: 'auto' }}
                  value={pageSize}
                  onChange={(e) => {
                    setPageSize(Number(e.target.value))
                    setCurrentPage(1)
                  }}
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
                <span className="text-muted ml-2">
                  registros. Mostrando {startRecord} a {endRecord} de {sortedData.length}
                </span>
              </div>
            </div>
            <div className="col-md-6">
              <nav>
                <ul className="pagination pagination-sm justify-content-end mb-0">
                  <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                    <button 
                      className="page-link"
                      onClick={() => setCurrentPage(1)}
                      disabled={currentPage === 1}
                    >
                      Primero
                    </button>
                  </li>
                  <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                    <button 
                      className="page-link"
                      onClick={() => setCurrentPage(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      Anterior
                    </button>
                  </li>
                  
                  {/* Page numbers */}
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i
                    if (pageNum <= totalPages) {
                      return (
                        <li key={pageNum} className={`page-item ${currentPage === pageNum ? 'active' : ''}`}>
                          <button 
                            className="page-link"
                            onClick={() => setCurrentPage(pageNum)}
                          >
                            {pageNum}
                          </button>
                        </li>
                      )
                    }
                    return null
                  })}
                  
                  <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                    <button 
                      className="page-link"
                      onClick={() => setCurrentPage(currentPage + 1)}
                      disabled={currentPage === totalPages}
                    >
                      Siguiente
                    </button>
                  </li>
                  <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                    <button 
                      className="page-link"
                      onClick={() => setCurrentPage(totalPages)}
                      disabled={currentPage === totalPages}
                    >
                      Último
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminLTEDataTable