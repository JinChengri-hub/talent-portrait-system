import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/',
    component: () => import('@/components/Layout/AppLayout.vue'),
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '工作台' } },
      { path: 'employees', name: 'Employees', component: () => import('@/views/Employees.vue'), meta: { title: '员工列表' } },
      { path: 'employees/:id', name: 'EmployeeProfile', component: () => import('@/views/EmployeeProfile.vue'), meta: { title: '员工画像' } },
      { path: 'project-requirements', name: 'ProjectRequirements', component: () => import('@/views/ProjectRequirements.vue'), meta: { title: '项目需求' } },
      { path: 'projects', name: 'Projects', component: () => import('@/views/Projects.vue'), meta: { title: '项目列表' } },
      { path: 'talent-filter', name: 'TalentFilter', component: () => import('@/views/TalentFilter.vue'), meta: { title: '人才筛选' } },
      { path: 'ut-dashboard', name: 'UTDashboard', component: () => import('@/views/UTDashboard.vue'), meta: { title: 'UT看板' } },
      { path: 'skill-management', name: 'SkillManagement', component: () => import('@/views/SkillManagement.vue'), meta: { title: '技能管理' } },
      { path: 'training-cpe', name: 'TrainingCPE', component: () => import('@/views/TrainingCPE.vue'), meta: { title: '培训CPE' } },
      { path: 'performance', name: 'Performance', component: () => import('@/views/Performance.vue'), meta: { title: '绩效管理' } },
      { path: 'data-analysis', name: 'DataAnalysis', component: () => import('@/views/DataAnalysis.vue'), meta: { title: '数据分析' } },
      { path: 'data-import', name: 'DataImport', component: () => import('@/views/DataImport.vue'), meta: { title: '数据导入' } },
      { path: 'permissions', name: 'Permissions', component: () => import('@/views/Permissions.vue'), meta: { title: '权限管理' } },
    ],
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
