import { isNil } from 'lodash'

export const getColumnLabel = (columns, columnName) => {
  const column = columns.find(column => column.name == columnName) || {}
  const label = isNil(column.unit) ? column.name : `${column.name} [${column.unit}]`
  return label
}
