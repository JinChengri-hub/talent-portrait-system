import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export const employeeApi = {
  list(params) {
    return http.get('/employees', { params })
  },
  getFilterOptions() {
    return http.get('/employees/filter-options')
  },
  getById(id) {
    return http.get(`/employees/${id}`)
  },
  create(data) {
    return http.post('/employees', data)
  },
  update(id, data) {
    return http.put(`/employees/${id}`, data)
  },
  exportExcel(params) {
    return http.get('/employees/export', {
      params,
      responseType: 'blob',
    })
  },
  remove(id) {
    return http.delete(`/employees/${id}`)
  },
}
