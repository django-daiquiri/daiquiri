import React from 'react'
import PropTypes from 'prop-types'

import { useDataLinksQuery, useNoteQuery } from '../../hooks/queries'

import TableModalDatalinks from './TableModalDatalinks'
import TableModalNavigation from './TableModalNavigation'

const TableModal = ({ modalRef, modalValues, onNavigation, onClose }) => {

  const { data: dataLinks } = useDataLinksQuery(modalValues.dataLinkId)
  const { data: note } = useNoteQuery(modalValues.noteUrl)

  return (
    <div ref={modalRef} className="dq-table-modal modal" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        {
          modalValues && (
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">{modalValues.title}</h5>
                <button type="button" className="btn-close" onClick={onClose}></button>
              </div>
              <div className="modal-body">
                <TableModalNavigation values={modalValues} onClick={onNavigation} />
                {
                  dataLinks && <TableModalDatalinks dataLinks={dataLinks} />
                }
                {
                  note && <pre>{note}</pre>
                }
                {
                  modalValues.imageSrc && (
                    <img className="d-block mx-auto" src={modalValues.imageSrc} alt={modalValues.title} />
                  )
                }
              </div>
            </div>
          )
        }
      </div>
    </div>
  )
}

TableModal.propTypes = {
  modalRef: PropTypes.object,
  modalValues: PropTypes.object,
  onNavigation: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired
}

export default TableModal
