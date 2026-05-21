import React, { useState, useRef } from 'react'
import { useUserExamplesQuery } from 'daiquiri/query/assets/js/hooks/queries'

import Sql from 'daiquiri/core/assets/js/components/form/Sql'

const CodeBlock = ({ queryString }) => {
  const [copied, setCopied] = useState(false)
  const dummyEditorRef = useRef()

  const triggerSuccess = () => {
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const fallbackCopy = (text) => {
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.opacity = '0'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()

    try {
      document.execCommand('copy')
      triggerSuccess()
    } catch (err) {
      console.error('Could not copy text: ', err)
    }

    document.body.removeChild(textArea)
  }

  const handleCopy = () => {
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(queryString)
        .then(triggerSuccess)
        .catch(() => fallbackCopy(queryString))
    } else {
      fallbackCopy(queryString)
    }
  }

  return (
    <div className="position-relative code-scroll-container">
      <div className="position-absolute top-0 end-0 p-2 z-3">
        <button
          aria-label="Copy query"
          className="btn btn-link p-1 text-muted btn-copy-overlay"
          onClick={handleCopy}
          type="button"
        >
          <i className={`bi ${copied ? 'bi-check-lg text-success' : 'bi-clipboard'}`} />
        </button>
      </div>

      <Sql
        value={queryString}
        editorRef={dummyEditorRef}
        height="auto"
        editable={false}
        readOnly={true}
        basicSetup={{
          lineNumbers: false,
          foldGutter: false,
          highlightActiveLine: false,
          highlightActiveLineGutter: false,
        }}
      />
    </div>
  )
}

const Examples = () => {
  const { data, isLoading, error } = useUserExamplesQuery()

  if (isLoading) {
    return <div className="text-muted">Loading examples...</div>
  }

  if (error) {
    return <div className="alert alert-danger">Error loading examples</div>
  }

  const rows = data ?? []

  return (
    <div>
      <h1 className="mb-4">Query examples</h1>

      {rows.length === 0 ? (
        <div className="text-muted">
          No examples found in the database
        </div>
      ) : (
        rows.map((example) => (
          <div key={example.id} className="border rounded p-3 mb-3">
            <div className="d-flex justify-content-between mb-2">
              <strong>{example.name}</strong>
              <span className="badge badge-secondary text-dark text-uppercase">
                {example.query_language}
              </span>
            </div>

            <div className="text-muted mb-2">
              {example.description}
            </div>

            <CodeBlock 
              queryString={example.query_string} 
            />
          </div>
        ))
      )}
    </div>
  )
}

export default Examples