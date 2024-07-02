// take the baseurl from the <head> of the django template
const baseUrl = document.querySelector('meta[name="baseurl"]').content.replace(/\/+$/, '')
const userId = document.querySelector('meta[name="userid"]').content.replace(/\/+$/, '')

export { baseUrl, userId }
