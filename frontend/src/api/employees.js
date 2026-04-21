import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export const employeeApi = {
  list(params) {
    return http.get('/employees', { params })
  },
  getFilterOptions() {
    return http.get('/employees/filter-options')
  },
  getSkillOptions() {
    return http.get('/employees/skill-options')
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
  uploadAvatar(id, file) {
    const form = new FormData()
    form.append('file', file)
    return http.post(`/employees/${id}/avatar`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  updateSkills(id, skills) {
    return http.put(`/employees/${id}/skills`, skills)
  },
  getProjects(id) {
    return http.get(`/employees/${id}/projects`)
  },
  getTrainings(id) {
    return http.get(`/employees/${id}/trainings`)
  },
  getPerformances(id) {
    return http.get(`/employees/${id}/performances`)
  },
}
