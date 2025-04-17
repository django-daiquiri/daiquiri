import React from 'react'
import PropTypes from 'prop-types'
import { isEmpty } from 'lodash'

import { baseUrl } from 'daiquiri/core/assets/js/utils/meta'

const TableModalDatalinks = ({ dataLinkId, dataLinks }) => {
  if (isEmpty(dataLinks)) {
    return (
      <p className="text-danger">
        {gettext('No data links were found for this ID.')}
      </p>
    )
  } else {

    const dlPreview = dataLinks.filter(dataLink => dataLink.semantics == '#preview')
    const dlThis = dataLinks.filter(dataLink => dataLink.semantics == '#this')
    const dlPreviewImages = dataLinks.filter(dataLink => dataLink.semantics == '#preview-image' || dataLink.semantics == '#preview-plot')

    return (
      <div>
        <ul className="list-unstyled">
          {dlPreview.map((dataLink, index) => (
            <li className="mb-1" key={index}>
              <a className="btn btn-primary btn-sm" href={dataLink.access_url} target="_blank" rel="noreferrer" data-bs-toggle="tooltip" title="Open viewer">
                <i className="bi bi-eye"></i>
              </a>
              &nbsp;&nbsp;{dataLink.description}
            </li>
          ))}
        </ul>
        <ul className="list-unstyled">
          {dlThis.map((dataLink, index) => (
            <li className="mb-1" key={index}>
              <a className="btn btn-primary btn-sm" href={dataLink.access_url} data-bs-toggle="tooltip" title="Download file">
                <i className="bi bi-download"></i>
              </a>
              &nbsp;&nbsp;{dataLink.description}
            </li>
          ))}
        </ul>
        <ul className="list-unstyled">
          <li>
            <a className="btn btn-primary btn-sm" href={`${baseUrl}/datalink/${dataLinkId}/`} target="_blank" rel="noreferrer" data-bs-toggle="tooltip" title="Open DataLink viewer">
              <i className="bi bi-link-45deg"></i>
            </a>
            &nbsp;&nbsp;Show all Data Links
          </li>
        </ul>
        <hr></hr>
        {dlPreviewImages.map((dataLink, dataLinkIndex) => (
            <div key={dataLinkIndex}>
                <h5>{dataLink.description}</h5>
                <a href={dataLink.access_url}><span><i class="bi bi-download"></i>&nbsp;Download</span></a>
                <img src={dataLink.access_url} className="d-block img-fluid" alt='Image is missing, please contact the administrator.' />
                <hr className="mb-4"></hr>
            </div>
        ))}
      </div>
    )
  }
}

TableModalDatalinks.propTypes = {
  dataLinkId: PropTypes.string,
  dataLinks: PropTypes.array
}

export default TableModalDatalinks

