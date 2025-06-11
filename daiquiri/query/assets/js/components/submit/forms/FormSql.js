import React, { useRef, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isNil } from 'lodash'

import { useLsState } from 'daiquiri/core/assets/js/hooks/ls'
import {
  useDropdownsQuery,
  useFormQuery,
  useQueryLanguagesQuery,
  useQueuesQuery,
} from 'daiquiri/query/assets/js/hooks/queries'
import { useStatusQuery } from 'daiquiri/query/assets/js/hooks/queries'
import { useSubmitJobMutation } from 'daiquiri/query/assets/js/hooks/mutations'
import { useUserFunctionsQuery } from 'daiquiri/metadata/assets/js/hooks/queries'

import Template from 'daiquiri/core/assets/js/components/Template'
import Tooltip from 'daiquiri/core/assets/js/components/Tooltip'

import Input from 'daiquiri/core/assets/js/components/form/Input'
import Sql from 'daiquiri/core/assets/js/components/form/Sql'
import Select from 'daiquiri/core/assets/js/components/form/Select'

import ColumnsDropdown from './dropdowns/ColumnsDropdown'
import ExamplesDropdown from './dropdowns/ExamplesDropdown'
import FunctionsDropdown from './dropdowns/FunctionsDropdown'
import SchemasDropdown from './dropdowns/SchemasDropdown'
import SimbadDropdown from './dropdowns/SimbadDropdown'
import VizierDropdown from './dropdowns/VizierDropdown'

