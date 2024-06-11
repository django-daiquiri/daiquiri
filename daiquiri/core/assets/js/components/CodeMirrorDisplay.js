import React from 'react'
import PropTypes from 'prop-types'

import ReactCodeMirror from '@uiw/react-codemirror'
import { EditorView } from '@codemirror/view'
import { sql } from '@codemirror/lang-sql'

const CodeMirrorDisplay = ({ value }) => {
  // check https://www.npmjs.com/package/@uiw/react-codemirror#Props for props

  return (
    <ReactCodeMirror
      className="codemirror"
      value={value}
      extensions={[sql(), EditorView.lineWrapping]}
      editable={false}
      basicSetup={{
        lineNumbers: false,
        foldGutter: false,
        highlightActiveLine: false,
      }}
    />
  )
}

CodeMirrorDisplay.propTypes = {
  value: PropTypes.string
}

export default CodeMirrorDisplay
