import { isNil } from 'lodash'

const encodeParams = params => {
  if (isNil(params)) {
    return ''
  }

  return Object.entries(params).map(item => {
    const [key, value] = item

    if (Array.isArray(value)) {
      return value.map(v => {
        return encodeURIComponent(key) + '=' + encodeURIComponent(v)
      }).join('&')
    } else {
      return encodeURIComponent(key) + '=' + encodeURIComponent(value)
    }
  }).join('&')
}

export { encodeParams }