import { isString } from 'lodash'
import { baseUrl } from './meta'

import { useServeParams } from 'daiquiri/serve/assets/js/hooks/params'

export const getBasename = (string) => {
  return isString(string) ? string.replace(/^.*[\\/]/, '') : string
}

export const getFileUrl = (column, value) => `${baseUrl}/files/${value}`

export const getLinkUrl = (column, value) => value

export const getReferenceUrl = (column, value) => {
  const params = useServeParams()
  const queryParameters = new URLSearchParams(params).toString()
  return `${baseUrl}/serve/references/${column.name}/${value}?${queryParameters}`
}

export const isRefColumn = (column) => column.ucd && column.ucd.includes('meta.ref')

export const isLinkColumn = (column) => column.ucd && column.ucd.includes('meta.ref.url')

export const isDataLinkColumn = (column) => column.ucd && column.ucd.includes('meta.ref.id')

export const isImageColumn = (column) => column.ucd && column.ucd.includes('meta.image')

export const isNoteColumn = (column) => column.ucd && column.ucd.includes('meta.note')

export const isFileColumn = (column) => column.ucd && column.ucd.includes('meta.file')

export const isModalColumn = (column) => (column) && (
  isDataLinkColumn(column) ||
  (isImageColumn(column) && isRefColumn(column)) ||
  (isNoteColumn(column) && isRefColumn(column))
)
