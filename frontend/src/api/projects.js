import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export const projectApi = {
  list(params) {
    return http.get('/projects', { params })
  },
  getFilterOptions() {
    return http.get('/projects/filter-options')
  },
  getById(id) {
    return http.get(`/projects/${id}`)
  },
}
