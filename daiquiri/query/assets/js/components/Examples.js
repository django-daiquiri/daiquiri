import React, { useState } from 'react'
import { useQueryExamplesQuery } from 'daiquiri/query/assets/js/hooks/queries'

const CodeBlock = ({ queryString, highlightedQuery }) => {
  const [copied, setCopied] = useState(false)

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
    <div className="position-relative border rounded my-2" style={{ backgroundColor: '#f8f9fa' }}>
      <style>{`
        .daiquiri-codehilite-wrapper .codehilite,
        .daiquiri-codehilite-wrapper pre,
        .daiquiri-codehilite-wrapper code {
          background: transparent !important;
          border: none !important;
          margin: 0 !important;
          padding: 0 !important;
          box-shadow: none !important;
        }
      `}</style>

      <div className="position-absolute" style={{ top: 8, right: 8, zIndex: 10 }}>
        <button
          aria-label="Copy query"
          className="btn btn-link p-1"
          onClick={handleCopy}
          type="button"
        >
          <i className={`bi ${copied ? 'bi-check-lg' : 'bi-clipboard'}`} />
        </button>
      </div>

      <div 
        className="daiquiri-codehilite-wrapper p-3"
        style={{ 
          fontSize: '0.875rem',
          overflowX: 'auto',
          paddingRight: '45px',
          fontFamily: 'SFMono-Regular, Consolas, "Liberation Mono", Menlo, Courier, monospace',
          lineHeight: '1.5',
          color: '#212529'
        }}
        dangerouslySetInnerHTML={{ __html: highlightedQuery }}
      />
    </div>
  )
}

const Examples = () => {
  const { data, isLoading, error } = useQueryExamplesQuery()

  if (isLoading) {
    return <div className="text-muted">Loading examples...</div>
  }

  if (error) {
    return <div className="alert alert-danger">Error loading examples</div>
  }

  const rows = data?.results ?? []

  return (
    <div>
      <h1 className="mb-4">Query examples</h1>

      {rows.map((example) => (
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
            highlightedQuery={example.highlighted_query} 
          />
        </div>
      ))}
    </div>
  )
}

export default Examples