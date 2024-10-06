import React, { useRef, useState, useEffect } from 'react'
import PropTypes from 'prop-types'

import { get, isNil } from 'lodash'

import { useLsState } from 'daiquiri/core/assets/js/hooks/ls'

import Template from 'daiquiri/core/assets/js/components/Template'

import { useDropdownsQuery, useFormQuery, useQueryLanguagesQuery, useQueuesQuery } from '../../hooks/queries'
import { useSubmitJobMutation } from '../../hooks/mutations'

import Input from './common/Input'
import Query from './common/Query'
import Select from './common/Select'

import ColumnsDropdown from './dropdowns/ColumnsDropdown'
import ExamplesDropdown from './dropdowns/ExamplesDropdown'
import FunctionsDropdown from './dropdowns/FunctionsDropdown'
import SchemasDropdown from './dropdowns/SchemasDropdown'
import SimbadDropdown from './dropdowns/SimbadDropdown'
import VizierDropdown from './dropdowns/VizierDropdown'

const FormSql = ({ formKey, loadJob, query }) => {
  const { data: form } = useFormQuery(formKey)
  const { data: queues } = useQueuesQuery()
  const { data: queryLanguages } = useQueryLanguagesQuery()
  const { data: dropdowns } = useDropdownsQuery()
  const mutation = useSubmitJobMutation()

  const [values, setValues] = useState({
    query: query || '',
    table_name: '',
    run_id: '',
    query_language: '',
    queue: '',
  })
  const [errors, setErrors] = useState({})

  const editor = useRef()

  const getDefaultQueryLanguage = () => isNil(queryLanguages) ? '' : queryLanguages[0].id
  const getDefaultQueue = () => isNil(queues) ? '' : queues[0].id

  const [openDropdown, setOpenDropdown] = useLsState('query.openDropdown')

  const handleDrowpdown = (dropdownKey) => {
    setOpenDropdown(openDropdown == dropdownKey ? false : dropdownKey)
  }

  useEffect(() => {
    setValues({
      ...values,
      queue: values.queue || getDefaultQueue(),
      query_language: values.query_language || getDefaultQueryLanguage()})
  }, [queues, queryLanguages])

  const handleSubmit = () => {
    mutation.mutate({values, setErrors, loadJob})
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

  const handleInsert = (item) => {
    let query_string = item.query_string

    if (isNil(query_string)) {
      const query_language = values.query_language || getDefaultQueryLanguage()
      const quote_char = queryLanguages.find((ql) => ql.id == query_language).quote_char

      query_string = item.query_strings.map((qs) => (quote_char + qs + quote_char)).join('.')
    }

    // see https://codemirror.net/examples/change/
    editor.current.view.dispatch({
      changes: {
        from: editor.current.view.state.selection.main.from,
        to: editor.current.view.state.selection.main.to,
        insert: query_string
      }
    })
  }

  const handleReplace = (item) => {
    setValues({...values, query: item.query_string})
  }

  return form && (
    <div className="query-form mb-4">
      <h2>{form.label}</h2>
      <Template template={form.template} />

      <div className="query-dropdowns">
        <div className="d-md-flex">
          {
            dropdowns && dropdowns.map((dropdown, index) => (
              <button
                key={index}
                type="button"
                className={`btn btn-outline-form dropdown-toggle mb-2 ${dropdown.classes || 'me-2'}`}
                onClick={() => handleDrowpdown(dropdown.key)}
              >
                {dropdown.label}
              </button>
            ))
          }
        </div>

        {
          openDropdown == 'schemas' && <SchemasDropdown onPaste={handleInsert} />
        }
        {
          openDropdown == 'columns' && <ColumnsDropdown onPaste={handleInsert} />
        }
        {
          openDropdown == 'functions' && <FunctionsDropdown onPaste={handleInsert} />
        }
        {
          dropdowns && dropdowns.map((dropdown, index) => {
            if (dropdown.key == 'simbad' && openDropdown == 'simbad') {
              return <SimbadDropdown key={index} options={dropdown.options} onPaste={handleInsert} />
            } else if ((dropdown.key == 'vizier' && openDropdown == 'vizier')) {
              return <VizierDropdown key={index} options={dropdown.options} onPaste={handleInsert} />
            }
          })
        }
        {
          openDropdown == 'examples' && <ExamplesDropdown onPaste={handleReplace} />
        }

      </div>

      <div className="mt-2">
        <div className="mb-3">
          <Query
            label={gettext('SQL query')}
            value={values.query}
            errors={get(errors, 'query.messages') || errors.query}
            setValue={(query) => setValues({...values, query})}
            editor={editor}
          />
        </div>

        <div className="row">
          <div className="col-md-4">
            <Input
              label={gettext('Table name')}
              value={values.table_name}
              errors={errors.table_name}
              setValue={(table_name) => setValues({...values, table_name})}
            />
          </div>
          <div className="col-md-2">
            <Input
              label={gettext('Run id')}
              value={values.run_id}
              errors={errors.run_id}
              setValue={(run_id) => setValues({...values, run_id})}
            />
          </div>
          <div className="col-md-3">
            <Select
              label={gettext('Query language')}
              value={values.query_language}
              errors={errors.query_language}
              options={queryLanguages}
              setValue={(query_language) => setValues({...values, query_language})}
            />
          </div>
          <div className="col-md-3">
            <Select
              label={gettext('Queue')}
              value={values.queue}
              errors={errors.queue}
              options={queues}
              setValue={(queue) => setValues({...values, queue})}
            />
          </div>
        </div>

        <div className="d-flex mt-2">
          <button type="button" className="btn btn-primary me-auto" onClick={() => handleSubmit()}>
            {form.submit || gettext('Submit new SQL query')}
          </button>
          <button type="button" className="btn btn-outline-secondary" onClick={() => handleClear()}>
            {gettext('Clear input window')}
          </button>
        </div>
      </div>
    </div>
  )
}

FormSql.propTypes = {
  formKey: PropTypes.string.isRequired,
  loadJob: PropTypes.func.isRequired,
  query: PropTypes.string
}

export default FormSql
