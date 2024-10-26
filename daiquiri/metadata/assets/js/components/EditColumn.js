import React from 'react'
import PropTypes from 'prop-types'

import { useGroupsQuery } from 'daiquiri/auth/assets/js/hooks/queries'

import { useMetaQuery } from '../hooks/queries'

import Checkbox from 'daiquiri/core/assets/js/components/form/Checkbox'
import Input from 'daiquiri/core/assets/js/components/form/Input'
import Textarea from 'daiquiri/core/assets/js/components/form/Textarea'

const EditColumn = ({ values, errors, setValues, onSubmit }) => {
  const { data: meta } = useMetaQuery()
  const { data: groups } = useGroupsQuery()

  return values && meta && groups && (
    <div className="card">
      <div className="d-flex align-items-center card-header">
        <span className="me-auto">
          <strong>{gettext('Table')}</strong> {values.label}
        </span>

        <a className="btn btn-secondary btn-sm me-2" href={values.admin_url} target="_blank" rel="noreferrer">
          {gettext('Admin')}
        </a>
        <button className="btn btn-primary btn-sm" onClick={() => onSubmit('column', values)}>
          {gettext('Save')}
        </button>
      </div>
      <div className="card-body">
        <form onSubmit={(event => event.preventDefault())}>
          <Textarea
            label={meta.column.description.verbose_name}
            help={meta.column.description.help_text}
            value={values.description}
            errors={errors.description}
            onChange={(description) => setValues({ ...values, description })} />

          <div className="row">
            <div className="col-md-3">
              <Input
                label={meta.column.unit.verbose_name}
                help={meta.column.unit.help_text}
                value={values.unit}
                errors={errors.unit}
                onChange={(unit) => setValues({ ...values, unit })} />
            </div>
            <div className="col-md-3">
              <Input
                label={meta.column.utype.verbose_name}
                help={meta.column.utype.help_text}
                value={values.utype}
                errors={errors.utype}
                onChange={(utype) => setValues({ ...values, utype })} />
            </div>
            <div className="col-md-3">
              <Input
                label={meta.column.ucd.verbose_name}
                help={meta.column.ucd.help_text}
                value={values.ucd}
                errors={errors.ucd}
                onChange={(doi) => setValues({ ...values, doi })} />
            </div>
            <div className="col-md-3">
              <Input
                type="number"
                label={meta.column.order.verbose_name}
                value={values.order}
                errors={errors.order}
                onChange={(order) => setValues({ ...values, order })} />
            </div>
          </div>

          <Input
            label={meta.column.index_for.verbose_name}
            help={meta.column.index_for.help_text}
            value={values.index_for}
            errors={errors.index_for}
            onChange={(index_for) => setValues({ ...values, index_for })} />

          <Checkbox
            label={meta.column.principal.verbose_name}
            help={meta.column.principal.help_text}
            checked={values.principal}
            onChange={(checked) => setValues({ ...values, principal: checked})} />
          <Checkbox
            label={meta.column.indexed.verbose_name}
            help={meta.column.indexed.help_text}
            checked={values.indexed}
            onChange={(checked) => setValues({ ...values, indexed: checked})} />
          <Checkbox
            label={meta.column.std.verbose_name}
            help={meta.column.std.help_text}
            checked={values.std}
            onChange={(checked) => setValues({ ...values, std: checked})} />

        </form>
      </div>
      <div className="card-footer text-end">
        <button className="btn btn-primary btn-sm" onClick={() => onSubmit('column', values)}>
          {gettext('Save')}
        </button>
      </div>
    </div>
  )
}

EditColumn.propTypes = {
  values: PropTypes.object,
  errors: PropTypes.object,
  setValues: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired
}

export default EditColumn
