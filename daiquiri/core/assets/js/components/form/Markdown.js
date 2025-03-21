import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { uniqueId } from 'lodash'

import ReactCodeMirror from '@uiw/react-codemirror'
import { EditorView } from '@codemirror/view'
import { markdown } from '@codemirror/lang-markdown'

import Errors from './Errors'

const Markdown = ({ label, help, value, errors, onChange }) => {
  const id = uniqueId('input-')

  return (
    <div className="mb-3">
      <label htmlFor={id} className="form-label">{label}</label>
      <ReactCodeMirror
        id={id}
        className={classNames('form-control codemirror', {'is-invalid': errors})}
        value={value}
        onChange={onChange}
        extensions={[markdown(), EditorView.lineWrapping]}
        basicSetup={{
          foldGutter: false,
          highlightActiveLine: false,
          highlightActiveLineGutter: false,
        }}
      />
      <Errors errors={errors} />
      {
        help && <div className="form-text">{help}</div>
      }
    </div>
  )
}

Markdown.propTypes = {
  label: PropTypes.string.isRequired,
  help: PropTypes.string.isRequired,
  value: PropTypes.string,
  errors: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  onChange: PropTypes.func.isRequired
}

export default Markdown
