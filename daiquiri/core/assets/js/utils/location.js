// take the baseurl from the <head> of the django template
const baseUrl = document.querySelector('meta[name="baseurl"]').content.replace(/\/+$/, '')

export { baseUrl }
