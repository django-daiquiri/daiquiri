import { baseUrl } from './meta'

export const getBasename = (string) => string.replace(/^.*[\\/]/, '')

export const getFileUrl = (column, value) => `${baseUrl}/files/${value}`

export const getLinkUrl = (column, value) => value

export const getReferenceUrl = (column, value) => `${baseUrl}/serve/references/${column.name}/${value}`

export const isRefColumn = (column) => column.ucd && column.ucd.includes('meta.ref')

export const isLinkColumn = (column) => column.ucd && column.ucd.includes('meta.ref.url')

export const isDataLinkColumn = (column) => column.ucd && column.ucd.includes('meta.ref.id')

export const isImageColumn = (column) => column.ucd && column.ucd.includes('meta.image')

export const isNoteColumn = (column) => column.ucd && column.ucd.includes('meta.note')

export const isFileColumn = (column) => column.ucd && column.ucd.includes('meta.file')

export const isModalColumn = (column) => isDataLinkColumn(column) || isImageColumn(column) || isNoteColumn(column)