import { useState } from 'react'
import { isNil } from 'lodash'

import { getLsValue, setLsValue, checkStoreId } from '../utils/ls'

export const useLsState = (path, initialValue) => {
  checkStoreId()

  // get the value from the local storage
  const lsValue = getLsValue(path)

  // setup the state with the value from the local storage or the provided initialValue
  const [value, setValue] = useState(isNil(lsValue) ? initialValue : lsValue)

  return [value, (value) => {
    setLsValue(path, value)
    setValue(value)
  }]
}
