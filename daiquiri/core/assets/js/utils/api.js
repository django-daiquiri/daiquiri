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

const downloadFile = url => {
  const iframe = document.createElement('iframe')
  iframe.style.display = 'none'
  iframe.src = url
  iframe.onload = function() {
    this.parentNode.removeChild(this)
  }
  document.body.appendChild(iframe)
}

export { downloadFile, encodeParams }
