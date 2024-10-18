import React, { useCallback } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { useDropzone } from 'react-dropzone'
import { isNil } from 'lodash'

import { bytes2human } from 'daiquiri/core/assets/js/utils/bytes'

import Errors from './Errors'

const File = ({ label, value, errors, onChange }) => {
  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles.length == 1) {
      onChange(acceptedFiles[0])
    }
  }, [value])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })

  return (
    <div className="mb-3">
      <label htmlFor="run-id" className="form-label">{label}</label>

      <div className={classNames('file-control', {'is-invalid': errors})}>
        <div {...getRootProps({className: 'dropzone'})}>
          <input {...getInputProps()} />
          {
            isDragActive ? (
              <div className="text-muted">
                <span>{gettext('Drop the file here ...')}</span>
              </div>
            ) : (
              <div>
              {
                isNil(value) ? <span>{gettext('No file selected.')}</span>
                             : <span>{value.name} ({bytes2human(value.size)})</span>
              }
              </div>
            )
          }
        </div>
        <small className="form-text text-muted">
          {gettext('Drag and drop file or click to open a file browser.')}
        </small>
      </div>

      <Errors errors={errors} />
    </div>
  )
}

File.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.object,
  errors: PropTypes.array,
  onChange: PropTypes.func.isRequired,
}

export default File
