import React from 'react'
import PropTypes from 'prop-types'

import ReactCodeMirror from '@uiw/react-codemirror'
import { EditorView } from '@codemirror/view'
import { sql } from '@codemirror/lang-sql'

const Query = ({ query }) => {

  return (
    <ReactCodeMirror
      className="codemirror"
      value={query}
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

Query.propTypes = {
  query: PropTypes.string
}

export default Query
