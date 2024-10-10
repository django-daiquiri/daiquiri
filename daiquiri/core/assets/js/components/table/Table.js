import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

import { useModal } from 'daiquiri/core/assets/js/hooks/modal'

import { getFileUrl, isDataLinkColumn, isImageColumn, isNoteColumn, isModalColumn } from '../../utils/table.js'

import TableFooter from './TableFooter'
import TableHeader from './TableHeader'
import TableModal from './TableModal'
import TablePane from './TablePane'

const Table = ({ columns, rows, pageSizes, params, setParams }) => {
  const show = !(isEmpty(columns) || isEmpty(rows))
  const pageCount = Math.ceil(rows.count / params.page_size)

  const [modalRef, showModal, hideModal]  = useModal()
  const [modalValues, setModalValues] = useState({})
  const [active, setActive] = useState({})

  useEffect(() => {
    if (modalRef.current && modalRef.current.classList.contains('show') && modalValues.page == params.page) {
      // update the modal if (a) it is shown and (b) if we are not currently changing pages
      updateModal(active)
    }
  }, [active])

  useEffect(() => {
    if (modalRef.current && modalRef.current.classList.contains('show')) {
      // always update the modal if the rows change
      updateModal(active)
    }
  }, [rows])

  const updateModal = ({ rowIndex, columnIndex }) => {
    const column = columns[columnIndex]
    const value = rows.results[rowIndex][columnIndex]

    if (isModalColumn(column)) {
      setModalValues({
        title: value,
        dataLinkId: isDataLinkColumn(column) ? value : null,
        noteUrl: isNoteColumn(column) ? getFileUrl(column, value) : null,
        imageSrc: isImageColumn(column) ? getFileUrl(column, value) : null,
        page: params.page,
        up: (rowIndex > 0 || params.page > 1),
        down: (rowIndex < params.page_size - 1 || params.page < pageCount),
        right: columns.filter((c, i) => i > columnIndex).some(isModalColumn),
        left: columns.filter((c, i) => i < columnIndex).some(isModalColumn),
      })
    }
  }

  const handleClick = (rowIndex, columnIndex) => {
    setActive({ rowIndex, columnIndex })

    console.log(isModalColumn(columns[columnIndex]))

    if (isModalColumn(columns[columnIndex])) {
      updateModal({ rowIndex, columnIndex })
      showModal()
    }
  }

  const handleNavigation = (direction) => {
    if (direction == 'up') {
      if (active.rowIndex > 0) {
        setActive({ ...active, rowIndex: active.rowIndex - 1 })
      } else if (params.page > 1) {
        setActive({ ...active, rowIndex: params.page_size - 1 })
        setParams({ ...params, page: params.page - 1 })
      }
    } else if (direction == 'down') {
      if (active.rowIndex < params.page_size - 1) {
        setActive({ ...active, rowIndex: active.rowIndex + 1 })
      } else if (params.page < pageCount) {
        setActive({ ...active, rowIndex: 0 })
        setParams({ ...params, page: params.page + 1 })
      }
    } else if (direction == 'right') {
      const columnIndex = columns.findIndex((c, i) => isModalColumn(c) && i > active.columnIndex)
      if (columnIndex > 0) {
        setActive({ ...active, columnIndex})
      }
    } else if (direction == 'left') {
      const columnIndex = columns.findIndex((c, i) => isModalColumn(c) && i < active.columnIndex)
      if (columnIndex > 0) {
        setActive({ ...active, columnIndex})
      }
    }
  }

  return show && (
    <div className="dq-table mb-3">
      <TableHeader
        pageCount={pageCount}
        params={params}
        setParams={setParams}
      />
      <TablePane
        columns={columns}
        rows={rows}
        params={params}
        active={active}
        setParams={setParams}
        onClick={handleClick}
      />
      <TableFooter
        rowCount={rows.count}
        pageCount={pageCount}
        pageSizes={pageSizes}
        params={params}
        setParams={setParams}
      />
      <TableModal
        modalRef={modalRef}
        modalValues={modalValues}
        onNavigation={handleNavigation}
        onClose={hideModal}
      />
    </div>
  )
}

Table.defaultProps = {
  columns: [],
  rows: {},
  pageSizes: [10, 20, 100]
}

Table.propTypes = {
  columns: PropTypes.array,
  rows: PropTypes.object,
  pageSizes: PropTypes.array,
  params: PropTypes.object.isRequired,
  setParams: PropTypes.func.isRequired
}

export default Table
