import React from 'react'
import PropTypes from 'prop-types'
import { isUndefined } from 'lodash'

import { useGroupsQuery } from 'daiquiri/auth/assets/js/hooks/queries'

import { useAccessLevelsQuery, useMetaQuery } from '../hooks/queries'

import Checkbox from 'daiquiri/core/assets/js/components/form/Checkbox'
import Input from 'daiquiri/core/assets/js/components/form/Input'
import Select from 'daiquiri/core/assets/js/components/form/Select'
import Textarea from 'daiquiri/core/assets/js/components/form/Textarea'

const EditColumn = ({ values, errors, setValues, onSubmit }) => {
  const { data: accessLevels } = useAccessLevelsQuery()
  const { data: meta } = useMetaQuery()
  const { data: groups } = useGroupsQuery()

  return values && meta && groups && (
    <div className="card">
      <div className="d-flex align-items-center card-header">
        <span className="me-auto">
          <strong>{gettext('Column')}</strong> {values.label}
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
                onChange={(ucd) => setValues({ ...values, ucd })} />
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

          {
            !isUndefined(values.access_level) && !isUndefined(values.metadata_access_level) && !isUndefined(values.groups) && <>
              <div className="row">
                <div className="col-md-6">
                  <Select
                    label={meta.column.access_level.verbose_name}
                    help={meta.column.access_level.help_text}
                    value={values.access_level}
                    options={accessLevels}
                    errors={errors.access_level}
                    onChange={(access_level) => setValues({ ...values, access_level })} />
                </div>
                <div className="col-md-6">
                  <Select
                    label={meta.column.metadata_access_level.verbose_name}
                    help={meta.column.metadata_access_level.help_text}
                    value={values.metadata_access_level}
                    options={accessLevels}
                    errors={errors.metadata_access_level}
                    onChange={(metadata_access_level) => setValues({ ...values, metadata_access_level })} />
                </div>
              </div>

              <div className="mb-3">
                <strong className="d-block mb-2">{gettext('Groups with access')}</strong>
                {
                  groups.map((group, groupIndex) => (
                    <Checkbox
                      key={groupIndex}
                      label={group.name}
                      checked={values.groups.includes(group.id)}
                      onChange={(checked) => setValues({ ...values, groups: checked ? (
                        [ ...values.groups, group.id]
                      ) : (
                        values.groups.filter(g => g.id !== group.id)
                      )})}
                    />
                  ))
                }
              </div>
            </>
          }

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