const FormSql = ({ formKey, loadJob, query, queryLanguage }) => {
  const { data: form } = useFormQuery(formKey)
  const { data: status } = useStatusQuery()
  const { data: queues } = useQueuesQuery()
  const { data: queryLanguages } = useQueryLanguagesQuery()
  const { data: dropdowns } = useDropdownsQuery()
  const { data: functions } = useUserFunctionsQuery()
  const mutation = useSubmitJobMutation()

  const [values, setValues] = useState({
    query: query || '',
    query_language: queryLanguage || '',
    table_name: '',
    run_id: '',
    queue: '',
  })
  const [errors, setErrors] = useState({})

  const editorRef = useRef()

  const getDefaultQueryLanguage = () =>
    isNil(queryLanguages) ? '' : queryLanguages[0].id
  const getDefaultQueue = () => (isNil(queues) ? '' : queues[0].id)

  const [openDropdown, setOpenDropdown] = useLsState('query.openDropdown')

  const handleDrowpdown = (dropdownKey) => {
    setOpenDropdown(openDropdown == dropdownKey ? false : dropdownKey)
  }

  useEffect(() => {
    setValues({
      ...values,
      queue: values.queue || getDefaultQueue(),
      query_language: values.query_language || getDefaultQueryLanguage(),
    })
  }, [queues, queryLanguages])

  const handleSubmit = () => {
    mutation.mutate({ values, setErrors, loadJob })
  }

  const handleClear = () => {
    setValues({
      query: '',
      table_name: '',
      run_id: '',
      query_language: getDefaultQueryLanguage(),
      queue: getDefaultQueue(),
    })
  }

  const handleInsert = (type, item) => {
    let query_string = item.query_string

    if (isNil(query_string)) {
      const query_language = values.query_language || getDefaultQueryLanguage()
      const quote_char = queryLanguages.find(
        (ql) => ql.id == query_language
      ).quote_char

      query_string = item.query_strings
        .map((qs) => quote_char + qs + quote_char)
        .join('.')
    }

    // see https://codemirror.net/examples/change/
    editorRef.current.view.dispatch({
      // replace the current selection with the query_string
      changes: {
        from: editorRef.current.view.state.selection.main.from,
        to: editorRef.current.view.state.selection.main.to,
        insert: query_string,
      },
      // move the position of the cursor by the length of the pasted query_string
      selection: {
        anchor:
          editorRef.current.view.state.selection.main.from +
          query_string.length,
        head:
          editorRef.current.view.state.selection.main.from +
          query_string.length,
      },
    })

    // re-focus the editor
    editorRef.current.view.focus()
  }

  const handleReplace = (type, item) => {
    setValues({
      ...values,
      query: item.query_string,
      query_language: item.query_language,
    })
  }

  return (
    form && (
      <div className="query-form mb-4">
        <h2>{form.label}</h2>
        <Template template={form.template} />

        <div className="query-dropdowns">
          <div className="d-md-flex">
            {dropdowns &&
              dropdowns.map((dropdown, index) => (
                (dropdown.key !== 'functions' || (functions && functions.length > 0)) && (
                  <button
                    key={index}
                    type="button"
                    className={`btn btn-outline-form dropdown-toggle mb-2 ${
                      dropdown.classes || 'me-2'
                    }`}
                    onClick={() => handleDrowpdown(dropdown.key)}
                  >
                    {dropdown.label}
                  </button>
                )
              ))}
          </div>

          {openDropdown == 'schemas' && (
            <SchemasDropdown onDoubleClick={handleInsert} />
          )}
          {openDropdown == 'columns' && (
            <ColumnsDropdown onDoubleClick={handleInsert} />
          )}
          {openDropdown == 'functions' && (
            <FunctionsDropdown onDoubleClick={handleInsert} />
          )}
          {dropdowns &&
            dropdowns.map((dropdown, index) => {
              if (dropdown.key == 'simbad' && openDropdown == 'simbad') {
                return (
                  <SimbadDropdown
                    key={index}
                    options={dropdown.options}
                    onClick={handleInsert}
                  />
                )
              } else if (dropdown.key == 'vizier' && openDropdown == 'vizier') {
                return (
                  <VizierDropdown
                    key={index}
                    options={dropdown.options}
                    onClick={handleInsert}
                  />
                )
              }
            })}
          {openDropdown == 'examples' && (
            <ExamplesDropdown onDoubleClick={handleReplace} />
          )}
        </div>

        <div className="mt-2">
          <div className="mb-3">
            <Sql
              label={gettext('SQL query')}
              value={values.query}
              errors={errors.query}
              onChange={(query) => setValues({ ...values, query })}
              editorRef={editorRef}
            />
            {status && status.max_records && (
              <small className="form-text text-muted">
                {interpolate(gettext('Maximum rows per query: %s. '), [
                  status.max_records,
                ])}
                <Tooltip
                  tooltip={{
                    title: interpolate(
                      gettext(`The queries on our service are limited to %s rows. If you need more data,
                    consider refining your query or retrieving data in smaller batches.`),
                      [status.max_records]
                    ),
                    placement: 'right',
                  }}
                >
                  <i className="bi bi-info-circle-fill"></i>
                </Tooltip>
              </small>
            )}
          </div>

          <div className="row">
            <div className="col-md-4">
              <Input
                label={gettext('Table name')}
                value={values.table_name}
                errors={errors.table_name}
                onChange={(table_name) => setValues({ ...values, table_name })}
              />
            </div>
            <div className="col-md-2">
              <Input
                label={gettext('Run id')}
                value={values.run_id}
                errors={errors.run_id}
                onChange={(run_id) => setValues({ ...values, run_id })}
              />
            </div>
            <div className="col-md-3">
              <Select
                label={gettext('Query language')}
                value={values.query_language}
                errors={errors.query_language}
                options={queryLanguages}
                onChange={(query_language) =>
                  setValues({ ...values, query_language })
                }
              />
            </div>
            <div className="col-md-3">
              <Select
                label={gettext('Queue')}
                value={values.queue}
                errors={errors.queue}
                options={queues}
                onChange={(queue) => setValues({ ...values, queue })}
              />
            </div>
          </div>

          <div className="d-flex mt-2">
            <button
              type="button"
              className="btn btn-primary me-auto"
              onClick={() => handleSubmit()}
            >
              {form.submit || gettext('Submit new SQL query')}
            </button>
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={() => handleClear()}
            >
              {gettext('Clear input window')}
            </button>
          </div>
        </div>
      </div>
    )
  )
}

FormSql.propTypes = {
  formKey: PropTypes.string.isRequired,
  loadJob: PropTypes.func.isRequired,
  query: PropTypes.string,
  queryLanguage: PropTypes.string,
}

export default FormSql
