import { useRef } from 'react'
import { Modal } from 'bootstrap'

export const useModal = () => {
  const ref = useRef()

  const showModal = () => {
    const modal = new Modal(ref.current, {})
    modal.show()
  }

  const hideModal = () => {
    const modal = Modal.getInstance(ref.current)
    modal.hide()
  }

  return [ref, showModal, hideModal]
}
