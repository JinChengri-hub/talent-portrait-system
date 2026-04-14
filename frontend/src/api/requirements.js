import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

function serializeParams(params) {
  const searchParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (Array.isArray(value)) {
      value.forEach(v => searchParams.append(key, v))
    } else {
      searchParams.append(key, String(value))
    }
  }
  return searchParams.toString()
}

export const requirementApi = {
  list(params) {
    return http.get('/requirements?' + serializeParams(params))
  },
  getFilterOptions() {
    return http.get('/requirements/filter-options')
  },
  remove(id) {
    return http.delete(`/requirements/${id}`)
  },
}
