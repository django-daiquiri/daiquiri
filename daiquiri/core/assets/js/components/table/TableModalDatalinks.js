import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { upperFirst } from 'lodash'

const TableModalDatalinks = ({ dataLinks }) => {
  const semanticsList = dataLinks.reduce((semanticsList, dataLink) => (
    semanticsList.includes(dataLink.semantics) ? semanticsList : [...semanticsList, dataLink.semantics]
  ), []).sort()

  return (
    <>
      {
        semanticsList.map(semantics => {
          const label = semantics.split('#')[1]

          return (
            <div key={semantics} className={classNames({'mt-2': semantics != semanticsList[0]})}>
              <strong>{label ? upperFirst(label) : semantics}</strong>
              <ul className="list-unstyled">
              {
                dataLinks.filter(dataLink => dataLink.semantics == semantics).map((dataLink, dataLinkIndex) => (
                  <li key={dataLinkIndex} className="list-group-item">
                     <a href={dataLink.access_url} target="_blank" rel="noreferrer">{dataLink.description || dataLink.access_url}</a>
                  </li>
                ))
              }
              </ul>
            </div>
          )
        })
      }
    </>
  )
}

TableModalDatalinks.propTypes = {
  dataLinks: PropTypes.array
}

export default TableModalDatalinks
