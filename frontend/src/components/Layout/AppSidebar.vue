<template>
  <div class="sidebar">
    <div class="sidebar-logo">
      <span class="logo-text">人才画像系统</span>
    </div>
    <nav class="sidebar-nav">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        active-class="nav-item--active"
      >
        <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
const menuItems = [
  { path: '/dashboard', label: '工作台', icon: 'Monitor' },
  { path: '/employees', label: '员工列表', icon: 'User' },
  { path: '/employees/profile', label: '员工画像', icon: 'UserFilled' },
  { path: '/project-requirements', label: '项目需求', icon: 'Document' },
  { path: '/projects', label: '项目列表', icon: 'Grid' },
  { path: '/talent-filter', label: '人才筛选', icon: 'Search' },
  { path: '/ut-dashboard', label: 'UT看板', icon: 'DataAnalysis' },
  { path: '/skill-management', label: '技能管理', icon: 'Tools' },
  { path: '/training-cpe', label: '培训CPE', icon: 'Reading' },
  { path: '/performance', label: '绩效管理', icon: 'Trophy' },
  { path: '/data-analysis', label: '数据分析', icon: 'TrendCharts' },
  { path: '/data-import', label: '数据导入', icon: 'Upload' },
  { path: '/permissions', label: '权限管理', icon: 'Lock' },
]
</script>

<style scoped>
.sidebar {
  width: 220px;
  min-width: 220px;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-logo {
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--border-color);
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--accent-cyan);
  letter-spacing: 0.5px;
}

.sidebar-nav {
  padding: 12px 0;
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 20px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  color: var(--text-primary);
  background-color: var(--bg-hover);
}

.nav-item--active {
  color: var(--accent-cyan) !important;
  background-color: rgba(0, 212, 255, 0.08);
  border-left-color: var(--accent-cyan);
}

.nav-icon {
  font-size: 16px;
  flex-shrink: 0;
}
</style>
