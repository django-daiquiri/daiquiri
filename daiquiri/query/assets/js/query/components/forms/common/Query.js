import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { get, isNil } from 'lodash'

import ReactCodeMirror from '@uiw/react-codemirror'
import { EditorView } from '@codemirror/view'
import { sql } from '@codemirror/lang-sql'

import { underlineRange } from '../../../utils/codemirror'

import Errors from './Errors'

const Query = ({ label, value, errors, setValue, editor }) => {

  useEffect(() => {
    const positions = JSON.parse(get(errors, 'positions') || '[]')
    const ranges = []
    positions.forEach(position => {
      ranges.push({ from: position[0], to: position[1]})
    })
    underlineRange(editor.current.view, ranges)
  }, [errors])

  return (
    <div className="mb-2">
      <label htmlFor="query" className="form-label">{label}</label>
      <ReactCodeMirror
        id="query"
        ref={editor}
        className={classNames('form-control codemirror', {'is-invalid': errors})}
        value={value}
        onChange={setValue}
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

Query.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  errors: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  setValue: PropTypes.func.isRequired,
  editor: PropTypes.object,
}

export default Query
