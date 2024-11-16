import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isEmpty, upperFirst } from 'lodash'

import { baseUrl } from 'daiquiri/core/assets/js/utils/meta'

const TableModalDatalinks = ({ dataLinkId, dataLinks }) => {
  if (isEmpty(dataLinks)) {
    return (
      <p className="text-danger">
        {gettext('No data links were found for this ID.')}
      </p>
    )
  } else {
    const semanticsList = dataLinks.reduce((semanticsList, dataLink) => (
      semanticsList.includes(dataLink.semantics) ? semanticsList : [...semanticsList, dataLink.semantics]
    ), [])

    return (
      <>
        {
          semanticsList.map(semantics => {
            const label = semantics.split('#')[1]

            return (
              <div key={semantics} className={classNames({'mt-2': semantics != semanticsList[0]})}>
                <strong>{label ? upperFirst(label) : semantics}</strong>

                {
                  semantics == '#preview' ? (
                    dataLinks.filter(dataLink => dataLink.semantics == semantics).map((dataLink, dataLinkIndex) => (
                      <img key={dataLinkIndex} src={dataLink.access_url} className="d-block img-fluid" alt={dataLink.description} />
                    ))
                  ) : (
                    <ul className="list-unstyled">
                    {
                      dataLinks.filter(dataLink => dataLink.semantics == semantics).map((dataLink, dataLinkIndex) => (
                        <li key={dataLinkIndex} className="list-group-item">
                           <a href={dataLink.access_url} target="_blank" rel="noreferrer">{dataLink.description || dataLink.access_url}</a>
                        </li>
                      ))
                    }
                    </ul>
                  )
                }
              </div>
            )
          })
        }
        <p className="mt-2">
          <a href={`${baseUrl}/datalink/${dataLinkId}/`} target="_blank" rel="noreferrer">
            {interpolate(gettext('Datalink page'), [dataLinkId])}
          </a>
        </p>
      </>
    )
  }
}

TableModalDatalinks.propTypes = {
  dataLinkId: PropTypes.string,
  dataLinks: PropTypes.array
}

export default TableModalDatalinks
