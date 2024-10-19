// take information from the <head> of the django template
export const baseUrl = document.querySelector('meta[name="baseurl"]').content.replace(/\/+$/, '')
export const userId = document.querySelector('meta[name="userid"]').content.replace(/\/+$/, '')
export const isStaff = document.querySelector('meta[name="is_staff"]').content.replace(/\/+$/, '') == 'true'
