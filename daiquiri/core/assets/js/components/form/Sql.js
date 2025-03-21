import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { get } from 'lodash'

import ReactCodeMirror from '@uiw/react-codemirror'
import { EditorView } from '@codemirror/view'
import { sql } from '@codemirror/lang-sql'

import { underlineRange } from 'daiquiri/core/assets/js/utils/codemirror'

import Errors from './Errors'

const Sql = ({ label, value, errors, onChange, editorRef }) => {

  useEffect(() => {
    const positions = JSON.parse(get(errors, 'positions') || '[]')
    const ranges = []
    positions.forEach(position => {
      ranges.push({ from: position[0], to: position[1]})
    })
    underlineRange(editorRef.current.view, ranges)
  }, [errors])

  return (
    <div className="mb-2">
      <label htmlFor="query" className="form-label">{label}</label>
      <ReactCodeMirror
        id="query"
        ref={editorRef}
        className={classNames('form-control codemirror', {'is-invalid': errors})}
        value={value}
        onChange={onChange}
        extensions={[sql(), EditorView.lineWrapping]}
        basicSetup={{
          foldGutter: false,
          highlightActiveLine: false,
          highlightActiveLineGutter: false,
        }}
      />
      <Errors errors={get(errors, 'messages') || errors} />
    </div>
  )
}

Sql.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  errors: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  onChange: PropTypes.func.isRequired,
  editorRef: PropTypes.object,
}

export default Sql
