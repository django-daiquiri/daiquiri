import { isEmpty } from 'lodash'
import Cookies from 'js-cookie'

const getLsValue = (path) => {
  const lsValue = localStorage.getItem(`daiquiri.${path}`)

  // check if the value is empty
  if (isEmpty(lsValue)) {
    return null
  } else {
    return JSON.parse(lsValue)
  }
}

const setLsValue = (path, value) => {
  localStorage.setItem(`daiquiri.${path}`, JSON.stringify(value))
}

const checkStoreId = () => {
  const storeId = Cookies.get('storeid')
  const localStoreId = localStorage.getItem('daiquiri.storeid')

  if (isEmpty(localStoreId) || storeId !== localStoreId) {
    localStorage.clear()
    localStorage.setItem('daiquiri.storeid', storeId)
  }
}

export { getLsValue, setLsValue, checkStoreId }
