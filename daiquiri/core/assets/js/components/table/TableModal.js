import React from 'react'
import PropTypes from 'prop-types'

import { useDataLinksQuery, useNoteQuery } from '../../hooks/queries'

import TableModalDatalinks from './TableModalDatalinks'
import TableModalNavigation from './TableModalNavigation'

const TableModal = ({ modal, modalValues, onNavigation }) => {

  const { data: dataLinks } = useDataLinksQuery(modalValues.dataLinkId)
  const { data: note } = useNoteQuery(modalValues.noteUrl)

  return (
    <div ref={modal.ref} className="dq-table-modal modal" tabIndex="-1">
      <div className="modal-dialog modal-lg">
        {
          modalValues && (
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">{modalValues.title}</h5>
                <button type="button" className="btn-close" onClick={modal.hide}></button>
              </div>
              <div className="modal-body">
                <TableModalNavigation values={modalValues} onClick={onNavigation} />
                {
                  dataLinks && <TableModalDatalinks dataLinkId={modalValues.dataLinkId} dataLinks={dataLinks} />
                }
                {
                  note && (
                    <div>
                    <a href={modalValues.noteUrl}><span><i class="bi bi-download"></i>&nbsp;Download</span></a>
                    <pre>{note}</pre>
                    </div>
                  )
                }
                {
                  modalValues.imageSrc && (
                    <div>
                    <a href={modalValues.imageSrc}><span><i class="bi bi-download"></i>&nbsp;Download</span></a>
                    <img className="d-block mx-auto" src={modalValues.imageSrc} alt={modalValues.title} />
                    </div>
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
  modal: PropTypes.object,
  modalValues: PropTypes.object,
  onNavigation: PropTypes.func.isRequired,
}

export default TableModal
