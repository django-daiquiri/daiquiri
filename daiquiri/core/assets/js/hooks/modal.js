import { useRef } from 'react'
import { Modal } from 'bootstrap'
import { isNil } from 'lodash'

export const useModal = () => {
  const ref = useRef()

  const show = () => {
    const modal = new Modal(ref.current, {})
    modal.show()
  }

  const hide = () => {
    const modal = Modal.getInstance(ref.current)
    if (!isNil(modal)) {
      modal.hide()
    }
  }

  return {ref, show, hide}
}
