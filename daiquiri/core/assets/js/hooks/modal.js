import { useRef } from 'react'
import { Modal } from 'bootstrap'
import { isNil } from 'lodash'

export const useModal = () => {
  const ref = useRef()

  const showModal = () => {
    const modal = new Modal(ref.current, {})
    modal.show()
  }

  const hideModal = () => {
    const modal = Modal.getInstance(ref.current)
    if (!isNil(modal)) {
      modal.hide()
    }
  }

  return [ref, showModal, hideModal]
}
