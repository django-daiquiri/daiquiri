import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import ReactCodeMirror from '@uiw/react-codemirror'
import { EditorView } from '@codemirror/view'
import { sql } from '@codemirror/lang-sql'

import Errors from './Errors'

const Query = ({ label, value, errors, setValue, editor }) => {
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
      <Errors errors={errors} />
    </div>
  )
}

Query.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  errors: PropTypes.array,
  setValue: PropTypes.func.isRequired,
  editor: PropTypes.object,
}

export default Query
